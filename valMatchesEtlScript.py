import valMatchesEtlLibs as m
from connectRds import queryRds, insertRds
import pandas as pd

query1 = """
    SELECT player_id, player_name 
    FROM top_players 
    WHERE latest_data = 1
"""
dfPlayerList = pd.DataFrame(queryRds(query1), columns=['player_id', 'player_name'])

dfMatchesId = m.scrapeMatchesHistory(dfPlayerList['player_id'], dfPlayerList['player_name'])
dfMatchesId = dfMatchesId.drop_duplicates(subset=['match_id'])

query2 = """
    SELECT match_id
    FROM matches
"""
dfExistingMatches = pd.DataFrame(queryRds(query2), columns=['match_id'])

dfMatchesId = dfMatchesId[~dfMatchesId['match_id'].isin(dfExistingMatches['match_id'])]

insert1 = """
    INSERT INTO matches (match_id, act_id, mode, match_date, match_url) VALUES (%s, %s, %s, %s, %s)
"""
val1 = list(dfMatchesId.itertuples(index=False, name=None))
insertRds(insert1, val1)


dfMatchesDetails = m.scrapeTeams(dfMatchesId['match_id'])

insert2 = """
    INSERT INTO matches_details (match_id, map, red_team, red_team_score, blue_team, blue_team_score) VALUES (%s, %s, %s, %s, %s, %s)
"""
val2 = list(dfMatchesDetails.itertuples(index=False, name=None))
insertRds(insert2, val2)
