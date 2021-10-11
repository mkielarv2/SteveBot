import json
import os
import subprocess

from external.az.AzAuthException import AzAuthException
from external.az.model.vm_state import VmState


class AzureController:
    def az_login(self, username, password):
        stdout, stderr = self.run_command('az', 'login', '-u', username, '-p', password)

        if 'The user name might be invalid.' in stderr:
            raise AzAuthException('Invalid credentials')

        j = json.loads(stdout)[0]

        return j['user']['name']

    def vm_start(self):
        stdout, stderr = self.run_command('az', 'vm', 'start', '-g', os.getenv('AZURE_WORKGROUP'),
                                          '-n', os.getenv('AZURE_VM_NAME'))

        self.checkAzureAuthFailed(stdout, stderr)

    def vm_stop(self):
        stdout, stderr = self.run_command('az', 'vm', 'deallocate', '-g', os.getenv('AZURE_WORKGROUP'),
                                          '-n', os.getenv('AZURE_VM_NAME'))

        self.checkAzureAuthFailed(stdout, stderr)

    def vm_state(self):
        stdout, stderr = self.run_command('az', 'vm', 'list', '-d')

        self.checkAzureAuthFailed(stdout, stderr)

        j = json.loads(stdout)[0]

        return VmState(
            j['hardwareProfile']['vmSize'],
            j['powerState'],
            j['location'],
            j['publicIps']
        )

    def run_command(self, *args: str):
        process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout = process.stdout.decode('utf-8')
        stderr = process.stderr.decode('utf-8')

        print('stdout: ', stdout)
        print('stderr: ', stderr)

        return stdout, stderr

    def checkAzureAuthFailed(self, stdout: str, stderr: str):
        if len(stdout) == 0 and 'az login' in stderr:
            raise AzAuthException('Failed to authenticate with Azure')
