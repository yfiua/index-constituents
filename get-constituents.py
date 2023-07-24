#!/usr/bin/env python3
# coding: utf-8

import pandas as pd
import requests

from selectorlib import Extractor

def convert_symbol_wglh(symbol):
    return symbol + 'SS' if symbol[0] == '6' else symbol + 'SZ'

def get_constituents_from_wglh(url):
    selector_yml = '''
                    Symbol:
                        css: 'td small.text-secondary'
                        xpath: null
                        multiple: true
                        type: Text
                    Name:
                        css: 'tr td:nth-of-type(2) a'
                        xpath: null
                        multiple: true
                        type: Text
                   '''

    e = Extractor.from_yaml_string(selector_yml)

    headers = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36' }
    r = requests.get(url, headers=headers)

    data = e.extract(r.text)
    df = pd.DataFrame(data)

    df['Symbol'] = df['Symbol'].apply(convert_symbol_wglh)

    return df

def get_constituents_from_slickcharts(url):
    selector_yml = '''
                    Symbol:
                        css: 'tr td:nth-of-type(3) a'
                        xpath: null
                        multiple: true
                        type: Text
                    Name:
                        css: 'div.col-lg-7 tr td:nth-of-type(2) a'
                        xpath: null
                        multiple: true
                        type: Text
                   '''

    e = Extractor.from_yaml_string(selector_yml)

    headers = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36' }
    r = requests.get(url, headers=headers)

    data = e.extract(r.text)
    df = pd.DataFrame(data)

    return df

# 沪深300
def get_constituents_csi300():
    url = 'https://wglh.com/ChinaIndicesCon/SH000300/'
    return get_constituents_from_wglh(url)

# 上证指数
def get_constituents_sse():
    url = 'https://wglh.com/ChinaIndicesCon/SH000001/'
    return get_constituents_from_wglh(url)

# 深证成指
def get_constituents_szse():
    url = 'https://wglh.com/ChinaIndicesCon/SZ399001/'
    return get_constituents_from_wglh(url)

# NASDAQ100
def get_constituents_nasdaq100():
    url = 'https://www.slickcharts.com/nasdaq100'
    return get_constituents_from_slickcharts(url)

# S&P500
def get_constituents_sp500():
    url = 'https://www.slickcharts.com/sp500'
    return get_constituents_from_slickcharts(url)

# Dow Jones
def get_constituents_dowjones():
    url = 'https://www.slickcharts.com/dowjones'
    return get_constituents_from_slickcharts(url)

if __name__ == '__main__':
    print('Fetching the constituents of CSI 300...')
    try:
        df = get_constituents_csi300()
        df.to_csv('docs/constituents-csi300.csv', index=False)
        df.to_json('docs/constituents-csi300.json', orient='records')
    except:
        print('Failed to fetch the constituents of CSI 300.')

    print('Fetching the constituents of SSE...')
    try:
        df = get_constituents_sse()
        df.to_csv('docs/constituents-sse.csv', index=False)
        df.to_json('docs/constituents-sse.json', orient='records')
    except:
        print('Failed to fetch the constituents of SSE.')

    print('Fetching the constituents of SZSE...')
    try:
        df = get_constituents_szse()
        df.to_csv('docs/constituents-szse.csv', index=False)
        df.to_json('docs/constituents-szse.json', orient='records')
    except:
        print('Failed to fetch the constituents of SZSE.')

    print('Fetching the constituents of NASDAQ 100...')
    try:
        df = get_constituents_nasdaq100()
        df.to_csv('docs/constituents-nasdaq100.csv', index=False)
        df.to_json('docs/constituents-nasdaq100.json', orient='records')
    except:
        print('Failed to fetch the constituents of NASDAQ 100.')

    print('Fetching the constituents of S&P 500...')
    try:
        df = get_constituents_sp500()
        df.to_csv('docs/constituents-sp500.csv', index=False)
        df.to_json('docs/constituents-sp500.json', orient='records')
    except:
        print('Failed to fetch the constituents of S&P 500.')

    print('Fetching the constituents of Dow Jones...')
    try:
        df = get_constituents_dowjones()
        df.to_csv('docs/constituents-dowjones.csv', index=False)
        df.to_json('docs/constituents-dowjones.json', orient='records')
    except:
        print('Failed to fetch the constituents of Dow Jones.')

    print('Done.')

