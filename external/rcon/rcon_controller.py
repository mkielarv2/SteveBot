import os

from mcrcon import MCRcon


class RconController:
    def __init__(self):
        self.server_address = os.getenv('SERVER_ADDRESS')
        self.rcon_secret = os.getenv('RCON_SECRET')
    
    def save_all(self):
        return self.executeRconCommand('/save-all')
        
    def stop(self):
        return self.executeRconCommand('/stop')

    def list(self):
        return self.executeRconCommand('/list')

    def tps(self):
        return self.executeRconCommand('/forge tps')

    def executeRconCommand(self, command: str):
        with MCRcon(self.server_address, self.rcon_secret) as mcr:
            return mcr.command(command)
