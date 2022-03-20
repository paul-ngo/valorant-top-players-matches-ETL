# VALORANT Top Players and Matches ETL
This project is to scrape the latest top players from Riot's Valorant leaderboard website and extract their matches data from Blitz.gg. The data is transformed and loaded to an AWS RDS database via Python scripts. 

Planned next steps:

-Move data directly to Redshift data warehouse since the data is being batch processed anyways

-Setup automated analytics for the data

-Improve table schemas by creating tables to map fields (e.g. agents, map, team comp)

-Explore data streaming implementation

-Explore Pyspark implementation


The Python libraries Selenium and BeauitfulSoup are used to facilitate scraping. Numpy and Pandas are used to process and transform the data. Pymysql is used to connect and query the RDS database. Concurrency is used to improve runtimes; loading the webpage takes the most time, so opening multiple webpages in parallel significantly reduces runtime with improved context switching.

Leaderboard: https://playvalorant.com/en-us/leaderboards/?page=1
