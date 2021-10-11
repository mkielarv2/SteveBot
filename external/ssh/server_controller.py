import os

import paramiko
from paramiko_expect import SSHClientInteraction

from external.ssh.InvalidServerException import InvalidServerException
from external.ssh.ServerAlreadyRunningException import ServerAlreadyRunningException


class ServerController:
    def __init__(self):
        self.server_address = os.getenv('SERVER_ADDRESS')
        self.server_username = os.getenv('SERVER_USERNAME')
        self.server_host = os.getenv('SERVER_HOST')

    def list(self):
        stdout, stderr = self.executeCommand('ls')

        output = ''
        for line in stdout:
            output = output + line

        return output

    def start(self, name):
        stdout, stderr = self.executeCommand('ls')

        servers = []
        for element in stdout:
            servers.append(element.strip())

        if name not in servers:
            raise InvalidServerException('Invalid server name')

        stdout, stderr = self.executeCommand('screen -list')
        # todo investigate
        if stdout[0] == 'There is a screen on:\r\n' or 'server' in stdout[1]:
            raise ServerAlreadyRunningException('There is a minecraft server already running')

        with paramiko.SSHClient() as ssh:
            k = self.getSshKey()
            prompt = self.server_username + '@' + self.server_host + ':~\$\s+'

            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.server_address, username=self.server_username, pkey=k, timeout=3)

            with SSHClientInteraction(ssh, timeout=3, display=True) as interact:
                interact.expect(prompt)

                interact.send('cd ' + name + ' ; screen -dmS server ./start.sh')
                interact.expect(prompt)

                interact.send('exit')
                interact.expect()

    def stop(self):
        self.executeCommand('screen -S server -X quit')

    def kill(self):
        self.executeCommand('pkill screen')

    def isServerRunning(self):
        stdout, stderr = self.executeCommand('screen -list')
        return stdout[0] == 'There is a screen on:\r\n' or 'server' in stdout[1]

    def executeCommand(self, command: str):
        with paramiko.SSHClient() as ssh:
            k = self.getSshKey()

            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.server_address, username=self.server_host, pkey=k, timeout=3)

            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
            stdout = ssh_stdout.readlines()
            stderr = ssh_stderr.readlines()

            print('stdout: ', stdout)
            print('stderr: ', stderr)

            return stdout, stderr

    def getSshKey(self):
        return paramiko.RSAKey.from_private_key_file('sshkey')
