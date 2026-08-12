import json
import urllib.request
import os

scratch_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
files_to_inspect = [
    "opus13_dual_momentum_gridsearch_v13.py",
    "opus12_erc_optimizer_v12.py",
    "opus12_goal_gridsearch_v12.py",
    "ask_master_brain_v11.py",
    "opus14_genesis_v14.py",
    "ask_master_brain_v13.py",
    "ask_opus5.py",
    "opus11_goal_gridsearch.py",
    "opus10_erc_optimizer_v10.py",
    "opus10_compare_naive.py",
    "opus10_gridsearch_v10.py",
    "master_brain_v9_review.md",
    "ask_master_brain_v9_blocking.py",
    "ask_master_brain_v9.py",
    "test_signal_causality_v8.py",
    "opus8_signal_generator_v8.py",
    "download_and_freeze_data_v2.py",
    "query_opus5_d1_v2.py",
    "test_signal_causality_v7.py",
    "opus8_signal_generator_v7.py",
    "verify_artifacts_v9.py",
    "opus9_signal_generator_v9.py",
    "test_data_causality_v9.py",
    "download_and_freeze_data_v3.py",
    "check_qqq.py",
    "test_signal_causality_v9.py",
    "query_opus5_d1_v8.py",
    "opus8_phase3_optimizer_v2.py",
    "opus8_matrix_gigantic_gridsearch_v5.py",
    "opus8_phase3_optimizer.py",
    "opus8_matrix_gigantic_gridsearch_v4.py",
    "opus8_matrix_gigantic_gridsearch_v3.py",
    "opus8_matrix_1a_generator.py",
    "download_and_freeze_data.py",
    "opus8_config.py",
    "query_opus5_d1.py",
    "test_signal_causality.py",
    "opus8_signal_generator_v6.py",
    "query_opus5.py"
]

compiled_content = ""
for f in files_to_inspect:
    fpath = os.path.join(scratch_dir, f)
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8", errors="ignore") as file:
            compiled_content += f"\n\n--- FILE: {f} ---\n\n"
            compiled_content += file.read()
    else:
        compiled_content += f"\n\n--- FILE: {f} (NOT FOUND) ---\n\n"

prompt = f"""
You are the Brutal Multipoint Quality Inspector (anthropic/claude-opus-5, Max Effort, Adaptive Reasoning).
The user is devastated. In V8 through V11, they saw Sharpe Ratios > 1.5. 
In V14, after stripping away Leveraged ETFs and fixing transaction costs and bugs, the Sharpe crashed to 0.61.
The user refuses to accept this and claims: "this SR and result can't be true at all after trying so many genius things. I want you to do unlimited cycles of brutal multipoint inspection loop of every versions of all above codes and logics of all past trials and ideas to introspect, find bugs and errors and logic gaps and identify what might have derailed this result."

I am feeding you the ENTIRE history of the codebase (39 files).
Your mission:
1. Trace the exact evolutionary lineage of the performance drop. Where EXACTLY did the high Sharpe ratios come from in V8/V10? (Was it purely look-ahead bias? 0*NaN bugs? Compounding math errors? TQQQ in a bull market?)
2. Is V14 (opus14_genesis_v14.py) flawed, or is V14 the ONLY mathematically truthful file in the entire repository? Are there any remaining bugs in V14 that are artificially SUPPRESSING the Sharpe ratio?
3. The user wants to know WHAT derailed the genius ideas. Introspect deeply across all these files. Did we lose a genuinely good alpha signal (like Dual Momentum or specific regime filters) in the transition to V14?
4. Provide the ultimate Brutal Inspection Report that permanently settles the mathematical reality of this strategy. Do not sugarcoat. If the 1.5 Sharpe was a mirage, prove it. If V14 has a bug that killed the Sharpe, expose it.

Here is the entire codebase history:
{compiled_content}
"""

req = urllib.request.Request(
    'https://openrouter.ai/api/v1/chat/completions',
    headers={
        'Authorization': "Bearer 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",
        'Content-Type': 'application/json'
    },
    data=json.dumps({
        'model': 'anthropic/claude-opus-5',
        'messages': [{'role': 'user', 'content': prompt}]
    }).encode('utf-8')
)

try:
    print("Calling Opus 5 Master Brain for the Ultimate Historical Brutal Inspection...")
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        content = result['choices'][0]['message']['content']
        out_path = r'C:\Users\Shivam Patel\.gemini\antigravity\brain\d7a6382f-6722-4f66-a7ae-197ee9225f74\ultimate_brutal_inspection_all_versions.md'
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Saved to ultimate_brutal_inspection_all_versions.md')
except Exception as e:
    print(f'Error: {e}')
