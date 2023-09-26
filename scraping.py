from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)

def click_on_nav(text):
    nav_bar = driver.find_element(By.XPATH, '//ul[contains(@class, "navbar-nav")]')

    # Go to the team tab
    team_tab = nav_bar.find_element(By.XPATH, f'//a[contains(text(), "{text}")]')
    team_tab.click()


def get_opponents(team_name):
    team = driver.find_element(By.XPATH, f'//span[@class="tooltip-trigger" and contains(., "{team_name}")]/ancestor::tr')
    cols = team.find_elements(By.XPATH, './/td')
    my_stats = []
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
                # print(names)
            else:
                score = round.find_elements(By.XPATH, './/div[@class="list-group-item"]')[1].get_attribute("innerText").split(": ")[1]  # TODO: fix this lol
                my_pos = ""
                curr_round = []
                teams = teams[1].split(")")
                for opp in teams[:-1]:
                    name, pos = opp.split(" (")
                    if name == team_name:
                        my_pos = pos
                    curr_round.append(name)
                my_stats.append((placement, my_pos, score))
                debate_rounds.append(curr_round)
    return my_stats, debate_rounds


def get_teams_position(team_name, col):
    popup = col.find_element(By.XPATH, './/div[@role="tooltip" and @class="popover bs-popover-bottom"]')
    teams = popup.find_elements(By.XPATH, './/div[@class="list-group-item"]')[0].get_attribute("innerText").split("Teams in debate:")[1].split(")")[:-1]
    for team in teams:
        name, pos = team.split(" (")
        if name == team_name:
            return pos


def get_teams_placement_points(col):
    points = {"1st": 3, "2nd": 2, "3rd": 1, "4th": 0}
    popup = col.find_element(By.XPATH, './/div[@role="tooltip" and @class="popover bs-popover-bottom"]')
    placement = popup.find_element(By.XPATH, './/h6[@class="flex-grow-1"]').get_attribute("innerText").replace("Placed ", "")
    return points[placement]


def get_tourney_scores_points_stats(teams, positions, num_rounds):
    print(positions)
    tourney_scores = [0] * num_rounds  # average speaker score per round for the tournament
    position_scores = [0] * num_rounds # average speaker score per round for the position in question
    room_scores = [0] * num_rounds     # average speaker score per round for the room in question
    avg_points = [0] * num_rounds      # average points per round of the position in question for the tournament

    tot_debate_teams = [0] * num_rounds
    table = driver.find_element(By.XPATH, '//table[@class="table"]').find_element(By.XPATH, './/tbody').find_elements(By.XPATH, './/tr')
    for row in table:  # children of the table
        cols = row.find_elements(By.XPATH, './/td')
        name = cols[1].find_element(By.XPATH, './/span[@class="tooltip-trigger"]').get_attribute("innerText")
        # print(name)
        for round in range(num_rounds):
            score = cols[3 + round].find_elements(By.XPATH, './/small')
            if not score:  # if no score, skip
                continue
            score = int(score[0].get_attribute("innerText"))
            if name in teams and round in teams[name]:
                room_scores[round] += score
            tourney_scores[round] += score

            if get_teams_position(name, cols[3 + round]) == positions[round]:
                # print(round, positions[round], name)
                position_scores[round] += score
                avg_points[round] += get_teams_placement_points(cols[3 + round])
            tot_debate_teams[round] += 1

    for i in range(num_rounds):
        tourney_scores[i] /= tot_debate_teams[i] * 2
        position_scores[i] /= (tot_debate_teams[i] / 4) * 2
        room_scores[i] /= 8
        avg_points[i] /= tot_debate_teams[i] / 4

    return tourney_scores, position_scores, room_scores, avg_points


def get_my_speaker_scores(my_name, num_rounds):
    my_row = driver.find_element(By.XPATH, f'//span[@class="tooltip-trigger" and contains(., "{my_name}")]/ancestor::tr')
    cols = my_row.find_elements(By.XPATH, './/td')
    my_scores = [-1] * num_rounds
    for round in range(num_rounds):
        score = cols[4 + round].find_elements(By.XPATH, './/span[@class="tooltip-trigger"]')
        if not score:
            continue
        my_scores[round] = int(score[0].get_attribute("innerText"))
    return my_scores


def scrape(url, team_name, my_name):
    driver.get(url)
    click_on_nav("Team Tab")
    my_stats, rounds = get_opponents(team_name)
    print(my_stats)
    # [print(round) for round in rounds]
    faced = {}
    for round, round_num in zip(rounds, range(len(rounds))):
        for team in round:
            if team in faced:
                faced[team].append(round_num)
            else:
                faced[team] = [round_num]

    # print(faced)
    # tourney_scores, position_scores, round_scores, avg_points = get_tourney_scores_points_stats(faced, [x[1] for x in my_stats], len(rounds))
    # print(tourney_scores)
    # print(position_scores)
    # print(round_scores)
    # print(avg_points)

    # Get participant speaker scores
    click_on_nav("Speaker Tab")
    my_scores = get_my_speaker_scores(my_name, len(rounds))
    print(my_scores)

    driver.quit()
