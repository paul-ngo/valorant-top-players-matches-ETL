import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import datetime
import concurrent.futures
import threading
import math
import requests
import configparser

parser = configparser.ConfigParser()
parser.read("config.ini")
config = 'default'

playerCount = int(parser.get(config, 'playerCount'))
maxThreads = int(parser.get(config, 'maxThreads'))
headless = parser.get(config, 'headless')

class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        if self.name:
            print('[%s]' % self.name,)
        print('Elapsed: %s' % (time.time() - self.tstart))
        
class Driver():
    def __init__(self, headless):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        if headless:
            options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--no-zygote")
        options.add_argument("--single-process")
        options.add_argument("window-size=2560x1440")
        options.binary_location = '/usr/local/bin/chrome'
        self.driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=options)

    def __del__(self):
        self.driver.quit()
            
def get_driver(threadLocal, headless=True):
    the_driver = getattr(threadLocal, 'the_driver', None)
    if the_driver is None:
        the_driver = Driver(headless)
        setattr(threadLocal, 'the_driver', the_driver)
    return the_driver.driver

timeout = 3

def getTopPlayers(args):
    pages = args[0]
    n = args[1]
    threadLocal = args[2]
    
    driver = get_driver(threadLocal, headless)
    arrPlayers = []
    arrRanks = []
    for page in range(pages-n, pages):
        url = "https://playvalorant.com/en-us/leaderboards/?page=" + str(page+1)  
        driver.get(url)
        
        playerTileAttr = "LeaderboardsItem-module--playerName--2BYaw"
        playerRankAttr = "LeaderboardsItem-module--leaderboardRank--3DHty"
        
        try:
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, playerTileAttr)))
        except: 
            try:
                print('Error encountered...trying again')
                driver.refresh()        
                WebDriverWait(driver, timeout*2).until(EC.presence_of_element_located((By.CLASS_NAME, playerTileAttr)))
            except:
                print('Error encountered on page ' + str(page))
                continue
            
        actIdRev = driver.current_url[::-1]
        actId = actIdRev[0:(actIdRev.find('='))][::-1]
            
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')   

        lsPlayers = []
        lsPlayers = soup.find_all("h2", {"class": playerTileAttr})
        lsRanks = soup.find_all("h3", {"class": playerRankAttr})
        
        for rank, player in zip(lsRanks, lsPlayers):
            arrRanks = np.append(arrRanks, rank.text.replace("#", "-"))
            arrPlayers = np.append(arrPlayers, player.text.replace("#", "-"))

    arrPlayerNames = []
    arrPlayerRanks = []
    arrPlayerIds = []
       
    for playerName, playerRank in zip(arrPlayers, arrRanks):
        url = 'https://valorant.iesdev.com/player/' + playerName.lower()
        r = requests.get(url)
        
        if r.status_code == 404:
            continue
        
        playerData = r.json()
        playerId = playerData['id'] or playerData['puuid']
        arrPlayerNames = np.append(arrPlayerNames, playerName)
        arrPlayerRanks = np.append(arrPlayerRanks, playerRank)
        arrPlayerIds = np.append(arrPlayerIds, playerId)
    
    
    del threadLocal
    return arrPlayerNames, arrPlayerRanks, arrPlayerIds, actId

def scrapePlayers():
    pageCount = math.ceil(playerCount/10)
    n = math.ceil(pageCount/maxThreads)

    arrPlayerNames = []
    arrPlayerRanks = []
    arrPlayerIds = []
    
    with Timer('Leaderboard Scrape:'):

        args = [(n*i, n, threading.local()) for i in range(1, maxThreads+1)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=maxThreads) as executor:
            results = executor.map(getTopPlayers, args)

            for result in results:
                arrPlayerNames = np.append(arrPlayerNames, result[0])
                arrPlayerRanks = np.append(arrPlayerRanks, result[1])    
                arrPlayerIds = np.append(arrPlayerIds, result[2]) 
                
            actId = result[3]
            
            dfPlayerList = pd.DataFrame(data=[arrPlayerIds, arrPlayerRanks, arrPlayerNames]).T
            dfPlayerList.columns = ['player_id', 'player_rank', 'player_name']
            dfPlayerList['act_id'] = actId
            dfPlayerList['date_added'] = datetime.datetime.now()
            dfPlayerList['latest_data'] = True

    return dfPlayerList
  