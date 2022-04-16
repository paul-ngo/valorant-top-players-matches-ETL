import numpy as np
import pandas as pd
import time
import concurrent.futures
import requests
import json
import math
import configparser
from dateutil import parser as dateparser

# combine match and match_details tables?
# add date_added datetimes for matches and match_details

parser = configparser.ConfigParser()
parser.read('config.ini')
config = 'default'

maxThreads = int(parser.get(config, 'maxThreads'))
# actId = parser.get(config, 'actId')
queue = parser.get(config, 'queue')
maxMatchCount = int(parser.get(config, 'minMatchCount'))
headless = parser.get(config, 'headless')

with open('dict_agents.json') as f:
    dictAgents = json.load(f)

class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        if self.name:
            print('[%s]' % self.name,)
        print('Elapsed: %s' % (time.time() - self.tstart))

def getPlayerMatches(args):
    
    arrPlayerIds = args[0]
    arrPlayers = args[1]
    actId = args[2]
    
    dfMatchesIds = pd.DataFrame()

    for (playerId, playerName, actId) in zip(arrPlayerIds, arrPlayers, actId):
        for offset in range(0, maxMatchCount, 20):
            url = 'https://valorant.iesdev.com/matchplayer/' + playerId + '?offset=' + str(offset) + '&queues=' + queue + ',&type=subject&updatedMPs=true&actId=' + actId
            
            try: 
                r = requests.get(url)
    
                if '500 Internal Server Error' in r.text:
                    r = requests.get(url)
                
                if r.text == '[]':
                    break
                
                matchesData = r.json()
                parsedData = [(match['matchId'], actId, match['queue'].upper(), dateparser.parse(match['matchDate'], ignoretz=True)) for match in matchesData]
                dfMatchId = pd.DataFrame(data = parsedData, columns = ['match_id', 'act_id', 'mode', 'match_date'])
                dfMatchId['match_url'] = 'https://blitz.gg/valorant/match/' + playerName + '/' + actId + '/' + dfMatchId['match_id']
                dfMatchesIds = pd.concat([dfMatchesIds, dfMatchId])
            except Exception as e:
                print('Error with the request to: ' + url)
                # print(e)
                continue
            
    return dfMatchesIds

def getMatchTeams(args):
    matchesIds = args
    dfMatchesDetails = pd.DataFrame()
    for matchId in matchesIds:
        
        try:
            try: 
                url = 'https://valorant.iesdev.com/match/' + matchId + '?type=puuid'
                r = requests.get(url)
                
                matchData = r.json()
                
            except:
                url = 'https://valorant.iesdev.com/match/' + matchId
                r = requests.get(url)
                
                matchData = r.json()
            
            if r.status_code == 404:
                print('Response error 404')
                continue
            
            arrplayers = matchData['players']
            map_ =  matchData['map'].upper()
            redTeam = []
            blueTeam = []
            
            for agent in arrplayers:
                if agent['teamId'] == 'Red':
                    redTeam = np.append(redTeam, dictAgents[agent['characterId']])
                else:
                    blueTeam = np.append(blueTeam, dictAgents[agent['characterId']])
            redTeamKey = "-".join((np.sort(redTeam)))
            blueTeamKey = "-".join((np.sort(blueTeam)))
            redTeamScore = matchData['teams'][0]['roundsWon']
            blueTeamScore = matchData['teams'][1]['roundsWon']
            
            dfMatchDetails = pd.DataFrame(data = [[matchId, map_, redTeamKey, redTeamScore, blueTeamKey, blueTeamScore]], columns = ['MATCH_ID', 'MAP', 'RED_TEAM', 'RED_TEAM_SCORE', 'BLUE_TEAM', 'BLUE_TEAM_SCORE'])
            dfMatchesDetails = pd.concat([dfMatchesDetails, dfMatchDetails])
            
        except Exception as e:
            # print(e)
            continue
        
    return dfMatchesDetails  

def scrapeMatchesHistory(arrPlayerIds, arrPlayerNames, actId):
    dfMatchesIds = pd.DataFrame()
    n = math.ceil(len(arrPlayerIds)/maxThreads)
    
    with Timer('Matches scraping'):
        try:
            args = [(arrPlayerIds[i:i+n], arrPlayerNames[i:i+n], actId[i:i+n]) for i in range(0, len(arrPlayerIds), n)]
            
            print('Scraping match history...')
            with concurrent.futures.ThreadPoolExecutor(max_workers=maxThreads) as executor:
                results = executor.map(getPlayerMatches, args)
    
                for result in results:
                    dfMatchesIds = pd.concat([dfMatchesIds, result])
                
                dfMatchesIds = dfMatchesIds[dfMatchesIds['mode']=='COMPETITIVE']
                dfMatchesIds = dfMatchesIds.drop_duplicates(['match_id'])
                dfMatchesIds = dfMatchesIds.reset_index(drop=True)
                return dfMatchesIds
            
        except:
            print('Error encountered')
            return
        
        
def scrapeTeams(matchesIds):
    with Timer('Team scraping:'):
        dfMatchesTeams = pd.DataFrame()
        n = math.ceil(len(matchesIds)/maxThreads)
        try: 
            args = [(matchesIds[i:i+n]) for i in range(0, len(matchesIds), n)]
            print('Scraping match details...')
            with concurrent.futures.ThreadPoolExecutor(max_workers=maxThreads) as executor:
                results = executor.map(getMatchTeams, args)
                
                for result in results:
                    dfMatchesTeams = pd.concat([dfMatchesTeams, result])
    
                return dfMatchesTeams
        except:
            print('Error encountered')
            return 