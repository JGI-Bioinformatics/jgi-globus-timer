import datetime

import globus_sdk
from globus_sdk import TimerJob

TRANSFER_SCOPE = "urn:globus:auth:scope:transfer.api.globus.org:all"
TIMER_CLIENT_ID = "524230d7-ea86-4a52-8312-86065a9e0417"
TIMER_SCOPE = f"https://auth.globus.org/scopes/{TIMER_CLIENT_ID}/timer"


def get_token_response(client_id, client_secret):
    scopes = [TRANSFER_SCOPE, TIMER_SCOPE]
    client = globus_sdk.ConfidentialAppAuthClient(client_id=client_id, client_secret=client_secret)
    return client.oauth2_client_credentials_tokens(requested_scopes=scopes)


def get_transfer_token(token_response):
    return token_response.by_resource_server["transfer.api.globus.org"]["access_token"]


def get_timer_token(token_response):
    return token_response.by_resource_server[TIMER_CLIENT_ID]["access_token"]


def create_globus_authorizer(token):
    """
    Authenticate with Globus Client Credentials Authentication flow

    examples located here: https://globus-sdk-python.readthedocs.io/en/stable/examples/client_credentials.html
    :param client_id:  UUID for the client generated by registering to Globus Auth Service
    :param client_secret:  Client secret used to generate oauth2 tokens
    :return: globus_sdk.AccessTokenAuthorizer
    """
    return globus_sdk.AccessTokenAuthorizer(token)


def create_transfer_client(authorizer):
    """
    Creates a transfer client object from globus SDK
    :param authorizer: globus_sdk.AccessTokenAuthorizer
    :return: globus_sdk.TransferClient
    """
    return globus_sdk.TransferClient(authorizer=authorizer)


def create_timer_client(authorizer):
    return globus_sdk.TimerClient(authorizer=authorizer)


def strtobool(value):
    boolstr = value.lower()
    if boolstr == "true":
        return True
    elif boolstr == "false":
        return False


def create_transfer_data(transfer_client, src_endpoint, dest_endpoint, csv_reader, deadline=None):
    if deadline is None:
        now = datetime.datetime.utcnow()
        deadline = now + datetime.timedelta(days=10)
    tdata = globus_sdk.TransferData(transfer_client,
                                    src_endpoint,
                                    dest_endpoint,
                                    sync_level=0,
                                    preserve_timestamp=True,
                                    deadline=str(deadline))
    for row in csv_reader:
        tdata.add_item(csv_reader[row]["source_path"],
                       csv_reader[row]["destination_path"],
                       recursive=strtobool(csv_reader[row]["recursive"]))
    return tdata


#------------------------- Timer Job Interface -------------------------------------
# Supports the CRUD features needed for timer jobs
def create_timer_job_object(transfer_data, start, interval, name):
    scope = "https://auth.globus.org/scopes/actions.globus.org/transfer/transfer"
    return TimerJob.from_transfer_data(transfer_data, start, interval, name=name, scope=scope)


def create_timer_job(timer_client, timer_job):
    timer_response = timer_client.create_job(timer_job)
    assert timer_response.http_status == 201
    return timer_response["job_id"]


def delete_timer_job(timer_client, job_id):
    response = timer_client.delete_job(job_id)
    assert response.http_status == 200
    return response.text


def list_timer_jobs(timer_client):
    response = timer_client.list_jobs()
    assert response.http_status == 200
    return response.text


def get_timer_job(timer_client, job_id):
    response = timer_client.get_job(job_id)
    assert response.http_status == 200
    return response.text


def update_timer_job(timer_client, job_id, update_params):
    response = timer_client.update_job(job_id, update_params)
    assert response.http_status == 200
    return response.text