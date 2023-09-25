from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def scrape(url, team_name):
    chrome_options = Options()

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    nav_bar = driver.find_element(By.XPATH, '//ul[contains(@class, "navbar-nav")]')
    print(nav_bar.text)

    # Go to the team tab
    team_tab = nav_bar.find_element(By.XPATH, '//a[contains(text(), "Team Tab")]')
    team_tab.click()

    # get the team
    team = driver.find_element(By.XPATH, f'//span[@class="tooltip-trigger" and contains(., "{team_name}")]/ancestor::tr')
    cols = team.find_elements(By.XPATH, './/td')
    for col in cols:
        round = col.find_elements(By.XPATH, f'.//div[@role="tooltip" and @class="popover bs-popover-bottom"]')
        if round:
            round = round[0]
            placement = round.find_element(By.XPATH, './/h6[@class="flex-grow-1"]').get_attribute("innerText").replace("Placed ", "")
            teams = round.find_elements(By.XPATH, './/div[@class="list-group-item"]')[0]
            print(placement, teams.get_attribute("innerText"))


    # driver.quit()
