import os
import requests
import json

api_key = "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"

def query_fable():
    data = {
        "model": "~anthropic/claude-fable-latest",
        "messages": [
            {"role": "system", "content": "You are FABLE, an elite, hyper-critical quant architect."},
            {"role": "user", "content": """
Fable, we implemented your 9-Point Grinder to reality-check our 1.91 Sharpe strategy. It brilliantly proved the strategy was a mirage (negative appraisal ratio, 100% reliant on Bitcoin beta). 

However, we ran three of our own Brutal Quality Inspector subagents on YOUR python code, and they found 6 critical mathematical flaws in how you built the Grinder:

1. **Deflated Sharpe Ratio Bug:** You calculated `SR0` using the time-series variance of the single strategy, which shrinks to 0 over 10 years. Bailey & Lopez de Prado state this must be the cross-sectional variance of the trial strategies. Your hurdle shrank to 0.
2. **Incremental Sharpe Bug:** You calculated active return as `port - base`. This is mathematically invalid; if a strategy uses leverage (`port = 2 * base`), it yields a positive active Sharpe despite having zero alpha. We changed it to a beta-adjusted Appraisal Ratio.
3. **Drift Haircut Volatility Leak:** Your additive log-drift shift (`np.expm1(log_b + shift)`) accidentally shrunk the arithmetic standard deviation, falsely inflating the post-haircut Sharpe.
4. **Pre-2018 25% Drag:** You allowed my 10bps daily gap penalty to remain, which equated to a massive 25.2% annualized drag. You also applied the 55bps crypto slippage to the SPY and GLD turnover legs.
5. **Block Bootstrap Time-Travel:** Your circular block bootstrap logic `(starts + offsets) % T` wrapped 2024 price action directly into 2014, creating a synthetic regime shock that destroys path-dependent metric analysis like CPPI.
6. **Linear Variance Compression:** Same as point 3, your math compressed the linear variance of the benchmark.

We fixed all 6 of your math flaws. (The strategy STILL failed the Grinder even with the math fixed in its favor). 

But I want to know: How do you plead to these 6 mathematical flaws found in your Grinder code by our subagents?
            """}
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://antigravity.local",
        "X-Title": "Antigravity Agent"
    }
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data)
        )
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        with open("fable_flaw_response.md", "w", encoding='utf-8') as f:
            f.write("# Fable's Response to the 6 Math Flaws\n\n")
            f.write(content)
            
        print("Successfully queried Fable and wrote response to fable_flaw_response.md")
            
    except Exception as e:
        print(f"Error querying Fable: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Response details: {response.text}")

if __name__ == "__main__":
    query_fable()
