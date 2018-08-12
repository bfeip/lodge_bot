import discord
import asyncio
import os
import sys
import utils
import logger
from chan_event import *

client = discord.Client()
prefix = None
token = None
command_table = dict()
chan_event = None
    
def start(token, pre='$'):
    global prefix
    prefix = pre
    client.run(token)
    
async def soft_fail(channel, err):
    logger.log(err)
    await client.send_message(channel, "Uh-oh! Show this to mosen:\n {}".format(str(err)))
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)

@client.event
async def on_ready():
    print('Logged in as {}'.format(client.user.name))
    print('User ID: {}'.format(client.user.id))
    
@client.event
async def on_message(message):
    if chan_event is not None and not message.author.bot:
        try:
            await chan_event.process_message(message)
        except ChanEventException as e:
            await client.send_message(message.channel, str(e))
        except Exception as e:
            await soft_fail(message.channel, e)
    if message.content.startswith(prefix) and len(message.content) > 1:
        command_text = message.content[1:].split()[0]
        command = command_table.get(command_text)
        if command is not None:
            response = await command(message)
        else:
            await client.send_message(message.channel, "Sorry, I didn't understand that")
            
def command(com):
    # add the name/func mapping to the dict
    global command_list
    command_invocation = com.__name__.replace('_', ' ')
    command_table.update({command_invocation: com})
    return com

###########################################

@command
async def debug(message):
    if not utils.message_is_from_admin(message) or message.server.id != '463549434488160317':
        return
    exec(" ".join(message.content.split()[1:]))
    return

@command
async def ping(message):
    await client.send_message(message.channel, "Pong")
   
@command
async def suicide(message):
    if not utils.message_is_from_admin(message) or message.server.id != '463549434488160317':
        return
    await client.send_message(message.channel, "oh fug")
    await client.logout()
    
@command
async def chanevent(message):
    if not utils.message_is_from_admin(message):
        await client.send_message(message.channel, "This command can only be used by an admin")
        return
        
    if len(message.content.split()) < 2:
        await client.send_message(message.channel, "This command requires arguments")
        return
        
    if message.content.split()[1].lower() == "init":
        await client.send_message(message.channel, "Initalizing")
        role_names = message.content.split()[2:]
        if role_names == []:
            await client.send_message(message.channel, "You need to supply some role names")
            return
        global chan_event
        try:
            chan_event = ChanEvent(client, message.server, role_names)
            await client.send_message(message.channel, "Done!")
        except ChanEventException as e:
            await client.send_message(message.channel, str(e))
        except Exception as e:
            await soft_fail(message.channel, e)
        return
            
    elif message.content.split()[1].lower() == "goal":
        if chan_event is not None:
            try:
                await chan_event.set_goal(message.content.split()[-1])
            except ChanEventException as e:
                await client.send_message(message.channel, str(e))
            except Exception as e:
                await soft_fail(message.channel, e)
        else:
            await client.send_message(message.channel, "Needs a chanevent to be initalized")
        return
        
    if message.content.split()[-1].lower() == "start":
        if chan_event is not None:
            try:
                await chan_event.start()
                await client.send_message(message.channel, "Started event!")
            except ChanEventException as e:
                await client.message(message.channel, str(e))
            except Exception as e:
                await soft_fail(message.channel, e)
        else:
            await client.send_message(message.channel, "chanevent needs to be initalized first")
        return
        
    if message.content.split()[-1].lower() == "score":
        if chan_event is not None and chan_event.started == True:
            try:
                score = await chan_event.show_scoreboard()
                await client.send_message(message.channel, score)
            except ChanEventException as e:
                await client.message(message.channel, str(e))
            except Exception as e:
                await soft_fail(message.channel, e)
        else:
            await client.send_message(message.channel, "chanevent needs to be started first")
        return
        
    if message.content.split()[-1].lower() == "finish":
        if chan_event is not None and chan_event.started == True:
            try:
                winner_msg = await chan_event.finish()
                await client.send_message(message.channel, winner_msg)
            except ChanEventException as e:
                await client.message(str(e))
            except Exception as e:
                await soft_fail(message.channel, e)
        else:
            await client.send_message(message.channel, "there isn't even a game started yet!")
        return
    
    await client.send_message(message.channel, "?")
    return
    
###########################################

if __name__ == '__main__':
    token = os.getenv("BOT_TOKEN")
    if token is None:
        print("Your bot token must be listed in the BOT_TOKEN envirnment variable")
        sys.exit(1)
    start(token)