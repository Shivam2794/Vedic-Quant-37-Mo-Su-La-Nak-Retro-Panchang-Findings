import requests
import json
import re
import sqlite3
import time
import random
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

DB_NAME = 'holy_grail_strategies_v4.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS strategies
                 (id INTEGER PRIMARY KEY, source TEXT, title TEXT, content TEXT, 
                  url TEXT, cagr REAL, drawdown REAL, sharpe REAL)''')
    conn.commit()
    conn.close()

def save_to_db(source, title, content, url, cagr, dd, sharpe):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Check if exists to avoid exact duplicates
    c.execute("SELECT id FROM strategies WHERE title=?", (title,))
    if not c.fetchone():
        c.execute('''INSERT INTO strategies (source, title, content, url, cagr, drawdown, sharpe) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', (source, title, content, url, cagr, dd, sharpe))
        conn.commit()
    conn.close()

def extract_metrics(text):
    if not text: return None, None, None
    text = text.lower()
    
    # CAGR
    cagr_match = re.search(r'(cagr|annual return|annualized return|return).*?(\d{1,3}\.?\d*)\s*%', text)
    cagr = float(cagr_match.group(2)) if cagr_match else None
    
    # Drawdown
    dd_match = re.search(r'(drawdown|max dd|mdd|max drawdown).*?(\d{1,3}\.?\d*)\s*%', text)
    dd = float(dd_match.group(2)) if dd_match else None
    
    # Sharpe
    sharpe_match = re.search(r'sharpe.*?(ratio)?.*?(\d{1}\.\d{1,2})', text)
    sharpe = float(sharpe_match.group(2)) if sharpe_match else None
    
    return cagr, dd, sharpe

def fetch_reddit(sub, q, after=""):
    headers = {'User-Agent': f'HolyGrailOmniBot/4.{random.randint(0, 999)}'}
    url = f'https://www.reddit.com/r/{sub}/search.json?q={q}&restrict_sr=on&sort=relevance&t=all&limit=100'
    if after: url += f'&after={after}'
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 429:
            time.sleep(10)
    except Exception:
        pass
    return None

def scrape_reddit():
    print("[*] Launching Massive Reddit Scrape...")
    subreddits = ['algotrading', 'quant', 'options', 'quantitativefinance', 'investing', 
                  'Daytrading', 'LETFs', 'stocks', 'algorithmictrading', 'FinancialEngineering', 
                  'MachineLearning', 'StockMarket', 'finance', 'wallstreetbets']
    queries = ['CAGR drawdown', 'strategy beat market', 'Sharpe', 'backtest returns', 'MAR ratio', 'trading system']
    
    found = 0
    for sub in subreddits:
        for q in queries:
            after = ""
            for _ in range(5): # Up to 500 results per query/sub combo
                data = fetch_reddit(sub, q, after)
                if not data or 'data' not in data or 'children' not in data['data'] or not data['data']['children']:
                    break
                
                for post in data['data']['children']:
                    p = post['data']
                    title = p.get('title', '')
                    text = p.get('selftext', '')
                    url = p.get('url', '')
                    
                    full_text = title + " " + text
                    cagr, dd, sharpe = extract_metrics(full_text)
                    
                    # Store if we found at least some metrics
                    if cagr or dd or sharpe:
                        save_to_db(f'Reddit (r/{sub})', title, text, url, cagr, dd, sharpe)
                        found += 1
                        
                after = data['data'].get('after')
                if not after: break
                time.sleep(random.uniform(1.5, 3.0))
    print(f"  -> Found {found} metric-containing Reddit posts.")

def scrape_hackernews():
    print("[*] Launching Massive HackerNews Scrape...")
    queries = ['algorithmic trading', 'quant strategy', 'CAGR drawdown', 'Sharpe ratio', 'trading system', 'market beating']
    found = 0
    for q in queries:
        for page in range(20): # Up to 2000 results per query
            url = f'https://hn.algolia.com/api/v1/search?query={q}&hitsPerPage=100&page={page}'
            try:
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    if not data['hits']: break
                    
                    for hit in data['hits']:
                        title = hit.get('title', '') or ''
                        text = hit.get('story_text', '') or ''
                        url = hit.get('url', '') or f"https://news.ycombinator.com/item?id={hit['objectID']}"
                        
                        full_text = title + " " + text
                        cagr, dd, sharpe = extract_metrics(full_text)
                        if cagr or dd or sharpe:
                            save_to_db('HackerNews', title, text, url, cagr, dd, sharpe)
                            found += 1
                time.sleep(0.5)
            except Exception:
                pass
    print(f"  -> Found {found} metric-containing HackerNews posts.")

def scrape_arxiv():
    print("[*] Launching Massive Arxiv Scrape...")
    categories = ['q-fin.TR', 'q-fin.PM', 'q-fin.ST', 'cs.LG']
    keywords = ['"drawdown"', '"CAGR"', '"Sharpe"', '"trading strategy"']
    
    found = 0
    for cat in categories:
        for kw in keywords:
            for start in range(0, 2000, 200): # Up to 2000 papers per category/keyword
                url = f'http://export.arxiv.org/api/query?search_query=cat:{cat}+AND+all:{kw}&start={start}&max_results=200'
                try:
                    res = requests.get(url, timeout=15)
                    if res.status_code == 200:
                        root = ET.fromstring(res.content)
                        entries = root.findall('{http://www.w3.org/2005/Atom}entry')
                        if not entries: break
                        
                        for entry in entries:
                            title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
                            link = entry.find('{http://www.w3.org/2005/Atom}id').text.strip()
                            
                            cagr, dd, sharpe = extract_metrics(summary)
                            if cagr or dd or sharpe:
                                save_to_db('Arxiv', title, summary, link, cagr, dd, sharpe)
                                found += 1
                        time.sleep(3) # Be nice to Arxiv
                except Exception:
                    time.sleep(5)
    print(f"  -> Found {found} metric-containing Arxiv papers.")

if __name__ == "__main__":
    init_db()
    print("========================================")
    print("V4 OMNI-SCRAPER (ETERNAL GRIND MODE)")
    print("========================================")
    
    # Run scrapers in parallel to maximize IO throughput
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(scrape_reddit)
        executor.submit(scrape_hackernews)
        executor.submit(scrape_arxiv)
    
    print("\n[+] ETERNAL SCRAPE COMPLETE. DB: holy_grail_strategies_v4.db")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM strategies")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM strategies WHERE (cagr > 14 AND drawdown < 25) OR sharpe > 1.5")
    elite = c.fetchone()[0]
    print(f"[*] Total Strategies Mined: {total}")
    print(f"[*] Elite Holy Grails Found: {elite}")
    conn.close()
