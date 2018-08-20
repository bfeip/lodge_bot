import asyncio
import logger
import operator

class OnTheCrossException:
    def __init__(self, message):
        self.message = message
        
    def __repr__(self):
        return self.message
        
    def __str__(self):
        return str(self.message)

class Voter:
    def __init__(self, voter, max_votes):
        self.voter = voter
        self.max_votes = max_votes
        self.votes = []
        
    def add_vote(self, vote):
        if len(self.votes) >= self.max_votes:
            raise OnTheCrossException("OnTheCross: You've reached your vote limit")
            return
        self.votes.append(vote)
        return
        
    def get_votes(self):
        return self.votes

class OnTheCross:
    def __init__(self, max_votes):
        self.voted = {}
        self.scoreboard = {}
        self.max_votes = max_votes

    def process_vote(self, message):
        author = message.author
        mentions = message.mentions
        voter = self.voted.get(author, Voter(author, self.max_votes))
        for mention in mentions:
            voter.add_vote(mention)
            degen_cnt = self.scoreboard.get(mention, 0) + 1
            self.scoreboard[mention] = degen_cnt
        self.voted[voter] = voter
        return
        
    def finish(self):
        logger.log("OnTheCross: finishing game")
        biggest_degen = max(self.scoreboard.items(), key=operator.itemgetter(1))[0]
        final_message = "**Bringing the cross for {} with {} accusations**\n".format(biggest_degen, self.scoreboard[biggest_degen])
        logger.log("OnTheCross: {}".format(final_message))
        score = self.show_scoreboard()
        return final_message + score
        
    def show_scoreboard(self):
        ret_msg = "```\n"
        place = 1
        for team, score in sorted(self.scoreboard.items(), key = operator.itemgetter(1), reverse = True):
            ret_msg += "[{}]\tDegenerate {}:\n\t {} degenerate points\n".format(place, team, score)
            place += 1
        ret_msg += "```\nDegenerates like you belong on a cross"
        return ret_msg