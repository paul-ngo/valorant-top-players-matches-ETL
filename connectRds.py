import pymysql
import configparser

def connectRds():
    parser = configparser.ConfigParser()
    parser.read('rds.creds')
    config = 'maria-db'
    host = parser.get(config, 'host')
    user = parser.get(config, 'user')
    password = parser.get(config, 'password')
    port = int(parser.get(config, 'port'))
    database = parser.get(config, 'database')
    
    connection = pymysql.connect(host=host, user=user, password=password, port=port, database=database)
    return connection

def queryRds(query: str) -> tuple:
    try:
        with connectRds() as connection:
            cur = connection.cursor()
            cur.execute(query)
            results = cur.fetchall()
    except:
        print('Failed query.')
    return results


def insertRds(statement: str, val: list):
    with connectRds() as connection:
        cur = connection.cursor()
       
        try:
            cur.executemany(statement, val)
            connection.commit()
            print(str(cur.rowcount) + ' rows inserted.')
        except Exception as e:
            print(e) #'Failed insert.'
            