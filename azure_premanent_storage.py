import shutil
from os.path import expanduser

from file_manager import FileManager


class AzurePermanentStorage:
    def __init__(self):
        self.file_manager = FileManager()

    def storeAzureCredentials(self):
        shutil.make_archive('azure', 'zip', expanduser('~/.azure'))
        self.file_manager.upload_file_to_bucket('azure.zip')

    def restoreAzureCredentials(self):
        self.file_manager.download_file_from_bucket('azure.zip', 'azure-restored.zip')
        try:
            shutil.rmtree(expanduser('~/.azure'))
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
        shutil.unpack_archive('azure-restored.zip', expanduser('~/.azure'))