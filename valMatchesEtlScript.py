import valMatchesEtlLibs as m
import s3fs
from connectRds import queryRds, insertRds
import pandas as pd

query1 = """select player_id, player_name
                from test_top_players, (SELECT max(date_added) as latest FROM test_top_players) as t
                where t.latest = test_top_players.date_added
                order by player_rank"""
dfPlayerList = pd.DataFrame(queryRds(query1), columns=['player_id', 'player_name'])

dfMatchesId = m.scrapeMatchesHistory(dfPlayerList['player_id'], dfPlayerList['player_name'])

query2 = """
    SELECT match_id b
    FROM matches
"""
dfExistingMatches = pd.DataFrame(queryRds(query2), columns=['match_id'])

dfMatchesId = dfMatchesId[~dfMatchesId['MATCH_ID'].isin(dfExistingMatches['match_id'])]

insert1 = """
    INSERT INTO matches (match_id, act_id, mode, match_url) VALUES (%s, %s, %s, %s)
"""
val1 = list(dfMatchesId.itertuples(index=False, name=None))
insertRds(insert1, val1)


dfMatchesDetails = m.scrapeTeams(dfMatchesId['MATCH_ID'])

insert2 = """
    INSERT INTO matches_details (match_id, map, red_team, red_team_score, blue_team, blue_team_score) VALUES (%s, %s, %s, %s, %s, %s)
"""
val2 = list(dfMatchesDetails.itertuples(index=False, name=None))
insertRds(insert2, val2)
