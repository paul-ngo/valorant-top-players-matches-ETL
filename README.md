# valorant
This project is to scrape the latest top players from Riot's Valorant leaderboard website. The data is processed and sent to an AWS S3 bucket. 

The Python libraries Selenium and BeauitfulSoup are used to facilitate scraping. Numpy and Pandas are used to process the data. Concurrency is used to improve runtimes; loading the webpage takes the most time, so opening multiple webpages in parallel significantly reduces runtime with improved context switching.

Leaderboard: https://playvalorant.com/en-us/leaderboards/?page=1
