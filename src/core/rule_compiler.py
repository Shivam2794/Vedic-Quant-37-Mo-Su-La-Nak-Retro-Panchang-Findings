"""
Rule-to-Code Compiler
=====================
Parses the deduplicated astrological rules from vedic_knowledge.db
and compiles them into executable Python functions (boolean expressions)
that evaluate against the Ephemeris Engine's feature dictionary.
"""
import sqlite3
import re
import json

DB_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\vedic_knowledge.db"

# ─── Regular Expressions for AST Parsing ───
PLANETS_RE = r"(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)"
SIGNS_RE = r"(Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces)"
HOUSES_RE = r"(\d{1,2})(?:st|nd|rd|th)?\s+House"

# 1. Conjunctions: "Sun-Jupiter Conjunction", "Conjunction of Mars and Venus", "Mars Conjunct Moon"
re_conj_1 = re.compile(rf"{PLANETS_RE}\s*-\s*{PLANETS_RE}\s*(?:Conjunction|Combination)", re.IGNORECASE)
re_conj_2 = re.compile(rf"Conjunction\s+of\s+{PLANETS_RE}\s+and\s+{PLANETS_RE}", re.IGNORECASE)
re_conj_3 = re.compile(rf"{PLANETS_RE}\s+(?:Conjunct|with)\s+{PLANETS_RE}", re.IGNORECASE)

# 2. Aspects: "Saturn Aspect On Moon", "Jupiter Aspects Sun", "Mars trine Venus"
re_asp_1 = re.compile(rf"{PLANETS_RE}\s+Aspect(?:s|ing)?\s+(?:On\s+)?{PLANETS_RE}", re.IGNORECASE)
re_asp_2 = re.compile(rf"{PLANETS_RE}\s+(?:trine|square|sextile|opposition)\s+{PLANETS_RE}", re.IGNORECASE)

# 3. Placement (Sign): "Mars in Aries", "Venus placed in Taurus"
re_sign = re.compile(rf"{PLANETS_RE}\s+(?:in|placed in|occupying)\s+(?:the\s+sign\s+of\s+)?{SIGNS_RE}", re.IGNORECASE)

# 4. Placement (House): "Jupiter in 5th House"
re_house = re.compile(rf"{PLANETS_RE}\s+(?:in|placed in)\s+{HOUSES_RE}", re.IGNORECASE)

# 5. Dasha: "Venus Mahadasha", "Saturn Dasha"
re_dasha = re.compile(rf"{PLANETS_RE}\s+(?:Mahadasha|Dasha|Period)", re.IGNORECASE)

def compile_rule(entity_name: str) -> str:
    """Returns a Python boolean expression string, or None if it cannot be compiled."""
    name = entity_name.strip()
    
    # 1. Conjunctions
    m = re_conj_1.search(name) or re_conj_2.search(name) or re_conj_3.search(name)
    if m:
        p1, p2 = m.groups()
        p1 = p1.capitalize()
        p2 = p2.capitalize()
        if p1 == p2: return None
        return f"features.get('aspect_{p1}_{p2}_conj', 0.0) > 0.8 or features.get('aspect_{p2}_{p1}_conj', 0.0) > 0.8"
        
    # 2. Aspects
    m = re_asp_1.search(name)
    if m:
        p1, p2 = m.groups()
        p1 = p1.capitalize()
        p2 = p2.capitalize()
        if p1 == p2: return None
        # We check all aspects since "aspect" is generic in Vedic (could be 7th, trine, special)
        # Using a threshold of > 0.5 for aspect presence
        return (f"(features.get('aspect_{p1}_{p2}_opp', 0.0) > 0.5 or "
                f"features.get('aspect_{p2}_{p1}_opp', 0.0) > 0.5 or "
                f"features.get('aspect_{p1}_{p2}_sqr', 0.0) > 0.5 or "
                f"features.get('aspect_{p2}_{p1}_sqr', 0.0) > 0.5 or "
                f"features.get('aspect_{p1}_{p2}_tri', 0.0) > 0.5 or "
                f"features.get('aspect_{p2}_{p1}_tri', 0.0) > 0.5)")
                
    m = re_asp_2.search(name)
    if m:
        p1, p2 = m.groups()
        p1, p2 = p1.capitalize(), p2.capitalize()
        asp_type = "tri" if "trine" in name.lower() else "sqr" if "square" in name.lower() else "sext" if "sextile" in name.lower() else "opp"
        return f"features.get('aspect_{p1}_{p2}_{asp_type}', 0.0) > 0.8 or features.get('aspect_{p2}_{p1}_{asp_type}', 0.0) > 0.8"
        
    # 3. Placement in Sign
    m = re_sign.search(name)
    if m:
        p1, sign = m.groups()
        p1, sign = p1.capitalize(), sign.capitalize()
        return f"features.get('{p1}_sign_name', '') == '{sign}'"
        
    # 4. Placement in House
    m = re_house.search(name)
    if m:
        p1, house_num = m.groups()
        p1 = p1.capitalize()
        return f"features.get('{p1}_house', 0) == {house_num}"
        
    # 5. Dasha
    m = re_dasha.search(name)
    if m:
        p1 = m.group(1).capitalize()
        return f"features.get('dasha_{p1}', 0.0) == 1.0"
        
    return None

def main():
    print("=" * 60)
    print("PHASE 0.6: Astrological Rule-to-Code Compiler")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Add compiled_code column if not exists
    try:
        c.execute("ALTER TABLE entities ADD COLUMN compiled_code TEXT")
    except sqlite3.OperationalError:
        pass
        
    # Get all computable cluster representatives
    rules = c.execute("SELECT id, entity_name, category FROM entities WHERE is_computable=1 AND is_cluster_rep=1").fetchall()
    print(f"Total computable rules: {len(rules)}")
    
    success = 0
    compiled_dict = {}
    
    for rid, name, category in rules:
        expr = compile_rule(name)
        if expr:
            c.execute("UPDATE entities SET compiled_code = ? WHERE id = ?", (expr, rid))
            compiled_dict[name] = expr
            success += 1
            
    conn.commit()
    print(f"\nSuccessfully compiled: {success} / {len(rules)} ({success/len(rules)*100:.1f}%)")
    
    print("\nSample Compiled Expressions:")
    sample_compiled = list(compiled_dict.items())[:20]
    for name, expr in sample_compiled:
        print(f"  {name:30s} => {expr}")
        
    # Save the dictionary for the feature matrix builder
    with open(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\compiled_rules.json", "w") as f:
        json.dump(compiled_dict, f, indent=2)
        
    print("\nSaved compiled rules to compiled_rules.json")

if __name__ == "__main__":
    main()
