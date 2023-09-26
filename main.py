from scraping import scrape
from flask import Flask

app = Flask(__name__)

@app.route('/', methods=['GET'])
def run():
    url = "https://yyzopen.calicotab.com/to23/" # input("Enter the URL: ")
    team_name = "EEC 15" # input("Enter the team name: ")
    my_name = "Terrence Zhu" # input("Enter the participant name: ")
    data = scrape(url, team_name, my_name)
    return data
