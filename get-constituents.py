#!/usr/bin/env python3
# coding: utf-8

import pandas as pd
import random
import requests
import sys
import time
from io import StringIO
from selectorlib import Extractor
from fake_useragent import UserAgent

ua = UserAgent()
n_retries = 5

# --- Parsers ---

def get_constituents_from_csindex(url, headers=None):
    def convert_symbol_csindex(symbol):
        match symbol[0]:
            case '0' | '3': return symbol + '.SZ'
            case '6': return symbol + '.SS'
            case '4' | '8': return symbol + '.BJ'
        return symbol

    r = requests.get(url, headers=headers)
    r.raise_for_status()
    df = pd.read_excel(r.content, dtype=str)
    
    # Handle potentially garbled or translated headers
    cols = df.columns
    sym_idx, name_idx = 0, 1
    for i, col in enumerate(cols):
        if 'Constituent Code' in col or '证券代码' in col or '成份券代码' in col:
            sym_idx = i
        if 'Constituent Name' in col or '证券简称' in col or '成份券名称' in col:
            name_idx = i
            
    df = df.iloc[:, [sym_idx, name_idx]]
    df.columns = ['Symbol', 'Name']
    df['Symbol'] = df['Symbol'].apply(convert_symbol_csindex)
    return df

def get_constituents_from_slickcharts(url, headers=None):
    selector_yml = '''
                    Symbol:
                        css: 'div.col-lg-7 tr td:nth-of-type(3) a'
                        multiple: true
                        type: Text
                    Name:
                        css: 'div.col-lg-7 tr td:nth-of-type(2) a'
                        multiple: true
                        type: Text
                   '''
    e = Extractor.from_yaml_string(selector_yml)
    if not headers: headers = { 'User-Agent' : ua.random }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = e.extract(r.text)
    return pd.DataFrame(data)

def get_constituents_from_bloomberg(url, headers=None, converter=None):
    selector_yml = '''
                    Symbol:
                        css: 'div.security-summary a.security-summary__ticker'
                        multiple: true
                        type: Text
                    Name:
                        css: 'div.security-summary a.security-summary__name'
                        multiple: true
                        type: Text
                   '''
    e = Extractor.from_yaml_string(selector_yml)
    if not headers: headers = { 'User-Agent' : ua.random }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = e.extract(r.text)
    df = pd.DataFrame(data)
    if converter:
        df['Symbol'] = df['Symbol'].apply(converter)
    return df

def get_constituents_from_wikipedia(url, headers=None, suffix=''):
    if not headers: headers = { 'User-Agent' : 'Mozilla/5.0' }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    tables = pd.read_html(StringIO(r.text))
    
    for t in tables:
        cols = [c.lower() for c in t.columns]
        sym_col = next((c for c in t.columns if c.lower() in ['ticker', 'symbol', 'code']), None)
        name_col = next((c for c in t.columns if c.lower() in ['company', 'security', 'company name']), None)
        
        if sym_col and name_col:
            df = t[[sym_col, name_col]].copy()
            df.columns = ['Symbol', 'Name']
            if suffix:
                df['Symbol'] = df['Symbol'].astype(str) + suffix
            return df
    raise ValueError(f"Could not find table on {url}")

# --- Index Logic ---

def fetch_and_save(name, fetch_func, filename):
    print(f'Fetching the constituents of {name}...')
    for i in range(n_retries):
        try:
            df = fetch_func()
            df.to_csv(f'docs/{filename}.csv', index=False)
            df.to_json(f'docs/{filename}.json', orient='records')
            return True
        except Exception as e:
            print(f'Attempt {i+1} failed: {e}')
            if i < n_retries - 1:
                time.sleep(random.paretovariate(2) * 5)
    return False

if __name__ == '__main__':
    status = 0
    
    # Bloomberg Indices
    indices_bloomberg = [
        ('DAX', lambda: get_constituents_from_bloomberg('https://www.bloomberg.com/quote/DAX:IND/members', converter=lambda s: s.replace(':GR', '.DE')), 'constituents-dax'),
        ('Hang Seng Index', lambda: get_constituents_from_bloomberg('https://www.bloomberg.com/quote/HSI:IND/members', converter=lambda s: s.rjust(7, '0').replace(':', '.')), 'constituents-hsi'),
        ('FTSE 100', lambda: get_constituents_from_bloomberg('https://www.bloomberg.com/quote/UKX:IND/members', converter=lambda s: s.replace(':LN', '.L')), 'constituents-ftse100'),
    ]

    for name, func, file in indices_bloomberg:
        if not fetch_and_save(name, func, file): status = 1
        time.sleep(random.paretovariate(2) * 5)

    # CSIndex / SZSE
    indices_china = [
        ('CSI 300', lambda: get_constituents_from_csindex('https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/cons/000300cons.xls'), 'constituents-csi300'),
        ('CSI 500', lambda: get_constituents_from_csindex('https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/cons/000500cons.xls'), 'constituents-csi500'),
        ('CSI 1000', lambda: get_constituents_from_csindex('https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/cons/000852cons.xls'), 'constituents-csi1000'),
        ('SSE', lambda: get_constituents_from_csindex('https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/cons/000001cons.xls'), 'constituents-sse'),
        ('SZSE', lambda: get_constituents_from_csindex('https://www.szse.cn/api/report/ShowReport?SHOWTYPE=xls&CATALOGID=1747_zs&ZSDM=399001'), 'constituents-szse'),
    ]

    for name, func, file in indices_china:
        if not fetch_and_save(name, func, file): status = 1

    # Slickcharts
    indices_slick = [
        ('NASDAQ 100', lambda: get_constituents_from_slickcharts('https://www.slickcharts.com/nasdaq100'), 'constituents-nasdaq100'),
        ('S&P 500', lambda: get_constituents_from_slickcharts('https://www.slickcharts.com/sp500'), 'constituents-sp500'),
        ('Dow Jones', lambda: get_constituents_from_slickcharts('https://www.slickcharts.com/dowjones'), 'constituents-dowjones'),
    ]

    for name, func, file in indices_slick:
        if not fetch_and_save(name, func, file): status = 1

    # Wikipedia
    indices_wiki = [
        ('IBEX 35', lambda: get_constituents_from_wikipedia('https://en.wikipedia.org/wiki/IBEX_35'), 'constituents-ibex35'),
        ('FTSE MIB', lambda: get_constituents_from_wikipedia('https://en.wikipedia.org/wiki/FTSE_MIB'), 'constituents-ftsemib'),
        ('NIFTY 50', lambda: get_constituents_from_wikipedia('https://en.wikipedia.org/wiki/NIFTY_50', suffix='.NS'), 'constituents-nifty50'),
        ('S&P/ASX 200', lambda: get_constituents_from_wikipedia('https://en.wikipedia.org/wiki/S%26P/ASX_200', suffix='.AX'), 'constituents-asx200'),
    ]

    for name, func, file in indices_wiki:
        if not fetch_and_save(name, func, file): status = 1

    print('Done.')
    sys.exit(status)
