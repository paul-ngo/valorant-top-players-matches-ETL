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
            
        return results
    
    except Exception as e:
        print(e)



def insertRds(statement: str, val: list):
        try:
            with connectRds() as connection:
                cur = connection.cursor()
                cur.executemany(statement, val)
                connection.commit()
            print(str(cur.rowcount) + ' records inserted.')
            
        except Exception as e:
            print(e)
            
def updateRds(statement: str):
    try:
        with connectRds() as connection:
            cur = connection.cursor()
            cur.execute(statement)
            connection.commit()
        print(str(cur.rowcount) + 'records updated.')
    except Exception as e:
        print(e)

            