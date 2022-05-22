import redshift_connector as dbConn
import configparser
import os

def connectRedshift():
    parser = configparser.ConfigParser()
    parser.read('redshift.creds')
    config = 'redshift'
    iam = parser.get(config, 'iam')
    user = parser.get(config, 'user')
    password = parser.get(config, 'password')    
    database = parser.get(config, 'database')
    db_user = parser.get(config, 'db_user')
    cluster_identifier = parser.get(config, 'cluster_identifier')


    connection = dbConn.connect(
        iam=iam,
        database=database,
        db_user=db_user,
        user=user,
        password=password,
        cluster_identifier=cluster_identifier,
        access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        session_token=os.environ['AWS_SESSION_TOKEN'],
        region=os.environ['AWS_REGION']
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

            