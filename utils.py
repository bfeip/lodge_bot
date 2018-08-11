import discord

def message_is_from_admin(message):
    author = message.author
    if type(author) is not discord.Member:
        # This is a private channel... I don't really know
        # how this should be handled so just say no
        return False
    for role in member.roles:
        if role.permissions.administrator():
            return True
    return False