import gspread
import statbotics
import json
import requests

constants = open("./json-files/constants.json")
constant = json.load(constants)
constants.close()
team_number_column = constant["team_number_column"]
team_name_column = constant["team_name_column"]
team_state_column = constant["team_state_column"]
team_epa_column = constant["team_epa_column"]
team_winrate_column = constant["team_winrate_column"]
spreadsheet_name = constant["spreadsheet_name"]
team_rookie_year_column = constant["team_rookie_year_column"]
team_auto_move_column = constant["team_auto_move_column"]
team_climb_column = constant["team_climb_column"]
team_auto_move_percent_column = constant["team_auto_move_percent_column"]
team_climb_percent_column = constant["team_climb_percent_column"]
team_events_played_column = constant["team_events_played_column"]


auth_key = open("./json-files/X-TBA-Auth-Key.json")
key = json.load(auth_key)
auth_key.close()

stats = statbotics.Statbotics()
TBA_AUTH_KEY = key["key"]
TBA_BASE_ENDPOINT = "https://www.thebluealliance.com/api/v3"

event_keys = [
    "2025miber"
    # "2025mibat"
]

gc = gspread.service_account(filename="./json-files/credentials.json")

# Open a sheet from a spreadsheet in one go
sheet = gc.open(spreadsheet_name).sheet1

team_numbers = []
team_names = []
team_states = []
team_epas = []
team_winrates = []
rookie_years = []
auto_move = []
climb = []
events_played = []
teams_climbed = []
teams_moved = []
teams_moved_percent = []
teams_climbed_percent = []
stat_by_team = []
complete_data = []


def call_tba_api(url):
    r = requests.get(f"{TBA_BASE_ENDPOINT}/{url}", headers={"X-TBA-Auth-Key": TBA_AUTH_KEY})

    return r.json()

def clear_vars():
    team_numbers.clear()
    team_names.clear()
    team_states.clear()
    team_epas.clear()
    team_winrates.clear()
    rookie_years.clear()
    auto_move.clear()
    climb.clear()
    teams_moved.clear()
    teams_climbed.clear()

def update_event_json():
    for event in event_keys:
        with open(f"./json-files/{event}.json", "w+") as jsonFile:
            data = call_tba_api(f"/event/{event}/teams")
            jsonFile.write(json.dumps(data))

async def update_sheet():
    # update json files for entered event keys
    clear_vars()
    update_event_json()
    # create lists that will store gathered data so that we can push all the data in one go

    # store team numbers, names, and state/provinces
    for event in event_keys:
        with open(f"./json-files/{event}.json", "r") as data:
            data = json.load(data)
            for item in data:
                try:
                    team_numbers.append([item["team_number"]])
                except Exception:
                    team_numbers.append(["N/A"])
                try:
                    team_names.append([item["nickname"]])
                except Exception:
                    team_names.append(["N/A"])
                try:
                    team_states.append([item["state_prov"]])
                except Exception:
                    team_states.append(["N/A"])

    # store team epas, winrates, and rookie years
    for team in team_numbers:
        print(team[0])
        stat_by_team.clear()
        stat_by_team.append(stats.get_team_year(team[0], 2025))
        auto_move.append([auto_leave(team[0])])
        climb.append([can_climb(team[0])])
        team_epas.append([stat_by_team[0]["epa"]["breakdown"]["total_points"]])
        rookie_years.append([stats.get_team(team[0])["rookie_year"]])
        team_winrate = round(stat_by_team[0]["record"]["winrate"] * 100, 1)
        team_winrates.append([f"{team_winrate}%"])
        events_played.append([team_events_played(team[0])])
        teams_moved.append([auto_leave(team[0])])
        teams_climbed.append([can_climb(team[0])])
        teams_climbed_percent.append([get_percentage(team[0], "climb")])
        teams_moved_percent.append([get_percentage(team[0], "auto_leave")])

    # complete_data.append(team_numbers)
    # complete_data.append(team_names)
    # complete_data.append(team_states)
    # complete_data.append(team_epas)
    # complete_data.append(rookie_years)
    # complete_data.append(team_winrates)
    # complete_data.append(auto_move)
    # complete_data.append(teams_moved_percent)
    # complete_data.append(teams_climbed)
    # complete_data.append(teams_climbed_percent)
    # complete_data.append(team_events_played)
    # use batch update to avoid google requests rate limit
    sheet.batch_update([{
        "range": f"{team_number_column}2:{team_number_column}{len(team_numbers) + 1}",
        "values": team_numbers
    }])

    sheet.batch_update([{
        "range": f"{team_name_column}2:{team_name_column}{len(team_names) + 1}",
        "values": team_names
    }])

    sheet.batch_update([{
        "range": f"{team_state_column}2:{team_state_column}{len(team_states) + 1}",
        "values": team_states
    }])

    sheet.batch_update([{
        "range": f"{team_epa_column}2:{team_epa_column}{len(team_epas) + 1}",
        "values": team_epas
    }])

    sheet.batch_update([{
        "range": f"{team_winrate_column}2:{team_winrate_column}{len(team_winrates) + 1}",
        "values": team_winrates
    }])

    sheet.batch_update([{
        "range": f"{team_rookie_year_column}2:{team_rookie_year_column}{len(rookie_years) + 1}",
        "values": rookie_years
    }])

    sheet.batch_update([{
        "range": f"{team_auto_move_column}2:{team_auto_move_column}{len(auto_move) + 1}",
        "values": auto_move
    }])

    sheet.batch_update([{
        "range": f"{team_auto_move_percent_column}2:{team_auto_move_percent_column}{len(teams_moved) + 1}",
        "values": teams_moved_percent
    }])

    sheet.batch_update([{
        "range": f"{team_climb_column}2:{team_climb_column}{len(climb) + 1}",
        "values": climb
    }])

    sheet.batch_update([{
        "range": f"{team_climb_percent_column}2:{team_climb_percent_column}{len(teams_climbed) + 1}",
        "values": teams_climbed_percent
    }])

    sheet.batch_update([{
        "range": f"{team_events_played_column}2:{team_events_played_column}{len(climb) + 1}",
        "values": events_played
    }])

    # sheet.batch_update([{
    #     "range" : f"{team_number_column}2:{team_events_played_column}{len(team_numbers) + 1}",
    #     "values" : [complete_data]
    # }])

def get_epa_by_team(team, epa_type):
    try:
       if epa_type == "total":
           return str(stats.get_team_year(team, 2025)["epa"]["breakdown"]["total_points"])
       elif epa_type == "teleop":
           return str(stats.get_team_year(team, 2025)["epa"]["breakdown"]["teleop_points"])
       elif epa_type == "auto":
           return str(stats.get_team_year(team, 2025)["epa"]["breakdown"]["auto_points"])
       elif epa_type == "climb":
           return str(stats.get_team_year(team, 2025)["epa"]["breakdown"]["endgame_points"])
       else:
           return "N/A"
    except Exception:
        return "N/A"

def get_winrate(team):
    try:
        str(round(stats.get_team_year(team, 2025)["record"]["winrate"] * 100, 1))
    except Exception:
        return "N/A"

    return str(round(stats.get_team_year(team, 2025)["record"]["winrate"] * 100, 1)) + "%"

def get_team_state(team):
    try:
        state_prov = call_tba_api(f"team/frc{team}")["state_prov"]
    except Exception:
        state_prov = "N/A"
    return state_prov

def get_rookie_year(team):
    try:
        rookie_year = str(call_tba_api(f"team/frc{team}")["rookie_year"])
    except Exception:
        rookie_year = "N/A"
    return rookie_year

def get_name(team):
    try:
        nickname = (call_tba_api(f"team/frc{team}")["nickname"])
    except:
        nickname = "N/A"
    return nickname

def auto_leave(team_num):
    team_slot = 0
    red = False
    i = 1
    j = 0
    keys = []

    events_auto = call_tba_api(f"team/frc{team_num}/events/2025")
    try:
        if "does not exist" in events_auto["Error"]:
            return False
    except:
        pass

    for event in events_auto:
        print(event)
        keys.append(event["key"])

        while j < len(keys):
            matches = call_tba_api(f"team/frc{team_num}/event/{keys[j]}/matches")
            match = 0
            while match < len(matches):
                for team in matches[match]["alliances"]["blue"]["team_keys"]:
                    if team == f"frc{team_num}":
                        team_slot = i
                        red = False
                    i = i + 1
                i = 1
                for team in matches[match]["alliances"]["red"]["team_keys"]:
                    if team == f"frc{team_num}":
                        team_slot = i
                        red = True
                    i = i + 1
                i = 1

                if red is False:
                    leave = call_tba_api(f"team/frc{team_num}/event/{keys[j]}/matches")[match]["score_breakdown"]["blue"][
                        f"autoLineRobot{team_slot}"]

                else:
                    leave = call_tba_api(f"team/frc{team_num}/event/{keys[j]}/matches")[match]["score_breakdown"]["red"][f"autoLineRobot{team_slot}"]

                match = match + 1

                # save all results in list, check if list contains one by one, and if contains none, return N/A
                if leave == "Yes":
                    return True
            j += 1
    return False

def get_percentage(team_num, type_):
    global match, type_of_data
    team_slot = 0
    red = False
    i = 1
    j = 0
    count = 0
    keys = []

    events_climb = call_tba_api(f"team/frc{team_num}/events/2025")
    try:
        if "does not exist" in events_climb["Error"]:
            return "0"
    except Exception:
        pass

    for event in events_climb:
        keys.append(event["key"])

        while j < len(keys):
            matches = call_tba_api(f"team/frc{team_num}/event/{keys[j]}/matches")
            if not matches:
                break
            match = 0
            while match < len(matches):
                for team in matches[match]["alliances"]["blue"]["team_keys"]:
                    if team == f"frc{team_num}":
                        team_slot = i
                        red = False
                    i += 1
                i = 1
                for team in matches[match]["alliances"]["red"]["team_keys"]:
                    if team == f"frc{team_num}":
                        team_slot = i
                        red = True
                    i += 1
                i = 1

                if type_ == "auto_leave":
                    type_of_data = f"autoLineRobot{team_slot}"
                elif type_ == "climb":
                    type_of_data = f"endGameRobot{team_slot}"

                if not red:
                    climb_or_leave = \
                    call_tba_api(f"team/frc{team_num}/event/{keys[j]}/matches")[match]["score_breakdown"]["blue"][type_of_data]
                else:
                    climb_or_leave = \
                    call_tba_api(f"team/frc{team_num}/event/{keys[j]}/matches")[match]["score_breakdown"]["red"][type_of_data]
                match = match + 1

                # save all results in list, check if list contains one by one, and if contains none, return N/A
                if type_ == "climb":
                    if climb_or_leave == "DeepCage" or climb_or_leave == "ShallowCage":
                        count += 1
                elif type_ == "auto_leave":
                    if climb_or_leave:
                        count += 1
            j += 1

    return f'{round((count / match) * 100, 1)}% of the time in {match} matches'

def can_climb(team_num):
    team_slot = 0
    red = False
    i = 1
    j = 0
    keys = []

    events_climb = call_tba_api(f"team/frc{team_num}/events/2025")
    try:
        if "does not exist" in events_climb["Error"]:
            return False
    except Exception:
        pass

    for event in events_climb:
        keys.append(event["key"])

        while j < len(keys):
            matches = call_tba_api(f"team/frc{team_num}/event/{keys[j]}/matches")
            match = 0
            while match < len(matches):
                for team in matches[match]["alliances"]["blue"]["team_keys"]:
                    if team == f"frc{team_num}":
                        team_slot = i
                        red = False
                    i += 1
                i = 1
                for team in matches[match]["alliances"]["red"]["team_keys"]:
                    if team == f"frc{team_num}":
                        team_slot = i
                        red = True
                    i += 1
                i = 1

                if red is False:
                    park = call_tba_api(f"team/frc{team_num}/event/{keys[j]}/matches")[match]["score_breakdown"]["blue"][
                        f"endGameRobot{team_slot}"]
                else:
                    park = call_tba_api(f"team/frc{team_num}/event/{keys[j]}/matches")[match]["score_breakdown"]["red"][
                        f"endGameRobot{team_slot}"]
                match = match + 1

                # save all results in list, check if list contains one by one, and if contains none, return N/A
                if park == "DeepCage":
                    return "Deep Cage"
                elif park == "ShallowCage":
                    return "Shallow Cage"
            j += 1

    return "Ground"

def team_events_played(team_num):
    try:
        played = 0
        events = call_tba_api(f"team/frc{team_num}/events/2025/statuses")
        i = 0
        for event in events:
            if (call_tba_api(f"team/frc{team_num}/events/2025/statuses")[event]["overall_status_str"]
                != f"Team {team_num} is waiting for the event to begin."):

                played += 1
            i += 1
        if played == 1:
            return str(played) + " event"
        else:
            return str(played) + " events"
    except Exception:
        return "N/A"