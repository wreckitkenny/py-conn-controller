import logging, os
from controller import handle_raw_request, load_config, parse_fields
from flask import Flask, request

app = Flask(__name__)
logger = logging.getLogger(os.path.dirname(__file__).split("/")[-1])

@app.route("/ping")
def ping(): return "pong!"

@app.post("/autoCheck")
def auto_check_connection():
    jsonRequest = request.get_json()
    mainTaskKey, subTaskKey,rawConnInfo = parse_fields(jsonRequest, "auto")
    logger.info("[{}] Handling a request that automatically check connections.".format(subTaskKey))
    return handle_raw_request(mainTaskKey, rawConnInfo)

@app.post("/manualCheck")
def manual_check_connection():
    jsonRequest = request.get_json()
    mainTaskKey, subTaskKey,rawConnInfo = parse_fields(jsonRequest, "manual")
    logger.info("[{}] Handling a request that manually check connections.".format(mainTaskKey))
    return handle_raw_request(mainTaskKey, rawConnInfo)

if __name__ == '__main__':
    log = logging.getLogger('werkzeug')
    log.disabled = True
    load_config("config/logging.yaml")
    app.run(host='0.0.0.0', port=5000)