import argparse
import configparser
import csv
import pathlib
from datetime import datetime, timedelta

import globus_helpers


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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create a timer to schedule data transfers")
    parser.add_argument("--name", help="Name for the data transfer timer job")
    parser.add_argument("--label", help="Friendly label for the timer job")
    parser.add_argument("--interval", help="Interval in seconds between timer jobs")
    parser.add_argument("--source-endpoint", help="UUID of source globus endpoint")
    parser.add_argument("--dest-endpoint", help="UUID of destination globus endpoint")
    parser.add_argument("--secrets-file", default=f"{str(pathlib.Path.home())}/.globus_secrets",
                        help="path for  globus client id and secret")
    parser.add_argument("--items-file", help="Name of CSV file to parse")

    args = parser.parse_args()

    inifile = args.secrets_file
    config = read_secrets_ini(inifile)
    client_id = get_client_id(config)
    client_secret = get_client_secret(config)
    csv_file = read_csv_file(args.items_file)

    # create the necessary globus objects
    authorizer = globus_helpers.create_globus_authorizer(client_id, client_secret)
    transfer_client = globus_helpers.create_transfer_client(authorizer)
    transfer_data = globus_helpers.create_transfer_data(transfer_client, args.source_endpoint, args.dest_endpoint, csv_file)
    timer_job = globus_helpers.create_timer_job(transfer_data, datetime.utcnow(), timedelta(seconds=args.interval), name=args.name)
    timer_client = globus_helpers.create_timer_client(authorizer)
    timer_result = timer_client.create_job(timer_job)
    print(timer_result)








