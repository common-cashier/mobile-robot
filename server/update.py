from settings import get_md5, log, Level


def update_init():
    file_path = r'./bots/boc.py'
    md5_01 = get_md5(file_path)
    file_path = r'./bots/ccb.py'
    md5_02 = get_md5(file_path)
    md5_json = {
        "boc": md5_01,
        "ccb": md5_02
    }
    log(str(md5_json), Level.X_LOG, True)
