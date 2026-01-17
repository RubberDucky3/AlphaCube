
import requests
from bs4 import BeautifulSoup
import sqlite3
from urllib.parse import urlparse, parse_qs, unquote
import time
import re
import os

DB_PATH = "reconstructions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solves (
            solve_id INTEGER PRIMARY KEY,
            solver TEXT,
            time_val FLOAT,
            scramble TEXT,
            solution_raw TEXT,
            url TEXT UNIQUE,
            is_expert BOOLEAN DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()

def scrape_solve(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title: "Solver - Time 3x3 solve"
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else ""
        solver = "Unknown"
        time_val = 0.0
        
        # Try to find solver and time in various formats
        match = re.search(r"(.*?) - ([\d\.]+) (.*?) solve", title)
        if match:
            solver = match.group(1).strip()
            try:
                time_val = float(match.group(2))
            except:
                pass
        
        # Find algbox or alg.cubing.net links
        cubing_link = soup.find('a', href=re.compile(r"alg\.cubing\.net"))
        if not cubing_link:
            return None
            
        href = cubing_link['href']
        parsed = urlparse(href)
        params = parse_qs(parsed.query)
        
        scramble = unquote(params.get('setup', [''])[0]).strip()
        solution = unquote(params.get('alg', [''])[0]).strip()
        
        if not scramble or not solution:
            return None
            
        return {
            'solver': solver,
            'time_val': time_val,
            'scramble': scramble,
            'solution_raw': solution,
            'url': url,
            'title': title
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def save_solve(data):
    if not data: return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO solves (solver, time_val, scramble, solution_raw, url)
            VALUES (?, ?, ?, ?, ?)
        """, (data['solver'], data['time_val'], data['scramble'], data['solution_raw'], data['url']))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Added solve by {data['solver']} ({data['time_val']}s)")
    except Exception as e:
        print(f"Database error: {e}")
    conn.close()

def scrape_solver_list(solver_name):
    print(f"Searching for solves by {solver_name}...")
    # reco.nz/solver/Solver_Name
    formatted_name = solver_name.replace(" ", "_")
    url = f"https://reco.nz/solver/{formatted_name}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Could not find solver {solver_name}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all /solve/XXXXX links
        solve_links = soup.find_all('a', href=re.compile(r"/solve/\d+"))
        
        unique_urls = list(set([f"https://reco.nz{l['href']}" for l in solve_links]))
        print(f"Found {len(unique_urls)} solves for {solver_name}")
        
        for s_url in unique_urls:
            # Check if exists
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT 1 FROM solves WHERE url = ?", (s_url,))
            exists = c.fetchone()
            conn.close()
            
            if not exists:
                data = scrape_solve(s_url)
                save_solve(data)
                time.sleep(1) # Be nice
            else:
                pass
                
    except Exception as e:
        print(f"Error scraping solver list: {e}")

def run_background_scraping():
    init_db()
    # Scrape everything from beginning to now
    start_id = 1
    end_id = 13000
    
    print(f"Mass ID scraping started: {start_id} to {end_id}...")
    
    for sid in range(start_id, end_id + 1):
        url = f"https://reco.nz/solve/{sid}"
        
        # Check if URL already tried (even if failed)
        # Using a simple check for now
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT 1 FROM solves WHERE url = ?", (url,))
        exists = c.fetchone()
        conn.close()
        
        if not exists:
            data = scrape_solve(url)
            if data:
                # Filter for 3x3 solves only
                if "3x3" in data.get('title', ''):
                     save_solve(data)
            
            if sid % 100 == 0:
                print(f"Progress: Processed up to ID {sid}")
            
            time.sleep(0.1) # Faster crawl for mass download
        else:
            pass

if __name__ == "__main__":
    run_background_scraping()
