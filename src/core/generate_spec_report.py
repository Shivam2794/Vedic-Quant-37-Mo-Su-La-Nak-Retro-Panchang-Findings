import sqlite3
import pandas as pd

def generate_spec_report():
    conn = sqlite3.connect('holy_grail_strategies_v4.db')
    
    # Get top 50 by Sharpe, then top 50 by CAGR
    query = """
    SELECT source, title, content, url, cagr, drawdown, sharpe 
    FROM strategies 
    WHERE (cagr > 14 AND drawdown < 25) OR sharpe > 1.5
    ORDER BY sharpe DESC NULLS LAST, cagr DESC NULLS LAST
    LIMIT 100
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    with open('actual_scraped_specs.md', 'w', encoding='utf-8') as f:
        f.write("# 🔬 Extracted Core Specifications (V4 Omni-Scraper DB)\n\n")
        f.write("This artifact contains the actual raw data, mathematical claims, and abstracts extracted directly from the web sources.\n\n")
        
        for idx, row in df.iterrows():
            f.write(f"## {idx+1}. {row['title']}\n")
            f.write(f"**Source:** {row['source']} | **URL:** {row['url']}\n")
            
            # Metrics
            f.write("**Quantitative Claims:**\n")
            if pd.notna(row['cagr']):
                f.write(f"- **CAGR:** {row['cagr']}%\n")
            if pd.notna(row['drawdown']):
                f.write(f"- **Max Drawdown:** {row['drawdown']}%\n")
            if pd.notna(row['sharpe']):
                f.write(f"- **Sharpe Ratio:** {row['sharpe']}\n")
            
            f.write("\n**Core Spec / Abstract Extract:**\n")
            # Truncate content if it's absurdly long, but keep it long enough for parameters
            content = str(row['content'])
            if len(content) > 1500:
                content = content[:1500] + "... [TRUNCATED]"
            f.write(f"> {content}\n\n")
            f.write("---\n\n")

if __name__ == "__main__":
    generate_spec_report()
