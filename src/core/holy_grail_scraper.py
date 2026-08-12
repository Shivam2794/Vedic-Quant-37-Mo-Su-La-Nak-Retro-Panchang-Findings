import sqlite3
import time
import re
from duckduckgo_search import DDGS
import requests

DB_PATH = "holy_grail_strategies.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scraped_strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            url TEXT,
            title TEXT,
            snippet TEXT,
            query_used TEXT,
            UNIQUE(url)
        )
    """)
    conn.commit()
    conn.close()

def save_result(source, url, title, snippet, query_used):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT OR IGNORE INTO scraped_strategies (source, url, title, snippet, query_used)
            VALUES (?, ?, ?, ?, ?)
        """, (source, url, title, snippet, query_used))
        conn.commit()
    except Exception as e:
        print(f"Error saving {url}: {e}")
    finally:
        conn.close()

def mine_duckduckgo(ddgs, query, max_results=50):
    print(f"[*] Mining Web: {query}")
    try:
        results = ddgs.text(query, max_results=max_results)
        count = 0
        if results:
            for r in results:
                title = r.get("title", "")
                url = r.get("href", "")
                body = r.get("body", "")
                
                # Check for mention of high cagr or low drawdown to prioritize
                text = (title + " " + body).lower()
                
                save_result("Web Search", url, title, body, query)
                count += 1
        print(f"  -> Found {count} results.")
    except Exception as e:
        print(f"  -> Error: {e}")
    time.sleep(2) # rate limit

def mine_openalex():
    print("[*] Mining OpenAlex for Academic Papers...")
    # Search for papers discussing high CAGR and low drawdown trading strategies
    url = "https://api.openalex.org/works"
    params = {
        "search": "trading strategy cagr drawdown",
        "filter": "title_and_abstract.search:cagr,title_and_abstract.search:drawdown",
        "per-page": 100,
        "sort": "cited_by_count:desc"
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            count = 0
            for r in results:
                title = r.get("title", "")
                doi = r.get("doi", "")
                abstract = r.get("abstract_inverted_index", {})
                
                # Reconstruct abstract
                abs_text = ""
                if abstract:
                    word_index = []
                    for word, positions in abstract.items():
                        for pos in positions:
                            word_index.append((pos, word))
                    word_index.sort()
                    abs_text = " ".join([word for pos, word in word_index])
                
                if not doi:
                    doi = r.get("id", "")
                
                save_result("OpenAlex", doi, title, abs_text, "trading strategy cagr drawdown")
                count += 1
            print(f"  -> Found {count} papers.")
    except Exception as e:
        print(f"  -> OpenAlex Error: {e}")


def main():
    init_db()
    
    # 20+ Highly specific queries for discovering the holy grail
    queries = [
        # Broad strategy search
        '"CAGR > 14%" OR "CAGR > 15%" "max drawdown" strategy',
        '"CAGR of 15%" "drawdown under 25%" trading',
        '"beating QQQ" systematic trading',
        '"beat QQQ" strategy "max drawdown"',
        
        # Site specific - Reddit
        'site:reddit.com/r/algotrading "CAGR" "drawdown" "15%"',
        'site:reddit.com/r/algotrading "beat SPY" OR "beat QQQ" "drawdown"',
        'site:reddit.com/r/quant "CAGR" "drawdown" strategy',
        'site:reddit.com/r/investing "CAGR" "drawdown" backtest 10 years',
        
        # Site specific - QuantConnect
        'site:quantconnect.com/forum "CAGR" "Drawdown" "15%"',
        'site:quantconnect.com/forum "beating QQQ" OR "beat the market"',
        
        # Site specific - EliteTrader
        'site:elitetrader.com "CAGR" "max drawdown" strategy',
        
        # Site specific - SSRN and Arxiv (via web)
        'site:ssrn.com "trading strategy" "CAGR" "drawdown"',
        'site:arxiv.org "quantitative trading" "annualized return" "max drawdown"',
        
        # Site specific - SeekingAlpha
        'site:seekingalpha.com "CAGR" "max drawdown" "trading system"',
        
        # General exact match phrases
        '"CAGR of 20%" "max drawdown"',
        '"Sharpe > 1.5" "Drawdown < 20%"',
        '"annualized return" > 15% "maximum drawdown"',
        '"backtest" "10 years" "CAGR" "drawdown"',
        '"backtest" "20 years" "CAGR" "drawdown"'
    ]
    
    ddgs = DDGS()
    
    for q in queries:
        mine_duckduckgo(ddgs, q, max_results=30)
        
    mine_openalex()
    
    # Print summary
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    total = cur.execute("SELECT count(*) FROM scraped_strategies").fetchone()[0]
    print(f"\n[+] Mining Complete. Total distinct strategies/items found: {total}")
    conn.close()

if __name__ == "__main__":
    main()
