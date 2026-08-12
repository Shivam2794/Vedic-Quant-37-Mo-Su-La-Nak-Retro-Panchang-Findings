import requests
import json
import re
import sqlite3
import time
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

DB_NAME = 'holy_grail_strategies_v3.db'

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
    dd_match = re.search(r'(drawdown|max dd|mdd).*?(\d{1,3}\.?\d*)\s*%', text)
    dd = float(dd_match.group(2)) if dd_match else None
    
    # Sharpe
    sharpe_match = re.search(r'sharpe.*?(ratio)?.*?(\d{1}\.\d{1,2})', text)
    sharpe = float(sharpe_match.group(2)) if sharpe_match else None
    
    return cagr, dd, sharpe

def scrape_reddit():
    print("[*] Scraping Reddit (r/algotrading, r/quant)...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) HolyGrailBot/1.0'}
    subreddits = ['algotrading', 'quant', 'options', 'quantitativefinance']
    queries = ['CAGR drawdown', 'strategy beat market', 'Sharpe > 1', 'MAR ratio']
    
    found = 0
    for sub in subreddits:
        for q in queries:
            url = f'https://www.reddit.com/r/{sub}/search.json?q={q}&restrict_sr=on&sort=top&t=all&limit=100'
            try:
                res = requests.get(url, headers=headers, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    for post in data['data']['children']:
                        p = post['data']
                        title = p.get('title', '')
                        text = p.get('selftext', '')
                        url = p.get('url', '')
                        
                        full_text = title + " " + text
                        cagr, dd, sharpe = extract_metrics(full_text)
                        
                        # Store if we found at least some metrics or it's highly relevant
                        if cagr or dd or sharpe or "strategy" in title.lower():
                            save_to_db(f'Reddit (r/{sub})', title, text, url, cagr, dd, sharpe)
                            found += 1
                time.sleep(2)  # Rate limiting
            except Exception as e:
                pass
    print(f"  -> Found {found} Reddit posts.")

def scrape_hackernews():
    print("[*] Scraping HackerNews...")
    queries = ['algorithmic trading', 'quant strategy', 'CAGR drawdown']
    found = 0
    for q in queries:
        url = f'https://hn.algolia.com/api/v1/search?query={q}&hitsPerPage=100'
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                for hit in data['hits']:
                    title = hit.get('title', '')
                    text = hit.get('story_text', '') or ''
                    url = hit.get('url', '') or f"https://news.ycombinator.com/item?id={hit['objectID']}"
                    
                    full_text = title + " " + text
                    cagr, dd, sharpe = extract_metrics(full_text)
                    if cagr or dd or sharpe or "quant" in title.lower():
                        save_to_db('HackerNews', title, text, url, cagr, dd, sharpe)
                        found += 1
            time.sleep(1)
        except Exception as e:
            pass
    print(f"  -> Found {found} HackerNews posts.")

def scrape_arxiv():
    print("[*] Scraping Arxiv (Quantitative Finance)...")
    url = 'http://export.arxiv.org/api/query?search_query=cat:q-fin.TR+AND+(all:"drawdown"+OR+all:"CAGR")&start=0&max_results=200'
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            found = 0
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
                link = entry.find('{http://www.w3.org/2005/Atom}id').text.strip()
                
                cagr, dd, sharpe = extract_metrics(summary)
                save_to_db('Arxiv', title, summary, link, cagr, dd, sharpe)
                found += 1
            print(f"  -> Found {found} Arxiv papers.")
    except Exception as e:
        print(f"  -> Arxiv Error: {e}")

def get_best_strategies():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM strategies WHERE cagr > 14 AND drawdown < 25", conn)
    conn.close()
    return df

if __name__ == "__main__":
    init_db()
    print("========================================")
    print("V3 MASSIVE OMNI-SCRAPER INITIALIZED")
    print("========================================")
    scrape_reddit()
    scrape_hackernews()
    scrape_arxiv()
    
    print("\n[+] Deep Mining Complete. DB: holy_grail_strategies_v3.db")
