// Common typo squatting domains that users accidentally type
export const COMMON_DOMAIN_TYPOS: Record<string, string> = {
  'gmal.com': 'gmail.com',
  'gamil.com': 'gmail.com',
  'gmial.com': 'gmail.com',
  'gmaill.com': 'gmail.com',
  'gmail.co': 'gmail.com',
  'gmail.cm': 'gmail.com',
  'gmai.com': 'gmail.com',
  'hotmial.com': 'hotmail.com',
  'hotmaill.com': 'hotmail.com',
  'yaho.com': 'yahoo.com',
  'yaho.co': 'yahoo.com',
  'yahooo.com': 'yahoo.com',
  'outlok.com': 'outlook.com',
  'outloo.com': 'outlook.com',
};

// Strict email regex matching standard RFC format
export const EMAIL_REGEX = /^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,63}$/;

// Legitimate 2nd-level domains for Bangladesh (.bd)
export const VALID_BD_SECOND_LEVEL = new Set([
  'com.bd',
  'edu.bd',
  'gov.bd',
  'ac.bd',
  'net.bd',
  'org.bd',
  'mil.bd',
]);

export interface EmailValidationResult {
  isValid: boolean;
  error?: string;
  suggestion?: string;
}

export function validateEmail(email: string, language: 'bn' | 'en' = 'bn'): EmailValidationResult {
  if (!email || !email.trim()) {
    return {
      isValid: false,
      error: language === 'bn' ? 'ইমেইল প্রদান করা হয়নি।' : 'Email is required.',
    };
  }

  const clean = email.trim().toLowerCase();

  if (clean.length > 254) {
    return {
      isValid: false,
      error: language === 'bn' ? 'ইমেইলটি অতিরিক্ত দীর্ঘ।' : 'Email is too long.',
    };
  }

  if (!clean.includes('@')) {
    return {
      isValid: false,
      error: language === 'bn' ? "ইমেইলে '@' চিহ্ন অনুপস্থিত।" : "Missing '@' symbol in email.",
    };
  }

  const parts = clean.split('@');
  if (parts.length !== 2) {
    return {
      isValid: false,
      error: language === 'bn' ? 'ইমেইল ফরম্যাট সঠিক নয়।' : 'Invalid email format.',
    };
  }

  const [local, domain] = parts;
  if (!local || !domain) {
    return {
      isValid: false,
      error: language === 'bn' ? 'ইমেইল ফরম্যাট অসম্পূর্ণ।' : 'Incomplete email address.',
    };
  }

  if (local.includes('..') || domain.includes('..')) {
    return {
      isValid: false,
      error: language === 'bn' ? "ইমেইলে পর পর দুটি ডট '..' ব্যবহার করা যাবে না।" : 'Consecutive dots are not allowed.',
    };
  }

  // 1. Check for common typos
  if (COMMON_DOMAIN_TYPOS[domain]) {
    const suggested = COMMON_DOMAIN_TYPOS[domain];
    return {
      isValid: false,
      error:
        language === 'bn'
          ? `অকার্যকর ডোমেন '${domain}'। আপনি কি '${suggested}' বোঝাতে চেয়েছেন?`
          : `Invalid domain '${domain}'. Did you mean '${suggested}'?`,
      suggestion: suggested,
    };
  }

  // 2. Syntax regex check
  if (!EMAIL_REGEX.test(clean)) {
    return {
      isValid: false,
      error:
        language === 'bn'
          ? 'সঠিক ইমেইল ফরম্যাট প্রদান করুন (যেমন: name@gmail.com বা user@seu.edu.bd)।'
          : 'Please enter a valid email format (e.g., name@gmail.com or user@seu.edu.bd).',
    };
  }

  const domainParts = domain.split('.');
  if (domainParts.length < 2) {
    return {
      isValid: false,
      error:
        language === 'bn'
          ? 'ডোমেনে অবশ্যই একটি বৈধ এক্সটেনশন থাকতে হবে (যেমন: .com, .edu.bd)।'
          : 'Domain must have a valid extension (e.g., .com, .edu.bd).',
    };
  }

  // 3. Bangladesh ccTLD structure check: .bd MUST be preceded by .com.bd, .edu.bd, etc.
  if (domain.endsWith('.bd')) {
    const twoLevelSuffix = domainParts.slice(-2).join('.');
    if (!VALID_BD_SECOND_LEVEL.has(twoLevelSuffix)) {
      return {
        isValid: false,
        error:
          language === 'bn'
            ? `বাংলাদেশে সরাসরি '${domain}' ডোমেন গ্রহণযোগ্য নয়। এটি '.com.bd', '.edu.bd' বা '.gov.bd' হতে হবে।`
            : `Direct '${domain}' is invalid in Bangladesh. It must end in '.com.bd', '.edu.bd' or '.gov.bd'.`,
      };
    }
  }

  const tld = domainParts[domainParts.length - 1];
  if (tld.length < 2 || !/^[a-zA-Z]+$/.test(tld)) {
    return {
      isValid: false,
      error:
        language === 'bn'
          ? `ডোমেন এক্সটেনশন '${tld}' বৈধ নয়।`
          : `Domain extension '${tld}' is invalid.`,
    };
  }

  return { isValid: true };
}

export function translateAuthError(error: string | null | undefined, language: 'bn' | 'en'): string {
  if (!error) return '';
  const trimmed = error.trim();

  // 1. DNS non-existent domain check
  const dnsMatch = trimmed.match(/(?:Domain '([^']+)' does not exist on the internet|ডোমেন '([^']+)' ইন্টারনেটে বিদ্যমান নয়)/i);
  if (dnsMatch) {
    const domain = dnsMatch[1] || dnsMatch[2];
    return language === 'bn'
      ? `ডোমেন '${domain}' ইন্টারনেটে বিদ্যমান নয় বা এর কোনো সক্রিয় ডিএনএস (DNS) নেই। অনুগ্রহ করে একটি আসল ইমেইল প্রদান করুন।`
      : `Domain '${domain}' does not exist on the internet or has no active DNS. Please provide a real email address.`;
  }

  // 2. BD direct domain check
  const bdMatch = trimmed.match(/(?:Direct '([^']+)' is invalid in Bangladesh|বাংলাদেশে সরাসরি '([^']+)' ডোমেন গ্রহণযোগ্য নয়)/i);
  if (bdMatch) {
    const domain = bdMatch[1] || bdMatch[2];
    return language === 'bn'
      ? `বাংলাদেশে সরাসরি '${domain}' ডোমেন গ্রহণযোগ্য নয়। এটি '.com.bd', '.edu.bd' বা '.gov.bd' হতে হবে।`
      : `Direct '${domain}' is invalid in Bangladesh. It must end with '.com.bd', '.edu.bd', or '.gov.bd'.`;
  }

  // 3. Typo check
  const typoMatch = trimmed.match(/(?:Invalid domain '([^']+)'. Did you mean '([^']+)'\?|অকার্যকর বা ভুল ডোমেন '([^']+)'। আপনি কি '([^']+)' বোঝাতে চেয়েছেন\?)/i);
  if (typoMatch) {
    const domain = typoMatch[1] || typoMatch[3];
    const suggested = typoMatch[2] || typoMatch[4];
    return language === 'bn'
      ? `অকার্যকর ডোমেন '${domain}'। আপনি কি '${suggested}' বোঝাতে চেয়েছেন?`
      : `Invalid domain '${domain}'. Did you mean '${suggested}'?`;
  }

  // 4. Missing @
  if (trimmed.includes("Missing '@'") || trimmed.includes("চিহ্ন অনুপস্থিত")) {
    return language === 'bn' ? "ইমেইলে '@' চিহ্ন অনুপস্থিত।" : "Missing '@' symbol in email.";
  }

  // 5. User/password invalid
  if (trimmed.includes("Invalid username or password") || trimmed.includes("ইউজারনেম এবং পাসওয়ার্ড") || trimmed.includes("ইউজারনেম অথবা পাসওয়ার্ড")) {
    return language === 'bn' ? "ইউজারনেম এবং পাসওয়ার্ড সঠিক নয়।" : "Invalid username or password.";
  }

  // 6. Username or email already registered
  if (trimmed.includes("Username or email already registered") || trimmed.includes("ইতিমধ্যে নিবন্ধিত")) {
    return language === 'bn' ? "ইউজারনেম অথবা ইমেইলটি ইতিমধ্যে নিবন্ধিত রয়েছে।" : "Username or email already registered.";
  }

  // 7. Passwords do not match
  if (trimmed.includes("Passwords do not match") || trimmed.includes("পাসওয়ার্ড দুটি মেলেনি")) {
    return language === 'bn' ? "পাসওয়ার্ড দুটি মেলেনি।" : "Passwords do not match.";
  }

  // 8. Too many requests / banned
  if (trimmed.includes("Too many requests") || trimmed.includes("অতিরিক্ত রিকোয়েস্ট")) {
    return language === 'bn' ? "অতিরিক্ত রিকোয়েস্ট পাঠানো হয়েছে। অনুগ্রহ করে কিছুক্ষণ অপেক্ষা করুন।" : "Too many requests. Please wait a moment before trying again.";
  }
  if (trimmed.includes("IP banned") || trimmed.includes("সাময়িক নিষিদ্ধ")) {
    return language === 'bn' ? "বারংবার সীমা লঙ্ঘনের কারণে আপনার আইপি ১৫ মিনিটের জন্য সাময়িক নিষিদ্ধ করা হয়েছে।" : "Your IP has been temporarily banned for 15 minutes due to repeated security violations.";
  }

  return trimmed;
}
