# index-constituents

[![update-monthly](https://github.com/yfiua/index-constituents/workflows/update-monthly/badge.svg)](https://github.com/yfiua/index-constituents/actions?query=workflow:%22update-monthly%22)

Get the current and historical constituents of popular stock indices.
All symbols are consistent with those in [Yahoo Finance](https://finance.yahoo.com/).

## Supported indices


| Code      |  Name             |  Start   | Download                                                                                                                                                      |
|:----------|:------------------|:---------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| csi300    | CSI 300 (沪深300) | 2023/07  | [json](https://yfiua.github.io/index-constituents/constituents-csi300.json) / [csv](https://yfiua.github.io/index-constituents/constituents-csi300.csv)       |
| sse       | SSE (上证综指)    | 2023/07  | [json](https://yfiua.github.io/index-constituents/constituents-sse.json) / [csv](https://yfiua.github.io/index-constituents/constituents-sse.csv)             |
| szse      | SZSE (深证成指)   | 2023/07  | [json](https://yfiua.github.io/index-constituents/constituents-szse.json) / [csv](https://yfiua.github.io/index-constituents/constituents-szse.csv)           |
| nasdaq100 | NASDAQ 100        | 2023/07  | [json](https://yfiua.github.io/index-constituents/constituents-nasdaq100.json) / [csv](https://yfiua.github.io/index-constituents/constituents-nasdaq100.csv) |
| sp500     | S&P 500           | 2023/07  | [json](https://yfiua.github.io/index-constituents/constituents-sp500.json) / [csv](https://yfiua.github.io/index-constituents/constituents-sp500.csv)         |
| dowjones  | Dow Jones         | 2023/07  | [json](https://yfiua.github.io/index-constituents/constituents-dowjones.json) / [csv](https://yfiua.github.io/index-constituents/constituents-dowjones.csv)   |
| dax       | DAX               | 2023/07  | [json](https://yfiua.github.io/index-constituents/constituents-dax.json) / [csv](https://yfiua.github.io/index-constituents/constituents-dax.csv)             |
| hsi       | HSI (恒生指数)    | 2023/07  | [json](https://yfiua.github.io/index-constituents/constituents-hsi.json) / [csv](https://yfiua.github.io/index-constituents/constituents-hsi.csv)             |
| ftse100   | FTSE 100          | 2023/07  | [json](https://yfiua.github.io/index-constituents/constituents-ftse100.json) / [csv](https://yfiua.github.io/index-constituents/constituents-ftse100.csv)     |

## Usage
### Direct download
To get the current index constituents, use the links above. You probably have noticed the URLs have some pattern:

```sh
wget https://yfiua.github.io/index-constituents/constituents-$CODE.$FORMAT
```

### Use in your program
Using Python as an example:

```python
import pandas as pd

url = "https://yfiua.github.io/index-constituents/constituents-csi300.csv"
df = pd.read_csv(url)
```

### Build yourself
Check `requirements.txt`. Run:

```sh
./get-constituents.py
```

## Historical data
To get the historical index constituents, use the following URL:

```sh
https://yfiua.github.io/index-constituents/$YYYY/$MM/constituents-$CODE.$FORMAT
```

By default we automatically update the data monthly (usually on the first day).
Historical data of a particular index is only available from the month we start to include it.

## Data source
* [乌龟量化](https://wglh.com/)
* [Slickcharts](https://www.slickcharts.com/)
* [Bloomberg](https://www.bloomberg.com/)

## Author
* [Yfiua](https://github.com/yfiua)
