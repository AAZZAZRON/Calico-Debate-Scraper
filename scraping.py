from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


driver = None
col_round_start = -1

def init():
    global driver
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

'''
Clicks on the nav bar to go to another tab
'''
def click_on_nav(tab_text):
    nav_bar = driver.find_element(By.XPATH, '//ul[contains(@class, "navbar-nav")]')

    # Go to the team tab
    team_tab = nav_bar.find_element(By.XPATH, f'//a[contains(text(), "{tab_text}")]')
    team_tab.click()


'''
Gets the opponents the team faces per round
At the same time, gets the team's placement and score per round

@param {team_name} is the name of the team
@return {my_placements} is a list of the user's placements per round
@return {my_positions} is a list of the user's positions per round
@return {team_scores} is a list of the user's team's scores per round
@return {debate_rounds} is a list of lists, where each list is the teams in the user's room per round
'''
def get_opponents(team_name):
    global col_round_start
    
    team = driver.find_element(By.XPATH, f'//span[@class="tooltip-trigger" and contains(., "{team_name}")]/ancestor::tr')
    cols = team.find_elements(By.XPATH, './/td')
    my_placements = []  # placement per round
    my_positions = []   # position per round
    team_scores = []    # score per round
    debate_rounds = []
    for col, ind in zip(cols, range(len(cols))):
        round = col.find_elements(By.XPATH, f'.//div[@role="tooltip" and @class="popover bs-popover-bottom"]')
        if round:
            round = round[0]
            placement = round.find_element(By.XPATH, './/h6[@class="flex-grow-1"]').get_attribute("innerText").replace("Placed ", "")
            teams = round.find_elements(By.XPATH, './/div[@class="list-group-item"]')[0].get_attribute("innerText")
            # print(repr(teams))
            teams = teams.split(":")
            if len(teams) == 1:
                continue
            else:
                if col_round_start == -1:
                    col_round_start = ind
                score = round.find_elements(By.XPATH, './/div[@class="list-group-item"]')[1].get_attribute("innerText").split(": ")[1]  # TODO: fix this lol
                my_pos = ""
                curr_round = []
                teams = teams[1].split(")")
                for opp in teams[:-1]:
                    name, pos = opp.split(" (")
                    if name == team_name:
                        my_pos = pos
                    curr_round.append(name)
                my_placements.append(placement)
                my_positions.append(my_pos)
                team_scores.append(int(score))
                debate_rounds.append(curr_round)
    return my_placements, my_positions, team_scores, debate_rounds


'''
Gets a team's position in a debate
@param {team_name} is the name of the team
@param {col} is the column of the table that contains the team's position
@return {pos} is the position of the team in the debate, either "OG", "OO", "CG", or "CO"
'''
def get_teams_position(team_name, col):
    popup = col.find_element(By.XPATH, './/div[@role="tooltip" and @class="popover bs-popover-bottom"]')
    teams = popup.find_elements(By.XPATH, './/div[@class="list-group-item"]')[0].get_attribute("innerText").split("Teams in debate:")[1].split(")")[:-1]
    for team in teams:
        name, pos = team.split(" (")
        if name == team_name:
            return pos


'''
Gets the points awarded to a team based on their placement
@param {col} is the column of the table that contains the team's position
@return {points[placement]} is the number of points awarded to the team
'''
def get_teams_placement_points(col):
    points = {"1st": 3, "2nd": 2, "3rd": 1, "4th": 0}
    popup = col.find_element(By.XPATH, './/div[@role="tooltip" and @class="popover bs-popover-bottom"]')
    placement = popup.find_element(By.XPATH, './/h6[@class="flex-grow-1"]').get_attribute("innerText").replace("Placed ", "")
    return points[placement]


'''
Gets the tournament average speaker score per round, the position average speaker score per round,
the room average speaker score per round, and the average points awarded per round

@param {teams} is a dictionary of teams and the rounds they were in
@param {positions} is a list of the user's positions per round
@param {num_rounds} is the number of rounds in the tournament

@return {tourney_scores} is a list of the tournament average speaker score per round
@return {position_scores} is a list of the position average speaker score per round (based on the user)
@return {room_scores} is a list of the room average speaker score per round (based on the user)
@return {avg_points} is a list of the average points awarded per round (based on the user's position)
'''
def get_tourney_scores_points_stats(teams, positions, num_rounds):
    # print(positions)
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
            score = cols[col_round_start + round].find_elements(By.XPATH, './/small')
            if not score:  # if no score, skip
                continue
            score = int(score[0].get_attribute("innerText"))
            if name in teams and round in teams[name]:
                room_scores[round] += score
            tourney_scores[round] += score

            if get_teams_position(name, cols[col_round_start + round]) == positions[round]:
                # print(round, positions[round], name)
                position_scores[round] += score
                avg_points[round] += get_teams_placement_points(cols[col_round_start + round])
            tot_debate_teams[round] += 1

    for i in range(num_rounds):
        tourney_scores[i] /= tot_debate_teams[i] * 2
        position_scores[i] /= (tot_debate_teams[i] / 4) * 2
        room_scores[i] /= 8
        avg_points[i] /= tot_debate_teams[i] / 4

    return tourney_scores, position_scores, room_scores, avg_points


'''
Gets the user's speaker scores per round

> Assert that the current page we are scraping is the Speaker Tab

@param {my_name} is the name of the user
@param {num_rounds} is the number of rounds in the tournament
@return {my_scores} is a list of the user's speaker scores per round
'''
def get_my_speaker_scores(my_name, num_rounds):
    my_row = driver.find_element(By.XPATH, f'//span[@class="tooltip-trigger" and contains(., "{my_name}")]/ancestor::tr')
    cols = my_row.find_elements(By.XPATH, './/td')
    my_scores = [-1] * num_rounds
    for round in range(num_rounds):
        score = cols[4 + round].find_elements(By.XPATH, './/span[@class="tooltip-trigger"]')  # TODO: fix the 4 + lol
        if not score:
            continue
        my_scores[round] = int(score[0].get_attribute("innerText"))
    return my_scores


'''
Format the data into a list of dictionaries, where each dictionary is the data for a round
'''
def format_data_by_round(data):
    points = {"1st": 3, "2nd": 2, "3rd": 1, "4th": 0}
    formatted_data = []
    for placement, position, team_score, tourney_score, position_score, room_score, avg_point, my_score in zip(data["my_placements"], data["my_positions"], data["team_scores"], data["tourney_scores"], data["position_scores"], data["round_scores"], data["avg_points"], data["my_scores"]):
        round_data = {
            "result": points[placement],
            "team": position,
            "partner_speaks": team_score - my_score,
            "round_speaks": round(tourney_score, 3),
            "position_speaks": round(position_score, 3),
            "room_speaks": round(room_score, 3),
            "avg_result": round(avg_point, 3),
            "speaks": my_score
        }
        formatted_data.append(round_data)
    avg_round = {
        "result": sum([points[placement] for placement in data["my_placements"]]),
        "avg_result": round(sum(data["avg_points"]), 3),
        "team": "",
        "speaks": round(sum(data["my_scores"]) / len(data["my_scores"]), 3),
        "partner_speaks": round((sum(data["team_scores"]) - sum(data["my_scores"])) / len(data["team_scores"]), 3),
        "round_speaks": round(sum(data["tourney_scores"]) / len(data["tourney_scores"]), 3),
        "position_speaks": round(sum(data["position_scores"]) / len(data["position_scores"]), 3),
        "room_speaks": round(sum(data["round_scores"]) / len(data["round_scores"]), 3)
    }
    formatted_data.append(avg_round)
    return formatted_data


'''
Main function to scrape the data
Gets the following:
- user's placements per round
- user's positions per round
- user's team's scores per round

- tournament average speaker score per round
- position average speaker score per round (based on the user)
- room average speaker score per round (based on the user)
- average points awarded per round (based on the user's position)

- user's speaker scores per round
'''
def scrape(url, team_name, my_name):
    init()

    driver.get(url)
    click_on_nav("Team Tab")
    print("Getting placements, positions, and scores for team...")
    my_placements, my_positions, team_scores, rounds = get_opponents(team_name)

    # [print(round) for round in rounds]
    faced = {}
    for round, round_num in zip(rounds, range(len(rounds))):
        for team in round:
            if team in faced:
                faced[team].append(round_num)
            else:
                faced[team] = [round_num]

    # print(faced)
    print("Getting tournament scores, position scores, round scores, and average points...")
    tourney_scores, position_scores, round_scores, avg_points = get_tourney_scores_points_stats(faced, my_positions, len(rounds))
    # print(tourney_scores)
    # print(position_scores)
    # print(round_scores)
    # print(avg_points)

    # Get participant speaker scores
    print("Getting your speaker scores...")
    click_on_nav("Speaker Tab")
    my_scores = get_my_speaker_scores(my_name, len(rounds))
    # print(my_scores)

    data = {
        "my_placements": my_placements,
        "my_positions": my_positions,
        "team_scores": team_scores,
        "tourney_scores": tourney_scores,
        "position_scores": position_scores,
        "round_scores": round_scores,
        "avg_points": avg_points,
        "my_scores": my_scores
    }

    driver.quit()

    return format_data_by_round(data)