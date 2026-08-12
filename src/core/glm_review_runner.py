import requests
import json

api_key = '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'

with open('Codebase/vedic/z_axis_declination.py', 'r') as fh:
    code = fh.read()

prompt = (
    "You are a world-class expert in Swiss Ephemeris (pyswisseph) computational astronomy AND Vedic/Jyotish financial astrology (Medini Jyotish).\n\n"
    "I am building a quantitative financial astrology ML pipeline to predict NYSE/SPY Wall Street market movements.\n\n"
    "This code has now been through TWO brutal review passes. All previously found bugs have been fixed:\n"
    "- Round 1: Removed dead set_topo(), added hemisphere sign constraint, replaced boolean thresholds with Gaussian kernels\n"
    "- Round 2: Fixed Vyatipata to check min(dist_to_180, dist_to_360), eliminated 999.0 sentinel values, added OOB planets, added Parallel/Contra-Parallel aspects\n\n"
    "Here is the FINAL production code after all fixes:\n\n"
    "```python\n" + code + "\n```\n\n"
    "This is your THIRD and FINAL inspection. Use your absolute maximum reasoning depth.\n\n"
    "Inspect everything:\n"
    "1. The OOB (Out of Bounds) detection - is SOLAR_DECLINATION_MAX = 23.4367 the correct threshold? Should it be computed dynamically from the actual Sun's current max declination based on the obliquity of the ecliptic for that year (which changes slowly over centuries)?\n"
    "2. The Parallel/Contra-Parallel sigma of 0.5 degrees - is this the classical orb used in declination astrology?\n"
    "3. The sign_product == 0 edge case (exact equatorial crossing) - are both triggers firing simultaneously at 1.0 correct classically?\n"
    "4. The Vaidhriti longitude threshold is dist_to_360 ONLY. But classically Vaidhriti also has a secondary trigger at 180 deg when the Moon is in the same hemisphere as the Sun? Review this.\n"
    "5. The Parallel/Contra-Parallel pairings only use fast-to-slow. Should we also compute Moon-to-Moon (auto-parallel which cannot exist), or Moon to Ketu/Rahu parallels?\n"
    "6. Is there a risk of NaN or division-by-zero in any part of this code?\n"
    "7. The OOB_Ketu feature at the bottom uses `declinations['Rahu']` but Ketu was never added to the planets dict. Is this consistent?\n"
    "8. For the Gaussian kernels, should the product of long_prox * dec_prox be replaced with a geometric mean or minimum to avoid one very weak factor killing a strong proximity signal?\n"
    "9. Any remaining classical astrology errors in the Maha Pata logic?\n"
    "10. Is this code now production-ready for a live quantitative trading system? Final verdict.\n\n"
    "Be absolutely ruthless. This is the final gate before production deployment."
)

headers = {
    'Authorization': 'Bearer ' + api_key,
    'Content-Type': 'application/json',
    'HTTP-Referer': 'https://antigravity.ai',
    'X-Title': 'Orion Alpha Engine - Z-Axis Round 3 Final'
}

payload = {
    'model': 'z-ai/glm-5.2',
    'messages': [{'role': 'user', 'content': prompt}],
    'temperature': 0.1,
    'max_tokens': 65000,
    'reasoning': {'effort': 'xhigh'},
    'include_reasoning': True
}

print('Sending FINAL Z-Axis code to GLM-5.2 (xhigh reasoning, 65k token budget)...')
r = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers=headers,
    json=payload,
    timeout=600
)
data = r.json()

if 'choices' in data:
    msg = data['choices'][0]['message']
    content = msg.get('content') or ''
    reasoning = msg.get('reasoning') or ''
    finish_reason = data['choices'][0].get('finish_reason', 'unknown')
    usage = data.get('usage', {})

    print('Finish reason: ' + finish_reason)
    print('Total tokens used: ' + str(usage.get('total_tokens', '?')))
    print('Reasoning tokens: ' + str(usage.get('completion_tokens_details', {}).get('reasoning_tokens', '?')))
    print('Cost: $' + str(usage.get('cost', '?')))
    print()

    full_review = content if content.strip() else reasoning

    print('=== GLM-5.2 | XHIGH REASONING | ROUND 3 FINAL VERDICT ===')
    print(full_review)

    with open('glm_z_axis_review_round3_xhigh.txt', 'w', encoding='utf-8') as fout:
        fout.write('FINISH REASON: ' + finish_reason + '\n')
        fout.write('TOKENS: ' + str(usage.get('total_tokens', '?')) + '\n')
        fout.write('COST: $' + str(usage.get('cost', '?')) + '\n\n')
        fout.write('=== XHIGH REASONING CHAIN ===\n')
        fout.write(reasoning + '\n\n')
        fout.write('=== FINAL VERDICT ===\n')
        fout.write(content)
    print()
    print('Full review saved to glm_z_axis_review_round3_xhigh.txt')
else:
    print('Error response:')
    print(json.dumps(data, indent=2))
