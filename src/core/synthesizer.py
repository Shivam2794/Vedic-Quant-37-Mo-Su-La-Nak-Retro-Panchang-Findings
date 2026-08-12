import os
import glob

raw_dir = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\encyclopedia_raw_notes'
artifacts_dir = r'C:\Users\Shivam Patel\.gemini\antigravity\brain\ac09686f-b2e2-4349-aa40-8ff7fa4bba80\artifacts'
os.makedirs(artifacts_dir, exist_ok=True)

categories = {
    'Origins & Objectives': ('vol1_origins_and_objectives.md', 'origin'),
    'The Data Wars & Feature Columns': ('vol2_datasets_and_features.md', 'dataset'),
    'Architectural Master Plans': ('vol3_architectural_plans.md', 'plan'),
    'Execution Results & File Registry': ('vol4_execution_and_files.md', 'result'),
    'The Graveyard of Failures & Errors': ('vol5_failures_and_errors.md', 'failure')
}

for title, (filename, term) in categories.items():
    output_path = os.path.join(artifacts_dir, filename)
    files = glob.glob(os.path.join(raw_dir, f'*{term}*.md'))
    
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(f'# Volume: {title}\n\n')
        out.write('> [!NOTE]\n> This volume contains the exhaustive, unsummarized historical records compiled by the Forensic_Neural_Reader fleet from the USA Vedic Quant master transcript.\n\n')
        
        for file in sorted(files):
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().strip()
                    if content:
                        out.write(f'## Source Extract: {os.path.basename(file)}\n\n')
                        out.write(content)
                        out.write('\n\n---\n\n')
            except Exception as e:
                print(f"Failed to read {file}: {e}")

print('Successfully synthesized all 5 Volumes into the artifacts directory.')
