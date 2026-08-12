import sqlite3
import time
import re
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

DB_PATH = "holy_grail_strategies_v2.db"

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
            full_text TEXT,
            query_used TEXT,
            cagr_extracted REAL,
            dd_extracted REAL,
            UNIQUE(url)
        )
    """)
    conn.commit()
    conn.close()

def extract_metrics(text):
    """
    Smartly extract CAGR and Drawdown numbers using Regex.
    Returns (cagr_val, dd_val) or (None, None)
    """
    cagr = None
    dd = None
    text = text.lower()
    
    # Match patterns like: "CAGR: 18%", "CAGR of 15.5%", "Return: 22%", "annualized return of 14%"
    cagr_patterns = [
        r'cagr\s*(?:of|:|is|=|>)?\s*(\d{2,3}(?:\.\d+)?)\s*%',
        r'annualized return\s*(?:of|:|is|=|>)?\s*(\d{2,3}(?:\.\d+)?)\s*%',
        r'annual return\s*(?:of|:|is|=|>)?\s*(\d{2,3}(?:\.\d+)?)\s*%',
        r'return\s*(?:of|:|is|=|>)?\s*(\d{2,3}(?:\.\d+)?)\s*cagr'
    ]
    
    # Match patterns like: "max drawdown: 12%", "drawdown of 20%", "mdd: 15%"
    dd_patterns = [
        r'drawdown\s*(?:of|:|is|=|<)?\s*(\d{1,2}(?:\.\d+)?)\s*%',
        r'max dd\s*(?:of|:|is|=|<)?\s*(\d{1,2}(?:\.\d+)?)\s*%',
        r'mdd\s*(?:of|:|is|=|<)?\s*(\d{1,2}(?:\.\d+)?)\s*%',
        r'drawdown\s*<\s*(\d{1,2}(?:\.\d+)?)'
    ]
    
    for p in cagr_patterns:
        m = re.search(p, text)
        if m:
            try:
                val = float(m.group(1))
                if 10 <= val <= 200: # reasonable bounds
                    cagr = val
                    break
            except: pass
            
    for p in dd_patterns:
        m = re.search(p, text)
        if m:
            try:
                val = float(m.group(1))
                if 0 <= val <= 60: # reasonable bounds
                    dd = val
                    break
            except: pass
            
    return cagr, dd

def save_result(source, url, title, snippet, full_text, query_used):
    cagr, dd = extract_metrics(title + " " + snippet + " " + full_text)
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT OR IGNORE INTO scraped_strategies (source, url, title, snippet, full_text, query_used, cagr_extracted, dd_extracted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (source, url, title, snippet, full_text, query_used, cagr, dd))
        conn.commit()
    except Exception as e:
        print(f"Error saving {url}: {e}")
    finally:
        conn.close()

def mine_duckduckgo(ddgs, query, max_results=30):
    print(f"[*] Mining Web: {query}")
    try:
        results = ddgs.text(query, max_results=max_results)
        count = 0
        if results:
            for r in results:
                title = r.get("title", "")
                url = r.get("href", "")
                body = r.get("body", "")
                
                # Fetch full text if it's a forum or reddit
                full_text = ""
                if "reddit.com" in url or "quantconnect.com" in url or "elitetrader.com" in url:
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                        resp = requests.get(url, headers=headers, timeout=5)
                        if resp.status_code == 200:
                            soup = BeautifulSoup(resp.text, 'html.parser')
                            full_text = soup.get_text(separator=' ', strip=True)[:10000] # Limit size
                    except:
                        pass
                
                save_result("Web Search", url, title, body, full_text, query)
                count += 1
        print(f"  -> Found {count} results.")
    except Exception as e:
        print(f"  -> Error: {e}")
    time.sleep(2)

def mine_openalex():
    print("[*] Mining OpenAlex for Academic Papers...")
    url = "https://api.openalex.org/works"
    params = {
        "search": "quantitative trading strategy",
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
                
                save_result("OpenAlex", doi, title, abs_text, "", "quantitative trading strategy")
                count += 1
            print(f"  -> Found {count} papers.")
    except Exception as e:
        print(f"  -> OpenAlex Error: {e}")


def main():
    init_db()
    
    # Broader queries to let DDG find semantic matches
    queries = [
        'quant strategy CAGR max drawdown backtest',
        'beating QQQ systematic trading system',
        'site:reddit.com/r/algotrading CAGR drawdown 10 years',
        'site:reddit.com/r/algotrading "beat QQQ" strategy',
        'site:reddit.com/r/quant "annualized return" drawdown strategy',
        'site:quantconnect.com/forum CAGR drawdown beat market',
        'site:quantconnect.com/forum strategy CAGR > 15%',
        'site:elitetrader.com CAGR drawdown backtest',
        'site:ssrn.com "trading strategy" CAGR drawdown',
        'site:arxiv.org "quantitative trading" annualized return max drawdown',
        'site:seekingalpha.com CAGR max drawdown trading system',
        'robust trading strategy CAGR 15% drawdown 20%',
        'backtest 10 years CAGR drawdown quantitative'
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
    
    print("\n[*] High Potential Strategies (CAGR > 14% AND DD < 25%):")
    holy_grails = cur.execute("SELECT url, title, cagr_extracted, dd_extracted FROM scraped_strategies WHERE cagr_extracted >= 14 AND dd_extracted <= 25").fetchall()
    for hg in holy_grails:
        print(f"  -> CAGR: {hg[2]}% | DD: {hg[3]}% | {hg[1]} | {hg[0]}")
        
    print("\n[*] Strategies beating QQQ (CAGR > 14%, unknown DD):")
    high_cagr = cur.execute("SELECT url, title, cagr_extracted, dd_extracted FROM scraped_strategies WHERE cagr_extracted >= 14 AND dd_extracted IS NULL").fetchall()
    for hc in high_cagr[:10]:
        print(f"  -> CAGR: {hc[2]}% | {hc[1]} | {hc[0]}")
        
    conn.close()

if __name__ == "__main__":
    main()
