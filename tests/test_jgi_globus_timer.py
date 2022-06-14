from jgi_globus_timer import __version__, main
import pytest


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