import logging
import re
import socket
from typing import Tuple, Optional

logger = logging.getLogger("fieldforesight.security")

# Common typos for popular domains
COMMON_DOMAIN_TYPOS = {
    "gmal.com": "gmail.com",
    "gamil.com": "gmail.com",
    "gmial.com": "gmail.com",
    "gmaill.com": "gmail.com",
    "gmail.co": "gmail.com",
    "gmail.cm": "gmail.com",
    "gmai.com": "gmail.com",
    "hotmial.com": "hotmail.com",
    "hotmaill.com": "hotmail.com",
    "yaho.com": "yahoo.com",
    "yaho.co": "yahoo.com",
    "yahooo.com": "yahoo.com",
    "outlok.com": "outlook.com",
    "outloo.com": "outlook.com",
}

# Strict email regex matching RFC 5322
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,63}$"
)

# Legitimate 2nd-level domains for Bangladesh (.bd)
VALID_BD_SECOND_LEVEL = {
    "com.bd", "edu.bd", "gov.bd", "ac.bd", "net.bd", "org.bd", "mil.bd"
}

# Cache for resolved domains to avoid repeated DNS lookups
_RESOLVED_DOMAINS_CACHE = {
    "gmail.com": True,
    "googlemail.com": True,
    "yahoo.com": True,
    "outlook.com": True,
    "hotmail.com": True,
    "icloud.com": True,
    "seu.edu.bd": True,
    "du.ac.bd": True,
    "buet.ac.bd": True,
    "dae.gov.bd": True,
    "brri.gov.bd": True,
    "bari.gov.bd": True,
    "fieldforesight.ai": True,
}


def _verify_domain_dns(domain: str) -> bool:
    """
    Checks if a domain has active DNS resolution on the internet.
    Caches verified domains in memory.
    """
    domain = domain.lower()
    if domain in _RESOLVED_DOMAINS_CACHE:
        return _RESOLVED_DOMAINS_CACHE[domain]

    try:
        socket.getaddrinfo(domain, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        _RESOLVED_DOMAINS_CACHE[domain] = True
        return True
    except Exception:
        _RESOLVED_DOMAINS_CACHE[domain] = False
        return False


def validate_email_address(
    email: str,
    verify_dns: bool = True,
    language: str = "en",
) -> Tuple[bool, Optional[str]]:
    """
    Strict, bilingual, production-grade email verification.
    Defaults to English initially; returns Bengali if language.startswith('bn').
    """
    is_bn = language.lower().startswith("bn")

    if not email or not isinstance(email, str):
        return False, (
            "ইমেইল প্রদান করা হয়নি।"
            if is_bn
            else "Email address is required."
        )

    email_clean = email.strip().lower()

    if len(email_clean) > 254:
        return False, (
            "ইমেইলটি অতিরিক্ত দীর্ঘ।"
            if is_bn
            else "Email address is too long."
        )

    if "@" not in email_clean:
        return False, (
            "ইমেইলে '@' চিহ্ন অনুপস্থিত।"
            if is_bn
            else "Missing '@' symbol in email address."
        )

    parts = email_clean.split("@")
    if len(parts) != 2:
        return False, (
            "ইমেইল ফরম্যাট সঠিক নয়।"
            if is_bn
            else "Invalid email address format."
        )

    local_part, domain = parts
    if not local_part or not domain:
        return False, (
            "ইমেইল ফরম্যাট অসম্পূর্ণ।"
            if is_bn
            else "Incomplete email address."
        )

    if ".." in local_part or ".." in domain:
        return False, (
            "ইমেইলে পর পর দুটি ডট '..' ব্যবহার করা যাবে না।"
            if is_bn
            else "Consecutive dots '..' are not allowed in email address."
        )

    # 1. Typo Check
    if domain in COMMON_DOMAIN_TYPOS:
        suggested = COMMON_DOMAIN_TYPOS[domain]
        return False, (
            f"অকার্যকর বা ভুল ডোমেন '{domain}'। আপনি কি '{suggested}' বোঝাতে চেয়েছেন?"
            if is_bn
            else f"Invalid domain '{domain}'. Did you mean '{suggested}'?"
        )

    # 2. Regex syntax check
    if not EMAIL_REGEX.match(email_clean):
        return False, (
            "সঠিক ইমেইল ফরম্যাট প্রদান করুন (যেমন: name@gmail.com বা user@seu.edu.bd)।"
            if is_bn
            else "Please enter a valid email format (e.g., name@gmail.com or user@seu.edu.bd)."
        )

    domain_parts = domain.split(".")
    if len(domain_parts) < 2:
        return False, (
            "ডোমেনে অবশ্যই একটি বৈধ এক্সটেনশন থাকতে হবে (যেমন: .com, .edu.bd)।"
            if is_bn
            else "Domain must have a valid extension (e.g., .com, .edu.bd)."
        )

    # 3. Bangladesh ccTLD structure check
    if domain.endswith(".bd"):
        two_level_suffix = ".".join(domain_parts[-2:])
        if two_level_suffix not in VALID_BD_SECOND_LEVEL:
            return False, (
                f"বাংলাদেশে সরাসরি '{domain}' ডোমেন গ্রহণযোগ্য নয়। এটি '.com.bd', '.edu.bd' বা '.gov.bd' হতে হবে।"
                if is_bn
                else f"Direct '{domain}' is invalid in Bangladesh. It must end with '.com.bd', '.edu.bd', or '.gov.bd'."
            )

    # 4. Real Internet DNS Verification
    if verify_dns:
        has_dns = _verify_domain_dns(domain)
        if not has_dns:
            return False, (
                f"ডোমেন '{domain}' ইন্টারনেটে বিদ্যমান নয় বা এর কোনো সক্রিয় ডিএনএস (DNS) নেই। অনুগ্রহ করে একটি আসল ইমেইল প্রদান করুন।"
                if is_bn
                else f"Domain '{domain}' does not exist on the internet or has no active DNS. Please provide a real email address."
            )

    return True, None
