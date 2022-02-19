import valScraperLibs as v
import s3fs
import os
from datetime import datetime
import pandas as pd
import configparser

parser = configparser.ConfigParser()
parser.read("valscraper_config.txt")

playerCount = int(parser.get('config', 'playerCount'))
maxThreads = int(parser.get('config', 'maxThreads'))
headless = parser.get('config', 'headless')
actId = parser.get('config', 'actId')

dfPlayerList = v.scrapePlayers(actId, playerCount, maxThreads, headless)

bPlayerList = dfPlayerList.to_csv(None, index=False).encode()

fs = s3fs.S3FileSystem()
bucket = parser.get('config', 'bucket')
folder = parser.get('config', 'folder')
filename = parser.get('config', 'filename')

with fs.open('s3://{}/{}/{}.csv'.format(bucket, folder, filename), 'wb') as f:
    f.write(bPlayerList)
