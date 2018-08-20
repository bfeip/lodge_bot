import discord
import asyncio
import logger
import operator
from collections import OrderedDict

class ChanEventException(Exception):
    def __init__(self, message):
        self.message = message
        
    def __repr__(self):
        return self.message
        
    def __str__(self):
        return str(self.message)

class ChanEvent:
    def __init__(self, client, server, role_names, goal=None):
        logger.log("initalizing chanevent with roles {} for {}".format(role_names, server.name))
        self.client = client
        self.server = server
        self.role_names = role_names
        self.role_names.sort()
        self.goal = goal
        self.scoreboard = {role_name: 0 for role_name in role_names}
        self.started = False
        role_names_check = [role.name for role in server.roles if role.name in role_names]
        role_names_check.sort()
        if self.role_names != role_names_check:
            # at least one of role_names is not a real role in the server
            # TODO: tell us which role
            raise ChanEventException("ChanEvent: One of the roles I was given does not exist in this server")
            
    async def set_goal(self, goal):
        try:
            self.goal = int(goal)
        except:
            raise ChanEventException("ChanEvent: Is that even a number my dude?")
        return
            
    async def start(self):
        members = self.server.members
        roles = [role for role in self.server.roles if role.name in self.role_names]
        i = 0
        for member in members:
            await self.client.add_roles(member, roles[i])
            i += 1
            i %= len(roles)
        self.started = True
        
    async def process_message(self, message):
        if not self.started:
            return
        author = message.author
        content = message.content
        points = len(content)
        teams_singleton = [role.name for role in author.roles if role.name in self.role_names]
        if len(teams_singleton) > 1:
            raise ChanEventException("ChanEvent: {} has multiple roles that match the game".format(author.name))
        if len(teams_singleton) == 0:
            logger.log("ChanEvent: Processed message from {}, who does not have a team".format(author.name))
        logger.log("ChanEvent: processed message worth {} points from {} for team {}".format(points, author.name, teams_singleton[0]))
        self.scoreboard[teams_singleton[0]] += points
        if self.goal is not None and scoreboard[teams_singleton[0]] >= self.goal:
            return finish(teams_singleton[0])
        return

    async def show_scoreboard(self):
        ret_msg = "```\n"
        place = 1
        for team, score in sorted(self.scoreboard.items(), key = operator.itemgetter(1), reverse = True):
            ret_msg += "[{}]\tTeam {}:\n\t {}\n".format(place, team, score)
            place += 1
        ret_msg += "```"
        return ret_msg
        
    async def finish(self, winning_team_name=None):
        logger.log("ChanEvent: finishing game")
        self.started = False
        if winning_team_name is None:
            winning_team_name = max(self.scoreboard.items(), key=operator.itemgetter(1))[0]
        final_message = "**WINNER: {} with {} points**\n".format(winning_team_name, self.scoreboard[winning_team_name])
        logger.log("ChanEvent: {}".format(final_message))
        await self.clean()
        score = await self.show_scoreboard()
        return final_message + score
        
    async def clean(self):
        roles = [role for role in self.server.roles if role.name in self.role_names]
        futures = []
        members = self.server.members
        for member in members:
            futures.append(self.client.remove_roles(member, *roles))
        asyncio.wait(futures)
        return