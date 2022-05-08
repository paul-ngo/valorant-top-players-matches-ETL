import valMatchesEtlLibs as m
from connectRedshift import queryRedshift, insertRedshift
import pandas as pd

query1 = """
    SELECT player_id, player_name, act_id
    FROM top_players 
    WHERE latest_data = 1
"""
dfPlayerList = pd.DataFrame(queryRedshift(query1), columns=['player_id', 'player_name', 'act_id'])

dfMatchesId = m.scrapeMatchesHistory(dfPlayerList['player_id'], dfPlayerList['player_name'], dfPlayerList['act_id'])
dfMatchesId = dfMatchesId.drop_duplicates(subset=['match_id'])

query2 = """
    SELECT match_id
    FROM matches
"""
dfExistingMatches = pd.DataFrame(queryRedshift(query2), columns=['match_id'])

dfNewMatchesId = dfMatchesId[~dfMatchesId['match_id'].isin(dfExistingMatches['match_id'])]

query3 = """
    SELECT match_id
    FROM matches_details
"""
## cross-check match IDs in the matches_details tables incase script failed to retrive match details previously
dfExistingMatchesDetails = pd.DataFrame(queryRedshift(query3), columns=['match_id'])
dfNewMatchesWithoutDetails = dfMatchesId[~dfMatchesId['match_id'].isin(dfExistingMatchesDetails['match_id'])]

dfNewMatchesDetails = m.scrapeTeams(dfNewMatchesWithoutDetails['match_id'])

insert1 = """
    INSERT INTO matches (match_id, act_id, mode, match_date, match_url) VALUES (%s, %s, %s, %s, %s)
"""
val1 = list(dfNewMatchesId.itertuples(index=False, name=None))
insertRedshift(insert1, val1)

insert2 = """
    INSERT INTO matches_details (match_id, map, red_team, red_team_score, blue_team, blue_team_score) VALUES (%s, %s, %s, %s, %s, %s)
"""
val2 = list(dfNewMatchesDetails.itertuples(index=False, name=None))
insertRedshift(insert2, val2)