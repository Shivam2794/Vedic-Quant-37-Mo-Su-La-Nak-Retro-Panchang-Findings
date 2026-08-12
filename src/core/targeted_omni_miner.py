import requests
import json
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor

DB_NAME = 'holy_grail_strategies_v5.db'

DOMAINS = {
    "Statistical Arbitrage": ["statistical arbitrage", "cointegration trading", "pairs trading strategy", "statistical mean reversion"],
    "Deep Learning": ["transformer trading strategy", "LSTM financial forecasting", "deep learning trading portfolio", "neural network quantitative strategy"],
    "Reinforcement Learning": ["reinforcement learning trading", "PPO portfolio optimization", "DQN trading strategy", "markov decision process trading"],
    "Microstructure & HFT": ["limit order book imbalance", "high frequency trading strategy", "order flow toxicity trading", "VPIN strategy"],
    "NLP & Sentiment": ["NLP trading strategy", "news sentiment alpha", "earnings call sentiment trading", "twitter sentiment quantitative"],
    "Options & Volatility": ["volatility dispersion trading", "options arbitrage strategy", "volatility surface trading", "variance premium strategy"],
    "Macro Regime Detection": ["hidden markov model trading", "macro regime detection strategy", "gaussian mixture model finance", "economic regime rotation"],
    "Alternative Data": ["alternative data trading", "satellite imagery alpha", "credit card data quantitative", "supply chain data trading"],
    "Fixed Income RV": ["fixed income relative value", "yield curve arbitrage", "swap spread trading", "bond basis arbitrage"],
    "Crypto Arbitrage": ["cryptocurrency statistical arbitrage", "funding rate arbitrage", "cross-exchange arbitrage crypto", "defi arbitrage strategy"],
    "Market Making": ["avellaneda stoikov", "automated market making strategy", "inventory management trading", "bid ask spread strategy"],
    "Factor Models": ["statistical factor model trading", "PCA trading strategy", "smart beta quantitative", "risk parity strategy"],
    "Trend Following (CTA)": ["time series momentum strategy", "CTA trend following", "breakout trading quantitative", "managed futures strategy"],
    "Kalman Filters": ["kalman filter trading", "ornstein uhlenbeck pairs trading", "state space model finance", "dynamic linear model trading"],
    "Event Driven": ["event driven quantitative", "post earnings announcement drift strategy", "merger arbitrage quantitative", "spin off trading strategy"],
    "Convertible Arbitrage": ["convertible bond arbitrage", "delta hedging quantitative", "convertible arbitrage strategy"],
    "Commodities & Futures": ["roll yield strategy", "contango backwardation trading", "calendar spread quantitative", "commodity futures strategy"],
    "Tail Risk Hedging": ["tail risk hedging strategy", "VIX futures trading", "black swan protection quantitative", "convexity trading strategy"],
    "Order Flow & Liquidity": ["liquidity provision strategy", "order flow imbalance trading", "tick data quantitative strategy", "market microstructure alpha"],
    "Exotic Derivatives": ["variance swap trading", "volatility index strategy", "dispersion trade", "correlation trading strategy"]
}

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS strategies
                 (id INTEGER PRIMARY KEY, domain TEXT, title TEXT, abstract TEXT, 
                  url TEXT, year INTEGER, citations INTEGER)''')
    conn.commit()
    conn.close()

def search_openalex(domain, keywords):
    print(f"[*] Mining OpenAlex for Domain: {domain}")
    results = []
    for kw in keywords:
        query = kw.replace(" ", "+")
        # Search for works with the keyword in title/abstract, and must mention 'trading' or 'strategy' or 'sharpe'
        url = f"https://api.openalex.org/works?search={query}&filter=title_and_abstract.search:trading|strategy|sharpe,has_abstract:true&per-page=5&sort=cited_by_count:desc"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                for work in data.get('results', []):
                    title = work.get('title', '')
                    abstract_inv = work.get('abstract_inverted_index', {})
                    if not abstract_inv: continue
                    
                    # Reconstruct abstract
                    word_index = []
                    for word, positions in abstract_inv.items():
                        for pos in positions:
                            word_index.append((pos, word))
                    word_index.sort()
                    abstract = " ".join([word for pos, word in word_index])
                    
                    year = work.get('publication_year', 0)
                    citations = work.get('cited_by_count', 0)
                    doi = work.get('doi', '')
                    
                    results.append((domain, title, abstract, doi, year, citations))
            time.sleep(1)
        except Exception as e:
            pass
    return results

def mine_all_domains():
    all_strategies = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for domain, keywords in DOMAINS.items():
            futures.append(executor.submit(search_openalex, domain, keywords))
        
        for future in futures:
            all_strategies.extend(future.result())
            
    # Deduplicate by title
    seen = set()
    unique_strategies = []
    for s in all_strategies:
        title = s[1].lower()
        if title not in seen:
            seen.add(title)
            unique_strategies.append(s)
            
    # Save to DB
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for s in unique_strategies:
        c.execute("INSERT INTO strategies (domain, title, abstract, url, year, citations) VALUES (?, ?, ?, ?, ?, ?)", s)
    conn.commit()
    
    # Check counts
    c.execute("SELECT COUNT(*) FROM strategies")
    count = c.fetchone()[0]
    
    # Get top 5 from each domain
    print(f"\n[+] Total Unique Strategies Found: {count}")
    print("======================================================")
    
    for domain in DOMAINS.keys():
        c.execute("SELECT title, citations FROM strategies WHERE domain=? ORDER BY citations DESC LIMIT 5", (domain,))
        rows = c.fetchall()
        print(f"\n[{domain}]")
        for row in rows:
            print(f"  - {row[0]} (Citations: {row[1]})")
            
    conn.close()

if __name__ == "__main__":
    init_db()
    mine_all_domains()
