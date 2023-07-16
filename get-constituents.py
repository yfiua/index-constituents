#!/usr/bin/env python3
# coding: utf-8

import pandas as pd
import requests

from selectorlib import Extractor

def convert_symbol(symbol):
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

    df['Symbol'] = df['Symbol'].apply(convert_symbol)

    return df

def get_constituents_csi300():
    url = 'https://wglh.com/ChinaIndicesCon/SH000300/'
    return get_constituents_from_wglh(url)

if __name__ == '__main__':
    df = get_constituents_csi300()
    df.to_csv('docs/constituents-csi300.csv', index=False)
    df.to_json('docs/constituents-csi300.json', orient='records')

