import pytest

from jgi_globus_timer import __version__, main, globus_helpers



def test_version():
    assert __version__ == '0.1.0'


def test_error_if_no_credential_file_exists():
    no_inifile = "/path/to/.inifile"
    with pytest.raises(FileNotFoundError):
        config = main.read_secrets_ini(no_inifile)


def test_error_if_credentials_are_not_set(tmp_path):
    config_file_contents = """
    [globus]
    client_id=
    """
    config_path = tmp_path / ".globus_secrets"
    config_path.write_text(config_file_contents)
    config = main.read_secrets_ini(config_path.as_posix())
    with pytest.raises(KeyError):
        main.get_client_secret(config)
    with pytest.raises(ValueError):
        main.get_client_id(config)


def test_csv_file_reader(tmp_path):
    csv_file_contents = """/global/cfs/cdirs/seqfs/ornl/global,/global,true"""
    csv_file_path = tmp_path / "tahoma-manifest.csv"
    csv_file_path.write_text(csv_file_contents)
    csv_reader = main.read_csv_file(csv_file_path.as_posix())
    for row in csv_reader:
        assert csv_reader[row]["source_path"] == "/global/cfs/cdirs/seqfs/ornl/global"
        assert csv_reader[row]["destination_path"] == "/global"
        assert csv_reader[row]["recursive"] == "true"


def test_transfer_data_body_creation():
    src_endpoint = "go#ep1"
    dest_endpoint = "go#ep2"
    src = "/path/to/src/dir"
    dest = "/path/to/dest/dir"
    csv_reader = {
        0: {
            "source_path": src,
            "destination_path": dest,
            "recursive": "true"
        }
    }
    transfer_data = globus_helpers.create_transfer_data(src_endpoint, dest_endpoint, csv_reader)

    assert transfer_data["source_endpoint_id"] == src_endpoint
    assert transfer_data["destination_endpoint_id"] == dest_endpoint

    transfer_items = transfer_data["transfer_items"]
    assert len(transfer_items) == 1

    transfer = transfer_items.pop()
    assert transfer["source_path"] == src
    assert transfer["destination_path"] == dest
    assert transfer["recursive"] == True




