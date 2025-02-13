from jira import JIRA, exceptions
import logging, os

logger = logging.getLogger(os.path.dirname(__file__).split("/")[-1])

def login_jira():
    jira = JIRA(server=os.environ['JIRA_URL'], token_auth=os.environ['JIRA_TOKEN'])
    return jira

def add_jira_comment(issue_key, comment, jira=login_jira()):
    logger.info("[{}] Adding a comment to Jira ticket.".format(issue_key))
    try:
        issue = jira.issue(issue_key)
        commentResponse = jira.add_comment(issue, comment)
        return commentResponse.raw
    except exceptions.JIRAError as e:
        print("Issue is not existing: {}".format(e))
    return ""
