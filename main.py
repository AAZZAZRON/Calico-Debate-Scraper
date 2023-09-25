from scraping import scrape
from flask import Flask

app = Flask(__name__)

@app.route('/', methods=['GET'])
def run():
    url = "https://yyzopen.calicotab.com/to23/" # input("Enter the URL: ")
    team_name = "EEC 15" # input("Enter the team name: ")
    scrape(url, team_name)
    return "Success"
