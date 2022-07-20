import argparse
import configparser
import csv
import pathlib
import json

from datetime import datetime, timedelta
from jgi_globus_timer import globus_helpers


def read_secrets_ini(inifile):
    """
    Reads a ini file that contains the client id and secrets. This is used in lieu of
    passing the credentials via the command line.
    :param inifile:  filepath to the configuration file
    :return: configparser.ConfigParser
    """
    conf = configparser.ConfigParser()
    try:
        conf.read_file(open(inifile))
    except FileNotFoundError as e:
        raise FileNotFoundError("Cannot locate configuration file. Please create one either in your homedir or provide"
                                "a path")
    return conf


def get(config, section, value):
    """
    Getter function for ini config

    :param config:  configparser.ConfigParser
    :param section: ini file section
    :param value:  configuration key to extract value from
    :return:
    """
    try:
        entry = config[section][value]
    except KeyError as e:
        raise KeyError(f"missing section: {section}")
    if not entry:
        raise ValueError(f"missing value: {entry}")
    return entry


def get_client_id(config):
    return get(config, "globus", "client_id")


def get_client_secret(config):
    return get(config, "globus", "client_secret")


def read_csv_file(csv_file):
    csv_file_contents = {}
    with open(csv_file, newline='') as csvfile:
        fieldnames = ["source_path", "destination_path", "recursive"]
        reader = csv.DictReader(csvfile, fieldnames=fieldnames)
        for i, row in enumerate(reader):
            csv_file_contents[i] = {
                "source_path": row["source_path"],
                "destination_path": row["destination_path"],
                "recursive": row["recursive"]
            }
    return csv_file_contents


def print_json(json_str):
    response = json.loads(json_str)
    print(json.dumps(response, indent=4, sort_keys=True))


def main():

    parser = argparse.ArgumentParser(description="Create or delete a Globus timer")
    parser.add_argument("--secrets-file", default=f"{str(pathlib.Path.home())}/.globus_secrets",
                        help="path for  globus client id and secret")
    subparsers = parser.add_subparsers(dest="command", help="Create a timer to schedule data transfers")

    transfer_parser = subparsers.add_parser("transfer")
    transfer_parser.add_argument("--name", help="Name for the data transfer timer job")
    transfer_parser.add_argument("--label", help="Friendly label for the timer job")
    transfer_parser.add_argument("--interval", default=300, help="Interval in seconds between timer jobs")
    transfer_parser.add_argument("--source-endpoint", help="UUID of source globus endpoint")
    transfer_parser.add_argument("--dest-endpoint", help="UUID of destination globus endpoint")
    transfer_parser.add_argument("--items-file", help="Name of CSV file to parse")
    transfer_parser.add_argument("--stop-after-n", dest="n_runs", default=None, help="Stop after N timer runs")

    list_parser = subparsers.add_parser("list")

    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("job_id")

    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("timer_id")

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("job_id")
    update_parser.add_argument("--name", help="Name for the data transfer timer job")
    update_parser.add_argument("--label", help="Friendly label for the timer job")
    update_parser.add_argument("--interval", help="Interval in seconds between timer jobs")

    args = parser.parse_args()

    # parse for the client id and client secret
    inifile = args.secrets_file
    config = read_secrets_ini(inifile)
    client_id = get_client_id(config)
    client_secret = get_client_secret(config)

    # create the necessary globus tokens
    token_response = globus_helpers.get_token_response(client_id, client_secret)
    transfer_token = globus_helpers.get_transfer_token(token_response)
    timer_token = globus_helpers.get_timer_token(token_response)

    # create the authorizers from their respective tokens
    transfer_authorizer = globus_helpers.create_globus_authorizer(transfer_token)
    timer_authorizer = globus_helpers.create_globus_authorizer(timer_token)

    # create the clients
    transfer_client = globus_helpers.create_transfer_client(transfer_authorizer)
    timer_client = globus_helpers.create_timer_client(timer_authorizer)

    if args.command == "delete":
        print_json(globus_helpers.delete_timer_job(timer_client, args.timer_id))
    elif args.command == "list":
        print_json(globus_helpers.list_timer_jobs(timer_client))
    elif args.command == "get":
        print_json(globus_helpers.get_timer_job(timer_client, args.job_id))
    elif args.command == "update":
        update_params = {}
        try:
            update_params["name"] = args.name
        except AttributeError:
            pass
        try:
            update_params["label"] = args.label
        except AttributeError:
            pass
        try:
            update_params["interval"] = args.interval
        except AttributeError:
            pass
        print(globus_helpers.update_timer_job(timer_client, args.job_id, update_params))
    elif args.command == "transfer":
        inifile = args.secrets_file
        config = read_secrets_ini(inifile)
        client_id = get_client_id(config)
        client_secret = get_client_secret(config)
        csv_file = read_csv_file(args.items_file)
        transfer_data = globus_helpers.create_transfer_data(args.source_endpoint,
                                                            args.dest_endpoint,
                                                            csv_file)
        if args.n_runs is None:
            interval = timedelta(minutes=args.interval)
        else:
            interval = None
        timer_job = globus_helpers.create_timer_job_object(transfer_data,
                                                           datetime.utcnow(),
                                                           interval,
                                                           args.name,
                                                           args.n_runs)
        job_id = globus_helpers.create_timer_job(timer_client, timer_job)
        print(f"Created job Timer Job ID: {job_id}")
