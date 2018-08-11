import discord
import asyncio
import os
import sys

client = discord.Client()
prefix = None
token = None
command_table = dict()
    
def start(token, pre='<'):
    global prefix
    prefix = pre
    client.run(token)

@client.event
async def on_ready():
    print('Logged in as {}'.format(client.user.name))
    print('User ID: {}'.format(client.user.id))
    
@client.event
async def on_message(message):
    if message.content.startswith(prefix):
        command_text = message.content[1:]
        print(command_table)
        command = command_table.get(command_text)
        if command is not None:
            response = await command(message)
        else:
            await client.send_message(message.channel, "Sorry, I didn't understand that")
            await client.send_message(message.channel, "I understand {}".format(command_table.keys()))
            
def command(com):
    # add the name/func mapping to the dict
    global command_list
    command_invocation = com.__name__.replace('_', ' ')
    command_table.update({command_invocation: com})
    print("New command table: {}".format(command_table))
    return com

###########################################

@command
async def ping(message):
    await client.send_message(message.channel, "Pong")
   
@command
async def suicide(message):
    await client.send_message(message.channel, "oh fug")
    await client.logout()
    
@command
async def special_event(message):
    if not utils.message_is_from_admin(message):
        client.send_message(message.channel, "This command can only be used by an admin")
    await client.send_message(message.channel, "Starting special event")
    
    
###########################################

if __name__ == '__main__':
    token = os.getenv("BOT_TOKEN")
    if token is None:
        print("Your bot token must be listed in the BOT_TOKEN envirnment variable")
        sys.exit(1)
    start(token)