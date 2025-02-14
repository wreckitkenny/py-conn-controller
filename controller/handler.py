import json, logging, os
from .utils import filter_connections, request_checker
from .jira import add_jira_comment

logger = logging.getLogger(os.path.dirname(__file__).split("/")[-1])

def handle_raw_request(main_task_key, raw_conn_info):
    connInfoDict = json.loads(raw_conn_info)

    del connInfoDict['configurationId']

    connInfoList = list()
    for key in connInfoDict.keys():
        connInfoList.append(connInfoDict[key]['fields'])

    parentConnList = list()
    parentConnDict = dict()
    for conn in connInfoList:
        clusterName, connections = filter_connections(conn)
        if clusterName not in parentConnDict:
            parentConnDict[clusterName] = [connections]
        else:
            parentConnDict[clusterName].append(connections)
    parentConnList.append(parentConnDict)

    response = request_checker(parentConnList, main_task_key)
    if response != "":
        jiraCommentRes = add_jira_comment(issue_key=main_task_key, comment=response + "{code}")
        user, body = jiraCommentRes['author']['displayName'], jiraCommentRes['body']
        # print("A comment is added to Jira [{}] by [{}]:\n{}".format(main_task_key, user, body))
        return "A comment is added to Jira [{}] by [{}]:\n{}".format(main_task_key, user, body)
    return "OK"