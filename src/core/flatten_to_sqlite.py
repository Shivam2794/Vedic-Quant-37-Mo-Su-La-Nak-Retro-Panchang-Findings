"""
Phase 0 / Step 0.2a: Flatten LightRAG Graphs → SQLite
=====================================================
Reads both nadi_sutras_memory and jaimini_memory LightRAG stores.
Extracts all entities (with descriptions + embeddings) and relations.
Performs rough automatic classification into astrological categories.
Stores everything in a single queryable SQLite database.

Output: vedic_knowledge.db (~50MB)
"""
import json
import os
import re
import sqlite3
import base64
from datetime import datetime

# ─── Paths ───
BASE = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\d3e7ccf9-35e0-46db-bcc3-2a44cc32acd1\scratch\vedic_graphs"
DB_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\vedic_knowledge.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ─── Keyword Sets for Auto-Classification ───
PLANETS = {
    "sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn",
    "rahu", "ketu", "uranus", "neptune", "pluto",
    "surya", "chandra", "mangal", "budha", "guru", "shukra", "shani",
    "brihaspati", "sani", "sukra", "budh", "ravi"
}
SIGNS = {
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
    "mesha", "vrishabha", "mithuna", "karka", "simha", "kanya",
    "tula", "vrischika", "dhanu", "makara", "kumbha", "meena"
}
HOUSES_RE = re.compile(r'\b(\d{1,2})(st|nd|rd|th)\s*(house|bhava)\b', re.IGNORECASE)
HOUSE_WORDS = {"house", "bhava", "lagna", "ascendant"}
CONJUNCTION_WORDS = {"conjunct", "conjunction", "conjoined", "together", "combine"}
ASPECT_WORDS = {"aspect", "trine", "square", "sextile", "opposition", "drishti", "dristi"}
DASHA_WORDS = {"dasha", "mahadasha", "antardasha", "bhukti", "pratyantar", "vimshottari", "chara dasha"}
YOGA_WORDS = {"yoga", "rajayoga", "raj yoga", "dhan yoga", "pancha mahapurusha"}
NAKSHATRA_WORDS = {"nakshatra", "ashwini", "bharani", "krittika", "rohini", "mrigashira",
                    "ardra", "punarvasu", "pushya", "ashlesha", "magha", "purva phalguni",
                    "uttara phalguni", "hasta", "chitra", "swati", "vishakha", "anuradha",
                    "jyeshtha", "moola", "purva ashadha", "uttara ashadha", "shravana",
                    "dhanishta", "shatabhisha", "purva bhadrapada", "uttara bhadrapada", "revati"}
ASHTAKAVARGA_WORDS = {"ashtakavarga", "bindu", "rekha", "sarvashtakavarga", "prastar"}
DIVISIONAL_RE = re.compile(r'\b[dD](\d{1,2})\b|navamsha|dashamsha|drekkana|hora chart', re.IGNORECASE)
KP_WORDS = {"sub-lord", "sublord", "star lord", "kp", "krishnamurti", "cuspal", "significator"}
JAIMINI_WORDS = {"karakamsa", "atmakaraka", "amatyakaraka", "chara karaka", "arudha",
                  "upapada", "mandooka", "sthira dasha", "jaimini", "pada"}
MUNDANE_WORDS = {"mundane", "sankranti", "eclipse", "grahana", "ingress", "panchang",
                  "tithi", "karana", "rahu kaal", "yamaganda", "gulika"}

def classify_entity(name: str, description: str = "") -> str:
    """Auto-classify an entity into an astrological category."""
    text = (name + " " + description).lower()

    # Check categories in priority order
    if any(w in text for w in CONJUNCTION_WORDS):
        return "conjunction"
    if any(w in text for w in ASPECT_WORDS):
        return "aspect"
    if any(w in text for w in DASHA_WORDS):
        return "dasha"
    if any(w in text for w in YOGA_WORDS):
        return "yoga"
    if any(w in text for w in ASHTAKAVARGA_WORDS):
        return "ashtakavarga"
    if DIVISIONAL_RE.search(text):
        return "divisional_chart"
    if any(w in text for w in KP_WORDS):
        return "kp_system"
    if any(w in text for w in JAIMINI_WORDS):
        return "jaimini"
    if any(w in text for w in MUNDANE_WORDS):
        return "mundane_hora"
    if any(w in text for w in NAKSHATRA_WORDS):
        return "nakshatra"
    if HOUSES_RE.search(text) or any(w in text for w in HOUSE_WORDS):
        return "house"
    if any(w in text for w in SIGNS):
        return "sign"
    if any(w in text for w in PLANETS):
        return "planet"
    # Check for outcomes (life events, not computable)
    outcome_patterns = [
        "death", "marriage", "wealth", "career", "disease", "child",
        "profession", "income", "loss", "accident", "education",
        "foreign travel", "litigation", "surgery", "divorce"
    ]
    if any(p in text for p in outcome_patterns):
        return "outcome"
    # Check for references (sutra numbers, chart numbers, book names)
    if re.search(r'\b(sutra|chart|page|book|chapter)\s*\d+', text, re.IGNORECASE):
        return "reference"
    return "other"

def is_computable(category: str) -> bool:
    """Can this entity be mapped to an ephemeris calculation?"""
    return category in {
        "planet", "sign", "house", "conjunction", "aspect",
        "dasha", "nakshatra", "ashtakavarga", "divisional_chart",
        "kp_system", "jaimini", "mundane_hora", "yoga"
    }

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def create_db(db_path):
    """Create the SQLite schema."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.executescript("""
        DROP TABLE IF EXISTS entities;
        DROP TABLE IF EXISTS relations;
        DROP TABLE IF EXISTS entity_chunks;
        DROP TABLE IF EXISTS stats;

        CREATE TABLE entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            entity_name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            is_computable BOOLEAN DEFAULT 0,
            embedding_id TEXT,
            source_chunks TEXT,
            created_at INTEGER,
            UNIQUE(source, entity_name)
        );

        CREATE TABLE relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            entity_a TEXT NOT NULL,
            entity_b TEXT NOT NULL,
            category_a TEXT,
            category_b TEXT,
            is_computable BOOLEAN DEFAULT 0
        );

        CREATE TABLE stats (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE INDEX idx_entities_category ON entities(category);
        CREATE INDEX idx_entities_computable ON entities(is_computable);
        CREATE INDEX idx_entities_name ON entities(entity_name);
        CREATE INDEX idx_relations_a ON relations(entity_a);
        CREATE INDEX idx_relations_b ON relations(entity_b);
    """)
    conn.commit()
    return conn

def ingest_entities(conn, source_name, vdb_data, entity_chunks):
    """Ingest entities from VDB data list."""
    c = conn.cursor()
    count = 0
    for entry in vdb_data:
        if not isinstance(entry, dict):
            continue
        name = entry.get("entity_name", "").strip()
        if not name:
            continue
        desc = entry.get("content", "").strip()
        eid = entry.get("__id__", "")
        created = entry.get("__created_at__", 0)
        src_id = entry.get("source_id", "")

        category = classify_entity(name, desc)
        computable = is_computable(category)

        try:
            c.execute("""
                INSERT OR IGNORE INTO entities 
                (source, entity_name, description, category, is_computable, 
                 embedding_id, source_chunks, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (source_name, name, desc, category, computable, eid, src_id, created))
            count += 1
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    return count

def ingest_relations(conn, source_name, rel_data, entity_lookup):
    """Ingest relation pairs."""
    c = conn.cursor()
    count = 0
    for doc_key, doc_val in rel_data.items():
        pairs = doc_val.get("relation_pairs", [])
        for pair in pairs:
            if len(pair) != 2:
                continue
            a, b = pair[0].strip(), pair[1].strip()
            cat_a = entity_lookup.get((source_name, a), classify_entity(a))
            cat_b = entity_lookup.get((source_name, b), classify_entity(b))
            computable = is_computable(cat_a) or is_computable(cat_b)

            c.execute("""
                INSERT INTO relations (source, entity_a, entity_b, category_a, category_b, is_computable)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (source_name, a, b, cat_a, cat_b, computable))
            count += 1

    conn.commit()
    return count

def main():
    print("=" * 60)
    print("PHASE 0.2a: Flattening LightRAG Graphs to SQLite")
    print("=" * 60)

    conn = create_db(DB_PATH)

    # ─── Load VDB data (has descriptions + embeddings) ───
    print("\nLoading VDB entities...")
    nadi_vdb = load_json(os.path.join(BASE, "nadi_sutras_memory", "vdb_entities.json"))
    jaim_vdb = load_json(os.path.join(BASE, "jaimini_memory", "vdb_entities.json"))

    # ─── Load entity chunks (for source mapping) ───
    nadi_ec = load_json(os.path.join(BASE, "nadi_sutras_memory", "kv_store_entity_chunks.json"))
    jaim_ec = load_json(os.path.join(BASE, "jaimini_memory", "kv_store_entity_chunks.json"))

    # ─── Load relations ───
    nadi_rel = load_json(os.path.join(BASE, "nadi_sutras_memory", "kv_store_full_relations.json"))
    jaim_rel = load_json(os.path.join(BASE, "jaimini_memory", "kv_store_full_relations.json"))

    # ─── Ingest entities ───
    print(f"Ingesting Nadi entities ({len(nadi_vdb['data'])} records)...")
    n1 = ingest_entities(conn, "nadi", nadi_vdb["data"], nadi_ec)
    print(f"  -> {n1} Nadi entities ingested")

    print(f"Ingesting Jaimini entities ({len(jaim_vdb['data'])} records)...")
    n2 = ingest_entities(conn, "jaimini", jaim_vdb["data"], jaim_ec)
    print(f"  -> {n2} Jaimini entities ingested")

    # ─── Build entity category lookup for relation classification ───
    c = conn.cursor()
    entity_lookup = {}
    for row in c.execute("SELECT source, entity_name, category FROM entities"):
        entity_lookup[(row[0], row[1])] = row[2]

    # ─── Ingest relations ───
    print(f"\nIngesting Nadi relations...")
    r1 = ingest_relations(conn, "nadi", nadi_rel, entity_lookup)
    print(f"  -> {r1} Nadi relations ingested")

    print(f"Ingesting Jaimini relations...")
    r2 = ingest_relations(conn, "jaimini", jaim_rel, entity_lookup)
    print(f"  -> {r2} Jaimini relations ingested")

    # ─── Compute and store stats ───
    stats = {}
    for label, query in [
        ("total_entities", "SELECT COUNT(*) FROM entities"),
        ("total_relations", "SELECT COUNT(*) FROM relations"),
        ("computable_entities", "SELECT COUNT(*) FROM entities WHERE is_computable = 1"),
        ("computable_relations", "SELECT COUNT(*) FROM relations WHERE is_computable = 1"),
        ("nadi_entities", "SELECT COUNT(*) FROM entities WHERE source = 'nadi'"),
        ("jaimini_entities", "SELECT COUNT(*) FROM entities WHERE source = 'jaimini'"),
    ]:
        val = c.execute(query).fetchone()[0]
        stats[label] = val
        c.execute("INSERT OR REPLACE INTO stats (key, value) VALUES (?, ?)", (label, str(val)))

    # Category breakdown
    print("\n" + "=" * 60)
    print("ENTITY CATEGORY BREAKDOWN")
    print("=" * 60)
    for row in c.execute("""
        SELECT category, COUNT(*) as cnt, 
               SUM(is_computable) as computable
        FROM entities 
        GROUP BY category 
        ORDER BY cnt DESC
    """):
        print(f"  {row[0]:25s} {row[1]:6d} entities  ({row[2]:5d} computable)")
        c.execute("INSERT OR REPLACE INTO stats (key, value) VALUES (?, ?)",
                  (f"cat_{row[0]}", str(row[1])))

    # Relation category breakdown
    print("\n" + "=" * 60)
    print("RELATION STATISTICS")
    print("=" * 60)
    for row in c.execute("""
        SELECT category_a, category_b, COUNT(*) as cnt
        FROM relations
        GROUP BY category_a, category_b
        ORDER BY cnt DESC
        LIMIT 20
    """):
        print(f"  {row[0]:20s} <-> {row[1]:20s} {row[2]:6d} relations")

    conn.commit()

    # ─── Summary ───
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total entities:      {stats['total_entities']}")
    print(f"  Total relations:     {stats['total_relations']}")
    print(f"  Computable entities: {stats['computable_entities']} ({100*stats['computable_entities']/stats['total_entities']:.1f}%)")
    print(f"  Computable relations:{stats['computable_relations']} ({100*stats['computable_relations']/stats['total_relations']:.1f}%)")
    print(f"  Database saved to:   {DB_PATH}")
    print(f"  Database size:       {os.path.getsize(DB_PATH) / 1024 / 1024:.1f} MB")

    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    main()
