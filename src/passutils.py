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

def encrypt(path: Path, root: Path, text: str):
    gpg = GPG(use_agent=True)
    recipients = get_recipients(path, root)
    if recipients is None:
        return "Recipients file (.gpg-id) not found"
    # pass always ends its files with a newline
    if not text.endswith("\n"):
        text += "\n"
    encrypted_data = gpg.encrypt(text, recipients, armor=False)
    if encrypted_data.ok:
        with open(path, "wb") as f:
            f.write(encrypted_data.data)
        return None
    else:
        if hasattr(encrypted_data, "status_detail"):
            return "{}: {}".format(encrypted_data.status, encrypted_data.status_detail)
        return encrypted_data.status

def get_recipients(path: Path, root: Path) -> None | list[str]:
    recipients_file: None | Path = None
    recipients: None | list[str] = None
    while path != root.parent:
        if (path / ".gpg-id").is_file():
            recipients_file = path / ".gpg-id"
            break
        path = path.parent
    if recipients_file is not None:
        with open(recipients_file, "r") as gpg_id_file:
            recipients = gpg_id_file.read().splitlines()
    return recipients
