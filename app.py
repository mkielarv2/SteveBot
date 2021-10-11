import base64
import os
import random
import socket
import traceback

import discord
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
from mcrcon import MCRconException

from external.s3.azure_premanent_storage import AzurePermanentStorage
from external.az.AzAuthException import AzAuthException
from external.az.azure_controller import AzureController
from external.rcon.rcon_controller import RconController
from external.ssh.InvalidServerException import InvalidServerException
from external.ssh.ServerAlreadyRunningException import ServerAlreadyRunningException
from external.ssh.server_controller import ServerController

load_dotenv(verbose=True)

prefix = '?'
if os.getenv('DEBUG'):
    prefix = '|'

bot = commands.Bot(command_prefix=prefix)

permanentStorage = AzurePermanentStorage()
azureController = AzureController()
serverController = ServerController()
rconController = RconController()


@bot.event
async def on_ready():
    permanentStorage.restoreAzureCredentials()
    print('SteveBot have started!')


@bot.event
async def on_message(message):
    await bot.process_commands(message)


key = None


@bot.command()
async def azlogin(ctx, *args):
    """
    Login to Microsoft Azure
    """
    global key
    if not args:
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)

        await ctx.send('Go to: https://www.devglan.com/online-tools/rsa-encryption-decryption\n'
                       'Encrypt your Azure username and password in format user:pass using '
                       '"RSA/ECB/OAEPWithSHA-1AndMGF1Padding" and this public key:\n\n' +
                       key.publickey().exportKey().decode() + '\n\nAnd then use ?azlogin <encrypted_credentials>')
    elif key:
        try:
            rsa_private_key = PKCS1_OAEP.new(RSA.importKey(key.exportKey('PEM')))
            decrypted = rsa_private_key.decrypt(base64.b64decode(args[0]))

            await ctx.send('Credentials decrypted successfully')

            credentials = decrypted.decode().split(':')
            username = azureController.az_login(credentials[0], credentials[1])

            permanentStorage.storeAzureCredentials()

            await ctx.send('Successfully authenticated user: ' + username)
        except AzAuthException:
            await ctx.send('Invalid username or password')
        except Exception:
            print(traceback.format_exc())
            await ctx.send('Something went wrong...')


@bot.command()
async def startvm(ctx):
    """
    Starts Azure virtual machine
    """
    await ctx.send('Starting Azure VM...')
    try:
        azureController.vm_start()
        await ctx.send('Azure VM started successfully')
    except AzAuthException:
        await ctx.send('Failed to authenticate with Azure')
    except Exception:
        print(traceback.format_exc())
        await ctx.send('Something went wrong...')


@bot.command()
async def stopvm(ctx):
    """
    Stops and deallocates Azure virtual machine
    """
    await ctx.send('Stopping Azure VM...')
    try:
        azureController.vm_stop()
        await ctx.send('Azure VM stopped successfully')
    except AzAuthException:
        await ctx.send('Failed to authenticate with Azure')
    except Exception:
        print(traceback.format_exc())
        await ctx.send('Something went wrong...')


@bot.command()
async def vmstate(ctx):
    """
    Get current state and ip of the virtual machine
    """
    await ctx.send('Checking VM state...')
    try:
        vm_state = azureController.vm_state()
        await ctx.send('Hardware: ' + vm_state.hardware + '\n' +
                       'State: ' + vm_state.state + '\n' +
                       'Location: ' + vm_state.location + '\n' +
                       'Public IP: ' + vm_state.public_ip)
    except AzAuthException:
        await ctx.send('Failed to authenticate with Azure')
    except Exception:
        print(traceback.format_exc())
        await ctx.send('Something went wrong...')


@bot.command()
async def balance(ctx):
    """
    Check your Azure balance
    """
    await ctx.send('Check your Azure balance here: https://www.microsoftazuresponsorships.com/Usage')


@bot.command()
async def list(ctx):
    """
    List available minecraft servers
    """
    try:
        servers = serverController.list()
        await ctx.send(servers)
    except socket.timeout:
        print(traceback.format_exc())
        await ctx.send('Connection timed out, the VM might be deallocated')
    except Exception:
        print(traceback.format_exc())
        await ctx.send('Something went wrong...')


@bot.command()
async def start(ctx, *args):
    """
    <server_name> Starts a Minecraft server
    """
    if not args:
        await ctx.send('Missing server name ?start <server_name>')
        return

    name = args[0]

    await ctx.send('Starting ' + name + ' server...')
    try:
        serverController.start(name)
        await ctx.send('Server ' + name + ' started successfully')
    except InvalidServerException:
        print(traceback.format_exc())
        await ctx.send('Invalid server name, use ?list to view available servers')
    except ServerAlreadyRunningException:
        print(traceback.format_exc())
        await ctx.send('There is a minecraft server already running')
    except socket.timeout:
        print(traceback.format_exc())
        await ctx.send('Connection timed out, the VM might be deallocated')
    except Exception:
        print(traceback.format_exc())
        await ctx.send('Something went wrong...')


@bot.command()
async def quickstart(ctx, *args):
    """
    Start VM and minecraft server in one go
    """
    if not args:
        await ctx.send('Missing server name ?quickstart <server_name>')
        return

    name = args[0]

    await ctx.send('Quickstart started...')
    await ctx.send('Starting Azure VM...')
    try:
        azureController.vm_start()
        await ctx.send('Azure VM started successfully')
    except AzAuthException:
        print(traceback.format_exc())
        await ctx.send('Failed to authenticate with Azure')
    except Exception:
        print(traceback.format_exc())
        await ctx.send('Azure VM Start failed')

    try:
        await ctx.send('Checking if server already running')
        if serverController.isServerRunning():
            await ctx.send('There is a minecraft server already running')
            return

        await ctx.send('No server running, starting ' + name + ' server')
        serverController.start(name)

        await ctx.send('Server ' + name + ' started successfully')
        await ctx.send('Quickstart completed successfully')
    except InvalidServerException:
        print(traceback.format_exc())
        await ctx.send('Invalid server name, use ?list to view available servers')
    except socket.timeout:
        print(traceback.format_exc())
        await ctx.send('Connection timed out, the VM might be deallocated')
    except Exception:
        print(traceback.format_exc())
        await ctx.send('Something went wrong...')


@bot.command()
async def stop(ctx):
    """
    Safely stop currently running minecraft server
    """
    try:
        await ctx.send('Stopping minecraft server...')

        if serverController.isServerRunning():
            await ctx.send('There is no server running')
            return

        await ctx.send('Saving progress')

        print(rconController.save_all())
        print(rconController.stop())

        await ctx.send('Stopping session')

        serverController.stop()

        await ctx.send('Server stopped successfully')
    except MCRconException:
        print(traceback.format_exc())
        await ctx.send('Unknown RCON error...')
    except socket.timeout:
        print(traceback.format_exc())
        await ctx.send('Connection timed out, the VM might be deallocated')
    except Exception:
        print(traceback.format_exc())
        await ctx.send('Something went wrong...')

@bot.command()
async def quickstop(ctx):
    """
    Safely stops minecraft server and VM
    """

    try:
        if not serverController.isServerRunning():
            await ctx.send('There is no server running, continuing')
        else:
            await ctx.send('Saving progress')

            print(rconController.save_all())
            print(rconController.stop())

            await ctx.send('Stopping session')

            serverController.stop()

            await ctx.send('Server stopped successfully')
    except socket.timeout:
        print(traceback.format_exc())
        await ctx.send('Connection timed out, the VM might be deallocated')
    except MCRconException:
        print(traceback.format_exc())
        await ctx.send('Unknown RCON error...')
    except Exception:
        print(traceback.format_exc())
        await ctx.send('Something went wrong, while saving and stopping minecraft server, ignoring')

    await ctx.send('Stopping Azure VM')
    try:
        azureController.vm_stop()
        await ctx.send('Azure VM stopped successfully')
        await ctx.send('Quickstop completed successfully')
    except AzAuthException:
        print(traceback.format_exc())
        await ctx.send('Failed to authenticate with Azure')
    except Exception:
        print(traceback.format_exc())
        await ctx.send('Azure VM stop failed, Quickstop did not complete')


@bot.command()
async def kill(ctx):
    """
    Performs sigkill on all running server processes USE WISELY!
    """
    try:
        await ctx.send('Killing all children...')
        serverController.kill()
        await ctx.send('All children killed successfully')
    except socket.timeout:
        print(traceback.format_exc())
        await ctx.send('Connection timed out, the VM might be deallocated')
    except Exception:
        print(traceback.format_exc())
        await ctx.send('Something went wrong...')

@bot.command()
async def players(ctx):
    """
    List players on currently running server
    """
    try:
        await ctx.send(rconController.list())
    except MCRconException:
        await ctx.send('Unknown RCON error...')
        print(traceback.format_exc())
    except Exception:
        await ctx.send('Something went wrong...')
        print(traceback.format_exc())


@bot.command()
async def tps(ctx):
    """
    Show tps for current running server
    """
    try:
        await ctx.send(rconController.tps())
    except MCRconException:
        await ctx.send('Unknown RCON error...')
        print(traceback.format_exc())
    except Exception:
        await ctx.send('Something went wrong...')
        print(traceback.format_exc())


@bot.command()
async def goodbot(ctx: Context):
    """
    Thank the Bot for its work
    """
    await ctx.message.add_reaction(random.choice(['❤️', '🥰', '😍', '🤩', '☺️', '😇']))
    embed = discord.Embed()
    embed.set_image(url='https://media.tenor.com/images/9db7a1b8f06f00b14ae8a05fd7404566/tenor.gif')
    await ctx.send(embed=embed)


bot.run(os.getenv('DISCORD_BOT_KEY'))
