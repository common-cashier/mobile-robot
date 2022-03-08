# coding: utf-8
from server.obj_factory import bot_util
import json
import os

from aliyun.log import LogClient, PutLogsRequest, LogItem, GetLogsRequest, IndexConfig
import time



# 配置AccessKey、服务入口、Project名称、Logstore名称等相关信息。
# 阿里云访问密钥AccessKey。更多信息，请参见访问密钥。
# 阿里云账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM用户进行API访问或日常运维。

third_party_api = {
    "accessKeyId": "",
    "accessKey": "",
    "SecretId": "",
    "SecretKey": ""
}

if os.path.exists('../config.json'):
    with open('../config.json', 'r') as conf:
        config = json.loads(conf.read())
        third_party_api['accessKeyId'] = config['accessKeyId']
        third_party_api['accessKey'] = config['accessKey']
        third_party_api['SecretId'] = config['SecretId']
        third_party_api['SecretKey'] = config['SecretKey']

accessKeyId = third_party_api['accessKeyId']
accessKey = third_party_api['accessKey']
# 日志服务的域名。更多信息，请参见服务入口。此处以杭州为例，其它地域请根据实际情况填写。
endpoint = "cn-hongkong.log.aliyuncs.com"

# 创建日志服务Client。
client = LogClient(endpoint, accessKeyId, accessKey)

# Project名称。
project_name = "mobile-robot"
# Logstore名称
logstore_name = "internal"
# 查询语句。
query = "*| select dev,id from " + logstore_name
# 索引。
logstore_index = {'line': {
    'token': [',', ' ', "'", '"', ';', '=', '(', ')', '[', ']', '{', '}', '?', '@', '&', '<', '>', '/', ':', '\n', '\t',
              '\r'], 'caseSensitive': False, 'chn': False}, 'keys': {'dev': {'type': 'text',
                                                                             'token': [',', ' ', "'", '"', ';', '=',
                                                                                       '(', ')', '[', ']', '{', '}',
                                                                                       '?', '@', '&', '<', '>', '/',
                                                                                       ':', '\n', '\t', '\r'],
                                                                             'caseSensitive': False, 'alias': '',
                                                                             'doc_value': True, 'chn': False},
                                                                     'id': {'type': 'long', 'alias': '',
                                                                            'doc_value': True}}, 'log_reduce': False,
    'max_text_len': 2048}

# from_time和to_time表示查询日志的时间范围，Unix时间戳格式。
from_time = int(time.time()) - 3600
to_time = time.time() + 3600


# 创建Project。
def create_project():
    print("ready to create project %s" % project_name)
    client.create_project(project_name, project_des="")
    print("create project %s success " % project_name)
    time.sleep(60)


# 创建Logstore。
def create_logstore():
    print("ready to create logstore %s" % logstore_name)
    client.create_logstore(project_name, logstore_name, ttl=3, shard_count=2)
    print("create logstore %s success " % project_name)
    time.sleep(30)


# 创建索引。
def create_index():
    print("ready to create index for %s" % logstore_name)
    index_config = IndexConfig()
    index_config.from_json(logstore_index)
    client.create_index(project_name, logstore_name, index_config)
    print("create index for %s success " % logstore_name)
    time.sleep(60 * 2)


def put_logs(devices_id, log, level):
    print("ready to put logs for %s" % logstore_name)
    log_group = []
    log_item = LogItem()
    contents = [
        ('devices_id', devices_id),
        ('log', log),
        ('level', level)
    ]
    log_item.set_contents(contents)
    log_group.append(log_item)
    request = PutLogsRequest(project_name, logstore_name, "", "", log_group, compress=False)
    client.put_logs(request)
    # try:
    #     client.put_logs(request)
    # except Exception as ext:
    #     if bot_util.cast_work is not None:
    #         bot_util.cast_work({"do_work": "stop"})
    #     print("日志连接问题: %s" % ext)
    #     print("日志系统连接不上-------> 无法启动卡机，强制stop")
    print("put logs for %s success " % logstore_name)


# 通过SQL查询日志。
def get_logs():
    print("ready to query logs from logstore %s" % logstore_name)
    request = GetLogsRequest(project_name, logstore_name, from_time, to_time, query=query)
    response = client.get_logs(request)
    for log in response.get_logs():
        for k, v in log.contents.items():
            print("%s : %s" % (k, v))
        print("*********************")


if __name__ == '__main__':
    # 创建Project。
    # create_project()
    # 创建Logstore。
    # create_logstore()
    # 创建索引。
    # create_index()
    # 向Logstore写入数据。
    put_logs("7d19caab", "success put in")
    # 通过SQL查询日志。
    # get_logs()
