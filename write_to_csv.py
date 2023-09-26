def write_to_csv(data):
    file = open("out.csv", "w")
    cols = ["team", "result", "avg_result", "speaks", "partner_speaks", "room_speaks", "position_speaks", "round_speaks"]
    for round in data:
        for col in cols:
            file.write(str(round[col]) + ",")
        file.write("\n")
    file.close()
    return "Done"

