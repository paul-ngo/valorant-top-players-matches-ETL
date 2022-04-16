import redshift_connector as dbConn
import configparser

def connectRedshift():
    parser = configparser.ConfigParser()
    parser.read('redshift.creds')
    config = 'redshift'
    iam = True
    user = parser.get(config, 'user')
    database = parser.get(config, 'database')
    cluster_identifier = parser.get(config, 'cluster_identifier')
    profile = parser.get(config, 'profile')
    
    connection = dbConn.connect(    
        iam=True,
        database='dev',
        db_user='awsuser',
        password='',
        user='',
        cluster_identifier=cluster_identifier,
        profile='default'
        )

    return connection

def queryRedshift(query: str) -> tuple:
    try:
        with connectRedshift() as connection:
            cur = connection.cursor()
            cur.execute(query)
            results = cur.fetchall()
            
        return results
    
    except Exception as e:
        print(e)


def insertRedshift(statement: str, val: list):
        try:
            with connectRedshift() as connection:
                cur = connection.cursor()
                cur.executemany(statement, val)
                connection.commit()
            print(str(cur.rowcount) + ' records inserted.')
            
        except Exception as e:
            print(e)
            
def updateRedshift(statement: str):
    try:
        with connectRedshift() as connection:
            cur = connection.cursor()
            cur.execute(statement)
            connection.commit()
        print(str(cur.rowcount) + ' records updated.')
    except Exception as e:
        print(e)

            