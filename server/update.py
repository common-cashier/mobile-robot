from server.settings import get_md5, log, Level
from server import settings


def update_init():
    file_path = r'./bots/boc.py'
    md5_01 = get_md5(file_path)
    file_path = r'./bots/ccb.py'
    md5_02 = get_md5(file_path)
    file_path = r'./bots/icbc.py'
    md5_03 = get_md5(file_path)
    settings.md5_json = {
        "boc": md5_01,
        "ccb": md5_02,
        "icbc": md5_03
    }
    log(str(settings.md5_json), Level.X_LOG, True)
