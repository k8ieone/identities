from pathlib import Path
from gnupg import GPG

def list_dir(path):
    dirs = [x for x in path.iterdir() if x.is_dir()]
    keys = list(path.glob('*.gpg'))
    return dirs, keys

def decrypt(path):
    gpg = GPG(use_agent=True)
    with open(path, 'rb') as key_file:
        return str(gpg.decrypt_file(key_file))

def get_recipients(path):
    # TODO: Start at path and look for the .gpg-id file, continue ascending until we get to the store root
    pass
