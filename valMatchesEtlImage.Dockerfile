FROM python:latest
WORKDIR /app
COPY requirements.txt/ .
COPY config.ini/ . 
COPY redshift.creds/ .
COPY connectRedshift.py/ .
COPY dict_agents.json/ .
COPY valMatchesEtlLibs.py/ .
COPY valMatchesEtlScript.py/ .

# install python libraries
RUN pip install -r requirements.txt

CMD [ "python", "-m", "valMatchesEtlScript"]