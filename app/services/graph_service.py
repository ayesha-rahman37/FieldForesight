"""
Neo4j Graph Database Service: Agricultural Knowledge Graph & Multi-Hop Query Engine
Provides:
  1. Connection lifecycle and health check for Neo4j Bolt driver
  2. Agricultural Ontology Seeding (Crops, Varieties, Pests/Diseases, Symptoms, Safe Treatments, Agro-zones)
  3. GraphRAG query methods for LangGraph Agent
"""

import os
import logging
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from neo4j import GraphDatabase, Driver

logger = logging.getLogger("fieldforesight.graph")

load_dotenv(override=True)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "fieldforesight123")

_driver: Optional[Driver] = None


def get_graph_driver() -> Driver:
    """Singleton getter for Neo4j driver with auto-reconnect."""
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
            max_connection_lifetime=3600,
        )
    return _driver


def close_graph_driver() -> None:
    """Closes driver pool on application shutdown."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


def check_graph_connection() -> Dict[str, Any]:
    """Tests connection to Neo4j database and returns basic status."""
    try:
        driver = get_graph_driver()
        with driver.session() as session:
            result = session.run("RETURN 1 AS connected, datetime() AS server_time")
            record = result.single()
            if record:
                return {
                    "status": "connected",
                    "uri": NEO4J_URI,
                    "server_time": str(record["server_time"]),
                }
    except Exception as exc:
        logger.error(f"Neo4j connection error: {exc}")
        return {"status": "error", "error": str(exc), "uri": NEO4J_URI}
    return {"status": "error", "error": "Unknown connection state"}


def seed_agricultural_knowledge_graph() -> Dict[str, int]:
    """
    Populates Neo4j with the official Bangladesh Agricultural Ontology:
    - Crops (ধান, গম, আলু, ভুট্টা, সরিষা, পাট, মসুর)
    - Varieties with growth duration and resistance profiles
    - Pests & Diseases (ব্লাস্ট, বাদামি গাছফড়িং, মাজরা, নাবি ধসা, জাবপোকা)
    - Field Symptoms
    - Certified IPM & Safe Chemical Treatments
    - Agro-Ecological Zones & Key Districts
    """
    driver = get_graph_driver()
    stats = {"nodes_created": 0, "relationships_created": 0}

    cypher_statements = [
        # --- 1. Unique Constraints ---
        "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Crop) REQUIRE c.name IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (v:Variety) REQUIRE v.name IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (p:PestDisease) REQUIRE p.name IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Symptom) REQUIRE s.name IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Treatment) REQUIRE t.name IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (d:District) REQUIRE d.name IS UNIQUE;",

        # --- 2. Seed Crops ---
        """
        MERGE (c1:Crop {name: 'Rice', bangla_name: 'ধান', category: 'cereal'})
        MERGE (c2:Crop {name: 'Potato', bangla_name: 'আলু', category: 'tuber'})
        MERGE (c3:Crop {name: 'Wheat', bangla_name: 'গম', category: 'cereal'})
        MERGE (c4:Crop {name: 'Mustard', bangla_name: 'সরিষা', category: 'oilseed'})
        MERGE (c5:Crop {name: 'Maize', bangla_name: 'ভুট্টা', category: 'cereal'})
        MERGE (c6:Crop {name: 'Jute', bangla_name: 'পাট', category: 'fiber'})
        MERGE (c7:Crop {name: 'Lentil', bangla_name: 'মসুর', category: 'pulse'})
        """,

        # --- 3. Seed Varieties & Link to Crops ---
        """
        MATCH (rice:Crop {name: 'Rice'})
        MERGE (v1:Variety {name: 'BRRI Dhan 28', bangla_name: 'ব্রি ধান ২৮', season: 'Boro', duration_days: 140, yield_tha: 5.5})
        MERGE (v2:Variety {name: 'BRRI Dhan 29', bangla_name: 'ব্রি ধান ২৯', season: 'Boro', duration_days: 160, yield_tha: 7.2})
        MERGE (v3:Variety {name: 'BRRI Dhan 89', bangla_name: 'ব্রি ধান ৮৯', season: 'Boro', duration_days: 155, yield_tha: 8.0})
        MERGE (v4:Variety {name: 'BRRI Dhan 56', bangla_name: 'ব্রি ধান ৫৬', season: 'Aman', duration_days: 110, drought_tolerant: true})
        MERGE (rice)-[:HAS_VARIETY]->(v1)
        MERGE (rice)-[:HAS_VARIETY]->(v2)
        MERGE (rice)-[:HAS_VARIETY]->(v3)
        MERGE (rice)-[:HAS_VARIETY]->(v4)
        """,
        """
        MATCH (potato:Crop {name: 'Potato'})
        MERGE (v5:Variety {name: 'BARI Alu 7 (Diamant)', bangla_name: 'ডায়মন্ট আলু', season: 'Rabi', duration_days: 90, yield_tha: 25.0})
        MERGE (v6:Variety {name: 'BARI Alu 8 (Cardinal)', bangla_name: 'কার্ডিনাল আলু', season: 'Rabi', duration_days: 95, yield_tha: 24.5})
        MERGE (potato)-[:HAS_VARIETY]->(v5)
        MERGE (potato)-[:HAS_VARIETY]->(v6)
        """,
        """
        MATCH (wheat:Crop {name: 'Wheat'})
        MERGE (v7:Variety {name: 'BARI Gom 25', bangla_name: 'বারি গম ২৫', season: 'Rabi', heat_tolerant: true, yield_tha: 4.2})
        MERGE (v8:Variety {name: 'BARI Gom 30', bangla_name: 'বারি গম ৩০', season: 'Rabi', blast_resistant: true, yield_tha: 4.5})
        MERGE (wheat)-[:HAS_VARIETY]->(v7)
        MERGE (wheat)-[:HAS_VARIETY]->(v8)
        """,
        """
        MATCH (mustard:Crop {name: 'Mustard'})
        MERGE (v9:Variety {name: 'BARI Sarisha 14', bangla_name: 'বারি সরিষা ১৪', season: 'Rabi', duration_days: 78, yield_tha: 1.5})
        MERGE (mustard)-[:HAS_VARIETY]->(v9)
        """,

        # --- 4. Seed Pests & Diseases ---
        """
        MERGE (p1:PestDisease {name: 'Rice Blast', bangla_name: 'ধানের ব্লাস্ট রোগ', type: 'fungal', severity: 'high', causal_agent: 'Magnaporthe oryzae'})
        MERGE (p2:PestDisease {name: 'Brown Planthopper (BPH)', bangla_name: 'বাদামি গাছফড়িং (কারেন্ট পোকা)', type: 'insect_pest', severity: 'critical', causal_agent: 'Nilaparvata lugens'})
        MERGE (p3:PestDisease {name: 'Yellow Stem Borer', bangla_name: 'হলুদ মাজরা পোকা', type: 'insect_pest', severity: 'high', causal_agent: 'Scirpophaga incertulas'})
        MERGE (p4:PestDisease {name: 'Potato Late Blight', bangla_name: 'আলুর নাবি ধসা রোগ', type: 'fungal', severity: 'critical', causal_agent: 'Phytophthora infestans'})
        MERGE (p5:PestDisease {name: 'Mustard Aphid', bangla_name: 'সরিষার জাবপোকা', type: 'insect_pest', severity: 'medium', causal_agent: 'Lipaphis erysimi'})
        MERGE (p6:PestDisease {name: 'Wheat Blast', bangla_name: 'গমের ব্লাস্ট রোগ', type: 'fungal', severity: 'critical', causal_agent: 'Magnaporthe oryzae Triticum'})
        """,

        # --- 5. Link Crops & Susceptibilities ---
        """
        MATCH (rice:Crop {name: 'Rice'}), (blast:PestDisease {name: 'Rice Blast'}), (bph:PestDisease {name: 'Brown Planthopper (BPH)'}), (borer:PestDisease {name: 'Yellow Stem Borer'})
        MERGE (rice)-[:AFFECTED_BY]->(blast)
        MERGE (rice)-[:AFFECTED_BY]->(bph)
        MERGE (rice)-[:AFFECTED_BY]->(borer)
        """,
        """
        MATCH (v1:Variety {name: 'BRRI Dhan 28'}), (blast:PestDisease {name: 'Rice Blast'})
        MERGE (v1)-[:SUSCEPTIBLE_TO {risk_stage: 'Neck Blast at panicle emergence'}]->(blast)
        """,
        """
        MATCH (potato:Crop {name: 'Potato'}), (lblight:PestDisease {name: 'Potato Late Blight'})
        MERGE (potato)-[:AFFECTED_BY]->(lblight)
        """,
        """
        MATCH (mustard:Crop {name: 'Mustard'}), (aphid:PestDisease {name: 'Mustard Aphid'})
        MERGE (mustard)-[:AFFECTED_BY]->(aphid)
        """,
        """
        MATCH (wheat:Crop {name: 'Wheat'}), (wblast:PestDisease {name: 'Wheat Blast'})
        MERGE (wheat)-[:AFFECTED_BY]->(wblast)
        """,

        # --- 6. Seed Symptoms ---
        """
        MERGE (s1:Symptom {name: 'Spindle-shaped eye spots', bangla_name: 'চোখের আকৃতির ধূসর কেন্দ্রযুক্ত দাগ', stage: 'Tillering/Booting'})
        MERGE (s2:Symptom {name: 'Black rotting neck node', bangla_name: 'শীষের গোড়ায় কালো পচন ও শীষ ভেঙে পড়া', stage: 'Heading/Flowering'})
        MERGE (s3:Symptom {name: 'Hopper burn circular drying', bangla_name: 'ক্ষেতের মাঝখানে বৃত্তাকারে গাছ পুড়ে শুকিয়ে যাওয়া', stage: 'Milking/Ripening'})
        MERGE (s4:Symptom {name: 'Dead Heart (dead central shoot)', bangla_name: 'কুশি অবস্থায় মাঝের ডগা শুকিয়ে যাওয়া (মৃত ডগা)', stage: 'Vegetative'})
        MERGE (s5:Symptom {name: 'White Head (chaffy white earhead)', bangla_name: 'শীষ আসার পর সাদা চিটা শীষ খাড়া হয়ে থাকা', stage: 'Heading'})
        MERGE (s6:Symptom {name: 'Water-soaked dark lesions with white mold', bangla_name: 'পাতার কিনারে বাদামি ভেজা দাগ ও কুয়াশায় নিচে সাদা ছাতা', stage: 'Cold/Foggy Rabi'})
        MERGE (s7:Symptom {name: 'Black sooty mold and honey dew on inflorescence', bangla_name: 'ফুল ও ফলে চিটচিটে রস ও কালো ঝুল পড়া', stage: 'Flowering/Siliqua'})
        """,

        # --- 6b. Link Symptoms to Diseases ---
        """
        MATCH (blast:PestDisease {name: 'Rice Blast'}), (s1:Symptom {name: 'Spindle-shaped eye spots'}), (s2:Symptom {name: 'Black rotting neck node'})
        MERGE (blast)-[:EXHIBITS_SYMPTOM]->(s1)
        MERGE (blast)-[:EXHIBITS_SYMPTOM]->(s2)
        """,
        """
        MATCH (bph:PestDisease {name: 'Brown Planthopper (BPH)'}), (s3:Symptom {name: 'Hopper burn circular drying'})
        MERGE (bph)-[:EXHIBITS_SYMPTOM]->(s3)
        """,
        """
        MATCH (borer:PestDisease {name: 'Yellow Stem Borer'}), (s4:Symptom {name: 'Dead Heart (dead central shoot)'}), (s5:Symptom {name: 'White Head (chaffy white earhead)'})
        MERGE (borer)-[:EXHIBITS_SYMPTOM]->(s4)
        MERGE (borer)-[:EXHIBITS_SYMPTOM]->(s5)
        """,
        """
        MATCH (lblight:PestDisease {name: 'Potato Late Blight'}), (s6:Symptom {name: 'Water-soaked dark lesions with white mold'})
        MERGE (lblight)-[:EXHIBITS_SYMPTOM]->(s6)
        """,
        """
        MATCH (aphid:PestDisease {name: 'Mustard Aphid'}), (s7:Symptom {name: 'Black sooty mold and honey dew on inflorescence'})
        MERGE (aphid)-[:EXHIBITS_SYMPTOM]->(s7)
        """,

        # --- 7. Seed Treatments ---
        """
        MERGE (t1:Treatment {
            name: 'Rice Blast Certified Management',
            bangla_name: 'ধানের ব্লাস্ট সমন্বিত দমন',
            cultural_practice: 'জমির পানি শুকাতে না দেওয়া, অতিরিক্ত ইউরিয়া বন্ধ রাখা এবং বিঘা প্রতি ৫ কেজি পটাশ সার উপরিপ্রয়োগ।',
            biological_control: 'ট্রাইকোডার্মা বায়ো-ফাংগিসাইড বীজ শোধন।',
            chemical_rule: 'তীব্র আক্রমণে ট্রাইসাইক্লাজল (যেমন ট্রুপার/দিফা) অথবা নেটিভো অনুমোদিত মাত্রায় বিকেলে স্প্রে করুন।',
            withholding_period_days: 14,
            safety_warning: 'কীটনাশক বা ছত্রাকনাশক ব্যবহারের আগে স্থানীয় উপ-সহকারী কৃষি কর্মকর্তা (SAAO) বা ১৬১২৩ নম্বরে পরামর্শ নিন।'
        })
        MERGE (t2:Treatment {
            name: 'BPH Ecological & Chemical Control',
            bangla_name: 'কারেন্ট পোকা (বিপিএইচ) নিয়ন্ত্রণ',
            cultural_practice: 'জমির পানি সরিয়ে দেওয়া (AWD), বিলি কেটে আলো-বাতাস প্রবেশের ব্যবস্থা করা।',
            biological_control: 'উপকারী মাকড়সা ও মিরিড বাগ সংরক্ষণ, আলোক ফাঁদ ব্যবহার।',
            chemical_rule: 'গাছের গোড়ায় পাইমেট্রোজিন (যেমন প্যাক্সার) বা ডিনেটোফুরান স্প্রে করুন।',
            withholding_period_days: 21,
            safety_warning: 'পাইরেথ্রয়েড জাতীয় কীটনাশক স্প্রে করবেন না—এতে পোকা দ্রুত বংশবৃদ্ধি করে (Resurgence)।'
        })
        MERGE (t3:Treatment {
            name: 'Stem Borer Perching & IPM',
            bangla_name: 'মাজরা পোকার পার্চিং ও জৈব দমন',
            cultural_practice: 'ক্ষেতে বিঘা প্রতি ৮-১০টি বাঁশের কঞ্চি পোঁতা (পার্চিং) যাতে পাখি বসে পোকা খায়।',
            biological_control: 'ট্রাইকোগ্রামা ও ব্রাকন বোলতা জৈব পরজীবী অবমুক্তকরণ।',
            chemical_rule: 'কুশি শুকিয়ে যাওয়া ১০% ছাড়ালে কার্বোফিউরান অনুমোদিত মাত্রায় ব্যবহার করা যেতে পারে।',
            withholding_period_days: 28,
            safety_warning: 'মাছ বা জলজ প্রাণীর ক্ষতি এড়াতে প্লাবন এলাকা ও বর্ষায় দানাদার কীটনাশক পরিহার করুন।'
        })
        MERGE (t4:Treatment {
            name: 'Potato Late Blight Preventative Action',
            bangla_name: 'আলুর নাবি ধসার আগাম সতর্কতা',
            cultural_practice: 'ঘন কুয়াশা ও মেঘলা আবহাওয়ায় সেচ বন্ধ রাখা, আক্রান্ত গাছ তুলে ধ্বংস করা।',
            biological_control: 'সুস্থ ও প্রত্যয়িত রোগমুক্ত বীজ আলু বপন।',
            chemical_rule: 'কুয়াশার আগে ম্যানকোজেব আগাম স্প্রে; রোগ দেখা দিলে ডাইমিথোমর্ফ বা এক্রোব্যাট এম জেড প্রয়োগ।',
            withholding_period_days: 14,
            safety_warning: 'টানা ২ বারের বেশি একই গ্রুপের ছত্রাকনাশক ব্যবহার করবেন না যাতে ছত্রাক প্রতিরোধী না হয়।'
        })
        """,

        # --- 7b. Link Treatments to Diseases ---
        """
        MATCH (blast:PestDisease {name: 'Rice Blast'}), (t1:Treatment {name: 'Rice Blast Certified Management'})
        MERGE (blast)-[:MANAGED_BY]->(t1)
        """,
        """
        MATCH (bph:PestDisease {name: 'Brown Planthopper (BPH)'}), (t2:Treatment {name: 'BPH Ecological & Chemical Control'})
        MERGE (bph)-[:MANAGED_BY]->(t2)
        """,
        """
        MATCH (borer:PestDisease {name: 'Yellow Stem Borer'}), (t3:Treatment {name: 'Stem Borer Perching & IPM'})
        MERGE (borer)-[:MANAGED_BY]->(t3)
        """,
        """
        MATCH (lblight:PestDisease {name: 'Potato Late Blight'}), (t4:Treatment {name: 'Potato Late Blight Preventative Action'})
        MERGE (lblight)-[:MANAGED_BY]->(t4)
        """,

        # --- 8. Seed Districts & Link to Crops ---
        """
        MERGE (d1:District {name: 'Rangpur', bangla_name: 'রংপুর', division: 'Rangpur', zone: 'Tista Meander Floodplain (AEZ-3)'})
        MERGE (d2:District {name: 'Bogura', bangla_name: 'বগুড়া', division: 'Rajshahi', zone: 'Level Barind Tract (AEZ-25)'})
        MERGE (d3:District {name: 'Dinajpur', bangla_name: 'দিনাজপুর', division: 'Rangpur', zone: 'Old Himalayan Piedmont Plain (AEZ-1)'})
        MERGE (d4:District {name: 'Munshiganj', bangla_name: 'মুন্সীগঞ্জ', division: 'Dhaka', zone: 'Active Ganges Floodplain (AEZ-10)'})
        MERGE (d5:District {name: 'Rajshahi', bangla_name: 'রাজশাহী', division: 'Rajshahi', zone: 'High Barind Tract (AEZ-26)'})
        MERGE (d6:District {name: 'Tangail', bangla_name: 'টাঙ্গাইল', division: 'Dhaka', zone: 'Young Brahmaputra Floodplain (AEZ-8)'})
        """,
        """
        MATCH (rice:Crop {name: 'Rice'}), (d1:District {name: 'Rangpur'}), (d2:District {name: 'Bogura'}), (d3:District {name: 'Dinajpur'})
        MERGE (rice)-[:THRIVES_IN]->(d1)
        MERGE (rice)-[:THRIVES_IN]->(d2)
        MERGE (rice)-[:THRIVES_IN]->(d3)
        """,
        """
        MATCH (potato:Crop {name: 'Potato'}), (d1:District {name: 'Rangpur'}), (d2:District {name: 'Bogura'}), (d4:District {name: 'Munshiganj'})
        MERGE (potato)-[:THRIVES_IN]->(d1)
        MERGE (potato)-[:THRIVES_IN]->(d2)
        MERGE (potato)-[:THRIVES_IN]->(d4)
        """
    ]

    with driver.session() as session:
        for stmt in cypher_statements:
            clean_stmt = stmt.strip()
            if not clean_stmt:
                continue
            res = session.run(clean_stmt)
            summary = res.consume()
            stats["nodes_created"] += summary.counters.nodes_created
            stats["relationships_created"] += summary.counters.relationships_created

    logger.info(f"Seeded Agricultural Knowledge Graph: {stats}")
    return stats


# --- Graph Multi-Hop Query Functions for LangGraph Agent ---

def query_crop_disease_graph(crop_name: str) -> List[Dict[str, Any]]:
    """
    Multi-hop Cypher traversal:
    Given a Crop (e.g., 'Rice' or 'Potato'), retrieves:
    - Associated Pests/Diseases
    - Field Symptoms
    - Certified Management Protocols & Safety Warnings
    """
    cypher = """
    MATCH (c:Crop)
    WHERE c.name =~ ('(?i)' + $crop_name) OR c.bangla_name =~ ('(?i)' + $crop_name)
    MATCH (c)-[:AFFECTED_BY]->(p:PestDisease)
    OPTIONAL MATCH (p)-[:EXHIBITS_SYMPTOM]->(s:Symptom)
    OPTIONAL MATCH (p)-[:MANAGED_BY]->(t:Treatment)
    RETURN
        c.name AS crop,
        c.bangla_name AS crop_bn,
        p.name AS pest_disease,
        p.bangla_name AS pest_disease_bn,
        p.severity AS severity,
        collect(DISTINCT s.bangla_name) AS symptoms_bn,
        t.bangla_name AS treatment_plan,
        t.cultural_practice AS cultural_practice,
        t.chemical_rule AS chemical_rule,
        t.safety_warning AS safety_warning
    LIMIT 6
    """
    driver = get_graph_driver()
    results = []
    with driver.session() as session:
        records = session.run(cypher, crop_name=crop_name.strip())
        for rec in records:
            results.append({
                "crop": rec["crop"],
                "crop_bn": rec["crop_bn"],
                "pest_disease": rec["pest_disease"],
                "pest_disease_bn": rec["pest_disease_bn"],
                "severity": rec["severity"],
                "symptoms_bn": rec["symptoms_bn"],
                "treatment_plan": rec["treatment_plan"],
                "cultural_practice": rec["cultural_practice"],
                "chemical_rule": rec["chemical_rule"],
                "safety_warning": rec["safety_warning"],
            })
    return results


def find_disease_by_symptom(symptom_keyword: str) -> List[Dict[str, Any]]:
    """
    Reverse Graph Traversal:
    Given a visual symptom described by the farmer (e.g. 'সাদা শীষ', 'চোখের দাগ', 'পুড়ে যাওয়া'),
    identifies the exact disease, affecting crop, and safe treatment.
    """
    cypher = """
    MATCH (s:Symptom)
    WHERE s.bangla_name CONTAINS $keyword OR toLower(s.name) CONTAINS toLower($keyword)
    MATCH (p:PestDisease)-[:EXHIBITS_SYMPTOM]->(s)
    MATCH (c:Crop)-[:AFFECTED_BY]->(p)
    OPTIONAL MATCH (p)-[:MANAGED_BY]->(t:Treatment)
    RETURN
        c.name AS crop,
        c.bangla_name AS crop_bn,
        p.name AS disease,
        p.bangla_name AS disease_bn,
        s.bangla_name AS matched_symptom,
        t.cultural_practice AS cultural_action,
        t.chemical_rule AS certified_chemical,
        t.safety_warning AS safety_warning
    LIMIT 4
    """
    driver = get_graph_driver()
    results = []
    with driver.session() as session:
        records = session.run(cypher, keyword=symptom_keyword.strip())
        for rec in records:
            results.append({
                "crop": rec["crop"],
                "crop_bn": rec["crop_bn"],
                "disease": rec["disease"],
                "disease_bn": rec["disease_bn"],
                "symptom": rec["matched_symptom"],
                "cultural_action": rec["cultural_action"],
                "certified_chemical": rec["certified_chemical"],
                "safety_warning": rec["safety_warning"],
            })
    return results


def query_variety_recommendation(crop_name: str, district_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Multi-hop Traversal:
    Retrieves approved varieties for a crop, along with resistance and suitability.
    """
    cypher = """
    MATCH (c:Crop)
    WHERE c.name =~ ('(?i)' + $crop_name) OR c.bangla_name =~ ('(?i)' + $crop_name)
    MATCH (c)-[:HAS_VARIETY]->(v:Variety)
    OPTIONAL MATCH (v)-[s:SUSCEPTIBLE_TO]->(p:PestDisease)
    RETURN
        c.name AS crop,
        v.name AS variety,
        v.bangla_name AS variety_bn,
        v.season AS season,
        v.duration_days AS duration_days,
        v.yield_tha AS potential_yield,
        collect(DISTINCT p.bangla_name) AS susceptibilities
    LIMIT 6
    """
    driver = get_graph_driver()
    results = []
    with driver.session() as session:
        records = session.run(cypher, crop_name=crop_name.strip())
        for rec in records:
            results.append({
                "crop": rec["crop"],
                "variety": rec["variety"],
                "variety_bn": rec["variety_bn"],
                "season": rec["season"],
                "duration_days": rec["duration_days"],
                "potential_yield": rec["potential_yield"],
                "susceptibilities": rec["susceptibilities"],
            })
    return results
