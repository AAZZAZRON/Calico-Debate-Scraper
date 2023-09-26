from scraping import scrape
from write_to_csv import write_to_csv


if __name__ == "__main__":
    url = input("Enter the URL: ") # "https://yyzopen.calicotab.com/to23/" 
    team_name = input("Enter the team name: ") # "EEC 15"
    my_name = input("Enter the participant name: ") # "Terrence Zhu" 
    data = scrape(url, team_name, my_name)

    write_to_csv(data)

    # output to console
    with open("out.csv", "r") as file:
        csv = file.readlines()
    for line in csv:
        print(line, end="")
