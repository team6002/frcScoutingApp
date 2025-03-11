import json

import discord
from discord import Option

import main

bot = discord.Bot()
token = json.load(open("./json-files/BotToken.json"))["token"]

@bot.command(name="get_epa", description="returns_requested_teams_epa")
async def get_epa(ctx, team, epa_type: Option(str, "types_of_epas", choices=["total", "auto", "climb", "teleop"])):
    await ctx.defer()
    await ctx.respond(f"team {team}'s {epa_type} epa is {main.get_epa_by_team(int(team), epa_type)}")

@bot.command(name="get_winrate", description="returns_requested_teams_epa")
async def get_winrate(ctx, team):
    await ctx.defer()
    await ctx.respond(f"team {team}'s winrate is {main.get_winrate(int(team))}")

@bot.command(name="get_rookie_year", description="returns_requested_teams_rookie_year")
async def get_rookie_year(ctx, team):
    await ctx.defer()
    await ctx.respond(f"team {team}'s rookie year is {main.get_rookie_year(int(team))}")

@bot.command(name="get_name", description="returns_requested_teams_name")
async def get_name(ctx, team):
    await ctx.defer()
    await ctx.respond(f"team {team}'s name is {main.get_name(int(team))}")

@bot.command(name="get_state", description="returns_requested_teams_state")
async def get_state(ctx, team):
    await ctx.defer()
    await ctx.respond(f"{team}'s home state/province is {main.get_team_state(int(team))}")

@bot.command(name="auto_move", description="returns_if_requested_team_can_auto_move")
async def get_auto_move(ctx, team):
    await ctx.defer()
    await ctx.respond(f"{team} can move in auto: {main.auto_leave(int(team))}")

@bot.command(name="climb", description="returns_if_requested_team_can_climb")
async def get_park(ctx, team):
    await ctx.defer()
    await ctx.respond(f"{team} can climb at the {main.can_climb(int(team))} level")

@bot.command(name="climb_percent", description="returns_percent_team_climbed")
async def get_climb_percent(ctx, team):
    await ctx.defer()
    await ctx.respond(f"{team} climbed in {main.get_percentage(int(team), "climb")}% of their matches")

@bot.command(name="auto_leave_percent", description="returns_percent_team_left_in_auto")
async def get_auto_leave_percent(ctx, team):
    await ctx.defer()
    await ctx.respond(f"{team} left the start line in {main.get_percentage(int(team), "auto_leave")}% of their matches")

@bot.command(name="played", description="returns_number_of_tournaments_played")
async def played(ctx, team):
    await ctx.defer()
    await ctx.respond(f"{team} has competed at {main.team_events_played(int(team))}")

@bot.command(name="summary", description="returns_summary_of_requested_team")
async def summary(ctx, team):
    await ctx.defer()
    await ctx.respond(
        f"summary of team {team} \n" +
        f"name: {main.get_name(int(team))} \n" +
        f"home state/province: {main.get_team_state(int(team))} \n" +
        f"epa: {main.get_epa_by_team(int(team), "total")} \n" +
        f"rookie year: {main.get_rookie_year(int(team))} \n" +
        f"winrate: {main.get_winrate(int(team))} \n" +
        f"can move in auto: {main.auto_leave(int(team))} \n" +
        f"leaves the start line: {main.get_percentage(int(team), "auto_leave")}% of the time\n" +
        f"can climb at the: {main.can_climb(int(team))} level\n" +
        f"climbs: {main.get_percentage(int(team), "climb")}% of the time\n" +
        f"has competed at: {main.team_events_played(int(team))}\n"
    )

bot.run(token)
