from pathlib import Path
from gnupg import GPG

class Store():

    def __init__(self, store_dir):
        self.store_dir = store_dir

    def list_dir(self, path):
        dirs = [x for x in path.iterdir() if x.is_dir()]
        keys = list(path.glob('*.gpg'))
        return dirs, keys

    def get_key(self, path):
        gpg = GPG(use_agent=True)
        with open(path, 'rb') as key_file:
            return str(gpg.decrypt_file(key_file))
