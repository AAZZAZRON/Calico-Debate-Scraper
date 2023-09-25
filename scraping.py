from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)

def click_on_nav(url, text):
    driver.get(url)
    nav_bar = driver.find_element(By.XPATH, '//ul[contains(@class, "navbar-nav")]')

    # Go to the team tab
    team_tab = nav_bar.find_element(By.XPATH, f'//a[contains(text(), "{text}")]')
    team_tab.click()


def get_debate_rounds(team_name):
    team = driver.find_element(By.XPATH, f'//span[@class="tooltip-trigger" and contains(., "{team_name}")]/ancestor::tr')
    cols = team.find_elements(By.XPATH, './/td')
    debate_rounds = []
    for col in cols:
        round = col.find_elements(By.XPATH, f'.//div[@role="tooltip" and @class="popover bs-popover-bottom"]')
        if round:
            round = round[0]
            placement = round.find_element(By.XPATH, './/h6[@class="flex-grow-1"]').get_attribute("innerText").replace("Placed ", "")
            teams = round.find_elements(By.XPATH, './/div[@class="list-group-item"]')[0].get_attribute("innerText")
            # print(repr(teams))
            teams = teams.split(":")
            if len(teams) == 1:
                names = teams[0].split(", ")
                print(names)
            else:
                curr_round = []
                teams = teams[1].split(")")
                for opp in teams[:-1]:
                    name, pos = opp.split(" (")
                    curr_round.append((name, pos))
                debate_rounds.append((placement, curr_round))
            # print(teams)
            
            # print(placement, teams)
    return debate_rounds


def scrape(url, team_name):
    click_on_nav(url, "Team Tab")
    rounds = get_debate_rounds(team_name)
    print(rounds)

    driver.quit()
