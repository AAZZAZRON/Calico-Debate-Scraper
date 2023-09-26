# Calico-Debate-Scraper
Scrapes Calico Debate Tournament Tabs

Calicotab is a website that hosts debate tournament results. This program scrapes the website for speaker and team scores and compares them to tournament averages. 

My brother wanted to compare his team and personal scores to the rest of the tournament, but calicotab did not have a way to do this. I wrote this program so he didn't have to spend an hour after each debate tournament manually finding and adding up numbers.  

## Usage
`python -m venv venv` to create a virtual environment

`venv/scripts/activate` to activate the virtual environment

`pip install -r requirements.txt` to install dependencies, namely selenium

`python main.py` to run the program

Data should be outputted to console and also in `out.csv`