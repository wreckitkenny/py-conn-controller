import requests, pathlib, yaml, logging.config, logging, os, re
from itertools import product

logger = logging.getLogger(os.path.dirname(__file__).split("/")[-1])

def filter_connections(conn):
    fList = list()
    fDict = dict()
    clusterName = ""
    for c in conn:
        if c['originId'] in ["f3f22fd5-6195-47d4-a339-ef3d51c29b12","ab91f6c2-83d4-4232-8bf8-5498f68baddc"]: clusterName = c['value']
        if c['originId'] in ["a8ffd024-e326-425b-908f-5433c1f67ea5","0ba7e1a8-1e5d-4ad2-9e26-3ceeb9276422"]: fDict['namespace'] = c['value']
        if c['originId'] in ["386f6671-cd1d-4a54-81e5-d80e64183209","76734ae4-5c84-45c7-ad05-fc22077301cb"]: fDict['src_name'] = c['value']
        if c['originId'] in ["f2c4174c-5cac-479d-a5a5-b38b83ea778d","362c565e-efa8-45e9-aa6f-ca6d14ff1075"]: fDict['dst_name'] = c['value']
        if c['originId'] in ["18aa1412-42a6-4c0d-a4a7-9978f83f3d92","a0c70a2d-edf2-4293-860e-b7d6e197beb9"]: fDict['dst_port'] = c['value']

    for fKey in fDict: fDict[fKey] = fDict[fKey].split("\n")
    for combination in product(*fDict.values()):
        fList.append(dict(zip(fDict.keys(), combination)))

    return clusterName, fList

def load_config(config_path):
    config_file = pathlib.Path(config_path)
    with open(config_file) as cf:
        config = yaml.load(cf, Loader=yaml.SafeLoader)

    if "logging.yaml" in config_path:
        logging.config.dictConfig(config)

    return config

def request_checker(conn_list, main_task_key):
    # clusterConfig = {"cmc-test-ocp02":"http://127.0.0.1:5000/checkConnection"}
    clusterConfig = load_config("config/general.yaml")["clusterConfig"]
    headers = {'Content-Type': 'application/json'}
    output = "[HT-Platforms] Đây là hệ thống kiểm tra kết nối tự động dành riêng cho các dịch vụ trên K8S (comment */checkconn* để kiểm tra kết nối bằng tay).\n{code:bash}\n"
    notSupportedOutput = "\n"
    req = ""

    logger.info("[{}] Requesting pyConnChecker to check connections.".format(main_task_key))

    for conn in conn_list:
        clusterNameDictKey = conn.keys()
        for cluster in clusterNameDictKey:
            connections = conn[cluster]
            cluster = re.search("(cmc|gds|vnp|cldhn|cldhcm|mts|etl)-(test|prod)-(ocp|rke|oss|kaas)(-.*|\\d+)", cluster.lower()).group()

            if cluster not in clusterConfig:
                logger.warning("[{}] Cluster {} has not been supported in this version yet.".format(main_task_key, cluster))
                notSupportedOutput += "{}\nCluster {} has not been supported in the current version yet.\n".format("!" * 30, cluster)
                continue

            for connection in connections:
                connection['cluster_name'] = cluster
                url = clusterConfig[cluster] + "/checkConnection"
                try:
                    req = requests.post(url=url, json=connection, headers=headers, timeout=load_config("config/general.yaml")["requestTimeout"])
                    req.raise_for_status()
                    output += req.text + "\n"
                except requests.exceptions.RequestException as e:
                    logger.error("[{}] Failed to request {} (Exception: {}).".format(main_task_key, req.url, e))
                    output += "Failed to check connections on {}.\n".format(cluster)
    return output + notSupportedOutput

def parse_fields(json_request, request_type):
    mainTaskKey, subTaskKey, rawConnInfo = None, None, None
    connType = json_request['fields']['customfield_10816']['id']

    match request_type:
        case "auto":
            mainTaskKey = json_request['fields']['parent']['key']
            subTaskKey = json_request['key']
        case "manual":
            mainTaskKey = json_request['key']
            subTaskKey = ""
        case default:
            logger.warning("Cannot identify request type. Must be auto or manual. (Current request type: {})".format(request_type))

    match connType:
        case "10620":
            rawConnInfo = json_request['fields']['customfield_10817']
        case "10622":
            rawConnInfo = json_request['fields']['customfield_11461']
        case default:
            logger.warning("Cannot identify connection type id. Current connection type id: {}".format(connType))

    return mainTaskKey, subTaskKey, rawConnInfo