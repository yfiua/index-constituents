#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import time
import random
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional, List, Dict, Any, Callable

import pandas as pd
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

# Import parsers from the main script
import importlib.util
spec = importlib.util.spec_from_file_location("get_constituents", "index-constituents-repo/get-constituents.py")
gc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gc)

WAYBACK_AVAILABLE_API = "https://archive.org/wayback/available"
WAYBACK_CDX_API = "http://web.archive.org/cdx/search/cdx"
WIKI_API_URL = "https://en.wikipedia.org/w/api.php"

class HistoricalFetcher:
    def __init__(self, code: str, name: str, url: str, fetch_func: Callable, **kwargs):
        self.code = code
        self.name = name
        self.url = url
        self.fetch_func = fetch_func
        self.kwargs = kwargs
        self.is_wiki = "wikipedia.org" in url

    def discover_earliest(self) -> str:
        """Query Wayback CDX or Wikipedia API to find the first recorded date, capped at 2008."""
        print(f"Discovering history for {self.code}...")
        safe_limit = "20080101"
        found_start = None
        
        if self.is_wiki:
            wiki_title = self.url.split("/wiki/")[-1]
            params = {
                "action": "query", "prop": "revisions", "titles": wiki_title,
                "rvlimit": 1, "rvdir": "newer", "format": "json"
            }
            try:
                r = requests.get(WIKI_API_URL, params=params, timeout=10)
                data = r.json()
                pages = data.get('query', {}).get('pages', {})
                for pgid in pages:
                    revs = pages[pgid].get('revisions', [])
                    if revs: found_start = revs[0]['timestamp'][:10].replace('-', '')
            except: pass
        else:
            try:
                params = {'url': self.url, 'output': 'json', 'limit': 1, 'fl': 'timestamp'}
                r = requests.get(WAYBACK_CDX_API, params=params, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    if len(data) > 1: found_start = data[1][0][:8]
            except: pass

        if found_start:
            return max(found_start, safe_limit)
        return safe_limit

    def get_wiki_revid(self, date_str: str) -> Optional[str]:
        wiki_title = self.url.split("/wiki/")[-1]
        target_dt = datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%dT00:00:00Z')
        params = {
            "action": "query", "prop": "revisions", "titles": wiki_title,
            "rvlimit": 1, "rvstart": target_dt, "rvdir": "older", "format": "json"
        }
        try:
            r = requests.get(WIKI_API_URL, params=params, timeout=10)
            data = r.json()
            pages = data.get('query', {}).get('pages', {})
            for pgid in pages:
                revs = pages[pgid].get('revisions', [])
                if revs: return revs[0]['revid']
        except: pass
        return None

    def get_historical_url(self, date_str: str) -> Optional[str]:
        if self.is_wiki:
            revid = self.get_wiki_revid(date_str)
            if revid:
                wiki_title = self.url.split("/wiki/")[-1]
                return f"https://en.wikipedia.org/w/index.php?title={wiki_title}&oldid={revid}"
        else:
            try:
                params = {'url': self.url, 'timestamp': date_str}
                r = requests.get(WAYBACK_AVAILABLE_API, params=params, timeout=10)
                data = r.json()
                snapshot = data.get('archived_snapshots', {}).get('closest', {})
                if snapshot.get('available'): return snapshot['url']
            except: pass
        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=5, max=30))
    def fetch_historical(self, date_str: str) -> Optional[pd.DataFrame]:
        target_url = self.get_historical_url(date_str)
        if not target_url: return None
        
        headers = {'User-Agent': gc.ua.random}
        try:
            return self.fetch_func(target_url, headers=headers, **self.kwargs)
        except (ValueError, requests.exceptions.HTTPError):
            return None

# Index Definitions
FETCHERS = [
    HistoricalFetcher('sp500', 'S&P 500', 'https://www.slickcharts.com/sp500', gc.get_constituents_from_slickcharts),
    HistoricalFetcher('nasdaq100', 'NASDAQ 100', 'https://www.slickcharts.com/nasdaq100', gc.get_constituents_from_slickcharts),
    HistoricalFetcher('dowjones', 'Dow Jones', 'https://www.slickcharts.com/dowjones', gc.get_constituents_from_slickcharts),
    HistoricalFetcher('dax', 'DAX', 'https://www.bloomberg.com/quote/DAX:IND/members', gc.get_constituents_from_bloomberg, converter=lambda s: s.replace(':GR', '.DE')),
    HistoricalFetcher('hsi', 'HSI', 'https://www.bloomberg.com/quote/HSI:IND/members', gc.get_constituents_from_bloomberg, converter=lambda s: s.rjust(7, '0').replace(':', '.')),
    HistoricalFetcher('ftse100', 'FTSE 100', 'https://www.bloomberg.com/quote/UKX:IND/members', gc.get_constituents_from_bloomberg, converter=lambda s: s.replace(':LN', '.L')),
    HistoricalFetcher('ibex35', 'IBEX 35', 'https://en.wikipedia.org/wiki/IBEX_35', gc.get_constituents_from_wikipedia),
    HistoricalFetcher('ftsemib', 'FTSE MIB', 'https://en.wikipedia.org/wiki/FTSE_MIB', gc.get_constituents_from_wikipedia),
    HistoricalFetcher('nifty50', 'NIFTY 50', 'https://en.wikipedia.org/wiki/NIFTY_50', gc.get_constituents_from_wikipedia, suffix='.NS'),
    HistoricalFetcher('asx200', 'S&P/ASX 200', 'https://en.wikipedia.org/wiki/S%26P/ASX_200', gc.get_constituents_from_wikipedia, suffix='.AX'),
]

def main():
    parser = argparse.ArgumentParser(description='Dataload historical constituents using Wikipedia Revisions & Wayback Machine')
    parser.add_argument('--indices', nargs='+', default=['all'], help='Indices to backfill')
    parser.add_argument('--start-date', help='Override discovery (YYYYMMDD)')
    parser.add_argument('--output', default='docs', help='Output directory')
    args = parser.parse_args()

    target_fetchers = FETCHERS if 'all' in args.indices else [f for f in FETCHERS if f.code in args.indices]

    for f in target_fetchers:
        start_date = args.start_date or f.discover_earliest()
        print(f"Backfilling {f.name} from {start_date}...")
        
        current = datetime.strptime(start_date, '%Y%m%d')
        current = current.replace(day=1)
        end = datetime.now()
        
        while current <= end:
            ds = current.strftime('%Y%m%d')
            folder = os.path.join(args.output, current.strftime('%Y'), current.strftime('%m'))
            
            try:
                df = f.fetch_historical(ds)
                if df is not None and not df.empty:
                    os.makedirs(folder, exist_ok=True)
                    df.to_csv(os.path.join(folder, f"constituents-{f.code}.csv"), index=False)
                    df.to_json(os.path.join(folder, f"constituents-{f.code}.json"), orient='records')
                    print(f"[{f.code}] Saved {ds}")
                else:
                    print(f"[{f.code}] No data for {ds}, skipping.")
            except Exception as e:
                print(f"[{f.code}] Error {ds}: {e}")
            
            current += relativedelta(months=1)
            time.sleep(random.uniform(0.5, 1.5))

if __name__ == '__main__':
    main()
