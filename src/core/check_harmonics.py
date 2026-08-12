import json

def check_harmonics():
    with open(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.json', 'r') as f:
        data = json.load(f)

    # Check for duplicate feature lists
    features_list = [tuple(sorted(x['features'])) for x in data]
    
    unique_features = set(features_list)
    print(f"Total entries: {len(data)}")
    print(f"Unique phase states (feature clusters): {len(unique_features)}")
    
    if len(unique_features) < len(data):
        print(f"PHASE COLLAPSE DETECTED: {len(data) - len(unique_features)} redundant harmonic states.")
    else:
        print("NO PHASE COLLAPSE: All harmonic states are distinct.")

    # Let's also check if any score/confidence are strictly identical
    scores = [x['score'] for x in data]
    print(f"Unique scores: {len(set(scores))}")

if __name__ == "__main__":
    check_harmonics()
