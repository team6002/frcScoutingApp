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
team_events_played_column = constant["team_events_played_column"]


auth_key = open("./json-files/X-TBA-Auth-Key.json")
key = json.load(auth_key)
auth_key.close()

stats = statbotics.Statbotics()
TBA_AUTH_KEY = key["key"]
TBA_BASE_ENDPOINT = "https://www.thebluealliance.com/api/v3"

gc = gspread.service_account(filename="json-files/credentials.json")

# Open a sheet from a spreadsheet in one go
sheet = gc.open(spreadsheet_name).sheet1

event_keys = [
    "2025miber"
    # "2025mibat"
]

team_numbers = []
team_names = []
team_states = []
team_epas = []
team_winrates = []
rookie_years = []
auto_move = []
climb = []
events_played = []
stat_by_team = []


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
                team_numbers.append([item["team_number"]])
                team_names.append([item["nickname"]])
                team_states.append([item["state_prov"]])

    # store team epas, winrates, and rookie years
    for team in team_numbers:
        stat_by_team.clear()
        stat_by_team.append(stats.get_team_year(team[0], 2025))

        auto_move.append([auto_leave(team[0])])
        climb.append([can_climb(team[0])])
        team_epas.append([stat_by_team[0]["epa"]["breakdown"]["total_points"]])
        rookie_years.append([stats.get_team(team[0])["rookie_year"]])
        team_winrate = round(stat_by_team[0]["record"]["winrate"] * 100, 1)
        team_winrates.append([f"{team_winrate}%"])
        events_played.append([team_events_played(team[0])])

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
        "range": f"{team_climb_column}2:{team_climb_column}{len(climb) + 1}",
        "values": climb
    }])

    sheet.batch_update([{
        "range": f"{team_events_played_column}2:{team_events_played_column}{len(climb) + 1}",
        "values": events_played
    }])

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
    except:
        return "N/A"

def get_winrate(team):
    try:
        str(round(stats.get_team_year(team, 2025)["record"]["winrate"] * 100, 1))
    except:
        return "N/A"

    return str(round(stats.get_team_year(team, 2025)["record"]["winrate"] * 100, 1)) + "%"

def get_team_state(team):
    return call_tba_api(f"team/frc{team}")["state_prov"]

def get_rookie_year(team):
    return str(call_tba_api(f"team/frc{team}")["rookie_year"])

def get_name(team):
    return str(call_tba_api(f"team/frc{team}")["nickname"])

def auto_leave(team_num):
    team_slot = 0
    red = False
    i = 1
    j = 0
    keys = []
    for event in call_tba_api(f"team/frc{team_num}/events/2025"):
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

def can_climb(team_num):
    team_slot = 0
    red = False
    i = 1
    j = 0
    keys = []
    for event in call_tba_api(f"team/frc{team_num}/events/2025"):
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