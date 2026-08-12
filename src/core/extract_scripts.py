import os
import re

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
md_files = [
    "Synthesizing High-Accuracy Options Data 11.md",
    "Synthesizing High-Accuracy Options Data 12.md",
    "Synthesizing High-Accuracy Options Data 13.md",
    "Scaling Vedic Neural Pipeline.md"
]

print("Scanning markdown files for Python scripts...")

for md_file in md_files:
    path = os.path.join(downloads_dir, md_file)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        continue
    
    print(f"\n==================================================")
    print(f"FILE: {md_file}")
    print(f"==================================================")
    
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Let's search for python or any code blocks robustly
    # We support ```python or ```py or ``` followed by anything, and \r?\n
    code_blocks = re.findall(r'```(?:python|py)?\r?\n(.*?)\r?\n```', content, re.DOTALL)
    print(f"Found {len(code_blocks)} code blocks.")
    
    for idx, block in enumerate(code_blocks):
        lines = block.split('\n')
        # Clean line endings and prefixes if any
        lines = [l.rstrip('\r') for l in lines]
        block_desc = f"Block {idx} ({len(lines)} lines): "
        
        # Identify block contents
        is_ssvi = any('class SSVICalibrator' in l or 'class SSVI' in l or 'SSVICalibrator' in l for l in lines)
        is_interpolator = any('class IntradayInterpolator' in l or 'IntradayInterpolator' in l for l in lines)
        is_microstructure = any('class MicrostructureLayer' in l or 'MicrostructureLayer' in l for l in lines)
        is_validation = any('class ValidationSuite' in l or 'ValidationSuite' in l for l in lines)
        is_anchor = any('class AnchorGenerator' in l or 'AnchorGenerator' in l for l in lines)
        is_vix = any('class VixAnchorGenerator' in l or 'VixAnchorGenerator' in l or 'class VIXAnchor' in l for l in lines)
        is_gpu = 'gpu_historical' in block.lower() or 'gpuhistorical' in block.lower()
        is_massive = 'run_massive' in block.lower() or 'runmassive' in block.lower()
        
        if is_ssvi: block_desc += "[SSVI Calibrator] "
        if is_interpolator: block_desc += "[Intraday Interpolator] "
        if is_microstructure: block_desc += "[Microstructure] "
        if is_validation: block_desc += "[Validation Suite] "
        if is_anchor: block_desc += "[Anchor Generator] "
        if is_vix: block_desc += "[VIX Anchor Generator] "
        if is_gpu: block_desc += "[GPU Historical] "
        if is_massive: block_desc += "[Massive Generation] "
        
        # Look for def or class signatures
        sigs = [l.strip() for l in lines if l.strip().startswith(('def ', 'class '))]
        
        # If the block has a relevant signature or contains classes, print details
        if is_ssvi or is_interpolator or is_microstructure or is_validation or is_anchor or is_vix or is_gpu or is_massive or sigs:
            print(f"  - {block_desc}")
            if sigs:
                print(f"    Signatures: {sigs[:8]}")
            else:
                print(f"    Preview: {lines[0][:100] if lines else ''}")
