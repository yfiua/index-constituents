#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

# params
file_formats = ['json', 'csv']

# read the csv file into a dataframe
df = pd.read_csv('supported-indices.csv')

# generate string of download links
def gen_download_links(code, file_formats):
    str_download = ''
    for file_format in file_formats:
        url = f'https://yfiua.github.io/index-constituents/constituents-{code}.{file_format}'
        str_download += f'[{file_format}]({url}) / '

    return str_download[:-3]

# for each row in the dataframe generate string of download links
df['Download'] = df.apply(lambda row: gen_download_links(row['Code'], file_formats), axis=1)

print(df.to_markdown(index=False))
