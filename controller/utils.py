import requests, pathlib, yaml, logging.config, logging, os, re

logger = logging.getLogger(os.path.dirname(__file__).split("/")[-1])

def load_config(config_path):
    config_file = pathlib.Path(config_path)
    with open(config_file) as cf:
        config = yaml.load(cf, Loader=yaml.SafeLoader)

    if "logging.yaml" in config_path:
        logging.config.dictConfig(config)

    return config

def filter_connections(conn):
    fDict = dict()
    clusterName = ''
    for c in conn:
        if c['originId'] == "f3f22fd5-6195-47d4-a339-ef3d51c29b12": clusterName = c['value']
        if c['originId'] == "a8ffd024-e326-425b-908f-5433c1f67ea5": fDict['namespace'] = c['value']
        if c['originId'] == "386f6671-cd1d-4a54-81e5-d80e64183209": fDict['src_name'] = c['value']
        if c['originId'] == "f2c4174c-5cac-479d-a5a5-b38b83ea778d": fDict['dst_name'] = c['value']
        if c['originId'] == "18aa1412-42a6-4c0d-a4a7-9978f83f3d92": fDict['dst_port'] = c['value']
    return clusterName, fDict

def request_checker(conn_list, main_task_key):
    # clusterConfig = {"cmc-test-ocp02":"http://127.0.0.1:5000/checkConnection"}
    clusterConfig = load_config("config/general.yaml")["clusterConfig"]
    headers = {'Content-Type': 'application/json'}
    output = "[HT-Platforms] Đây là hệ thống kiểm tra kết nối tự động dành riêng cho các dịch vụ trên K8S (comment */checkconn* để kiểm tra kết nối bằng tay).\n{code:bash}\n"

    logger.info("[{}] Requesting pyConnChecker to check connections.".format(main_task_key))

    for conn in conn_list:
        clusterNameList = conn.keys()
        for cluster in clusterNameList:
            connections = conn[cluster]
            cluster = re.search("(cmc|gds|vnp|cldhn|cldhcm|mts|etl)-(test|prod)-(ocp|rke|oss|kaas)(-.*|\\d+)", cluster.lower()).group()

            if cluster not in clusterConfig:
                logger.warning("[{}] Cluster {} has not been supported in this version yet.".format(main_task_key, cluster))
                output += "{}\nCluster {} has not been supported in the current version yet.\n".format("!" * 30, cluster)
                break

            for connection in connections:
                connection['cluster_name'] = cluster
                req = requests.post(url=clusterConfig[cluster], json=connection, headers=headers, timeout=60)
                if req.status_code != 200:
                    logger.error("[{}] Failed to request {}.".format(main_task_key, clusterConfig[cluster]))
                    output += "Failed to check connections on {}.\n".format(cluster)
                    break
                output += req.text + "\n"
    return output