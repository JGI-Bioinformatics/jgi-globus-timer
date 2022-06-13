from jgi_globus_timer import __version__, main
import pytest


def test_version():
    assert __version__ == '0.1.0'


def test_error_if_no_credential_file_exists():
    no_inifile = "/path/to/.inifile"
    with pytest.raises(FileNotFoundError):
        config = main.read_secrets_ini(no_inifile)