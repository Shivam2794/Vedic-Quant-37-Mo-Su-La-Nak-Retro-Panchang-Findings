import os
import re

def fix_ayanamsha_and_close():
    count_ayanamsha = 0
    count_close = 0
    count_double = 0

    for root, _, files in os.walk(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\Vedic-Quant-37-Mo-Su-La-Nak-Retro-Panchang-Findings"):
        for file in files:
            if not file.endswith(".py"):
                continue
                
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue

            orig_content = content

            # Point 5: Move set_sid_mode up.
    if "swe.calc_ut" in content and "swe.set_sid_mode" in content:  # CRITICAL BUG FIX #5: Moved before calc
            # Look for coordinate loops or swe.calc_ut where set_sid_mode might be late.
            # Easiest global fix: if set_sid_mode is not at the module level (e.g., inside a function loop), 
            # make sure it is pushed to the top of the computation block.
                # Check if set_sid_mode is AFTER calc_ut
                idx_calc = content.find("swe.calc_ut")
                if idx_sid > idx_calc:
                    # Move it to immediately before the first calc_ut
                    # Find the line containing set_sid_mode and remove it
                    lines = content.split('\n')
                    new_lines = []
                    sid_line = None
                    for line in lines:
                            sid_line = line.strip()
                            pass # remove duplicates
                        else:
                            new_lines.append(line)
                    
                    if sid_line:
                        # Insert before first calc_ut
                        final_lines = []
                        inserted = False
                        for line in new_lines:
                            if "swe.calc_ut" in line and not inserted:
                                final_lines.append(f"    {sid_line}  # CRITICAL BUG FIX #5: Moved before calc")
                                inserted = True
                            final_lines.append(line)
                        content = '\n'.join(final_lines)
                        count_ayanamsha += 1

            # Point 6: Remove Double Ayanamsha Deduction
            # If we see `FLG_SIDEREAL` and `- ayanamsha`, remove the manual subtraction.
            if "swe.FLG_SIDEREAL" in content and "ayanamsha" in content:
                # Regex to find something like: lon = ... - ayanamsha
                # It's tricky to regex, we look for explicit math
                if re.search(r'-\s*ayanamsha_deg', content):
                    content = re.sub(r'-\s*ayanamsha_deg', '', content)
                    content += "\n# CRITICAL BUG FIX #6: Removed double ayanamsha deduction."
                    count_double += 1

            # Point 17: Add swe.close()
            if "swe.calc_ut" in content and "swe.close()" not in content:
                content += "\n\n# CRITICAL BUG FIX #17: Ensure swisseph is closed\nimport atexit\natexit.register(swe.close)\n"
                count_close += 1

            if content != orig_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

    print(f"Fixed Ayanamsha order in {count_ayanamsha} files.")
    print(f"Fixed Double Ayanamsha in {count_double} files.")
    print(f"Fixed missing swe.close() in {count_close} files.")

if __name__ == "__main__":
    fix_ayanamsha_and_close()
