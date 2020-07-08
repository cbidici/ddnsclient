import os
import requests
import tempfile

_GOOGLE_CHECK_IP = "https://domains.google.com/checkip"
_GOOGLE_DOMAINS_NIC_UPDATE = "https://{}:{}@domains.google.com/nic/update"
_DATA_FILE = "ddnsclient.dat"
_DATA_DIR = "ddnsclient"
_CURRENT_IP = ""
_CONFIG = dict()


def _create_path_if_not_exists(path):
    os.makedirs(path, mode=0o776, exist_ok=True)


def _create_file_if_not_exists(file_path):
    f = open(file_path, "a+")
    f.close()


def _create_data_file_if_not_exists():
    _create_path_if_not_exists(_get_data_file_dir_path())
    _create_file_if_not_exists(_get_data_file_path())


def _get_data_file_dir_path():
    return os.path.join(tempfile.gettempdir(), _DATA_DIR)


def _get_data_file_path():
    return os.path.join(_get_data_file_dir_path(), _DATA_FILE)


def _load_config():
    global _CONFIG
    _CONFIG = {
        "googledomains": [
            {
                "username": "xxxx",
                "password": "xxxx",
                "hostname": "www.com",
            },
            {
                "username": "xxxx",
                "password": "xxxx",
                "hostname": "ccc.com",
            }
        ]
    }


def _get_url(url, params=None):
    return requests.get(url, params=params).content.decode("utf-8")


def _get_last_ip():
    with open(_get_data_file_path(), "r") as f:
        return f.readline()


def _find_current_ip():
    global _CURRENT_IP
    _CURRENT_IP = _get_url(_GOOGLE_CHECK_IP)
    return _CURRENT_IP


def _update_required():
    return _find_current_ip() != _get_last_ip()


def _initialize():
    _create_data_file_if_not_exists()
    _load_config()


def _update_google_dns(hostname, username, password, ipaddress):
    result = _get_url(
        _GOOGLE_DOMAINS_NIC_UPDATE.format(username, password),
        {"hostname": hostname, "ip": ipaddress},
    )
    print("Hostname {} IP {} Update Result {}".format(hostname, ipaddress, result))


def _update_dns(protocol, domains):
    if protocol == "googledomains":
        for domain in domains:
            _update_google_dns(
                domain["hostname"], domain["username"], domain["password"], _CURRENT_IP
            )
    else:
        raise NotImplementedError()


def _write_current_ip():
    with open(_get_data_file_path(), "w") as f:
        f.write(_CURRENT_IP)


def _process_current_ip():
    for config in _CONFIG:
        _update_dns(config, _CONFIG[config])
    _write_current_ip()


def update_dynaminc_dns():
    _initialize()
    if _update_required():
        _process_current_ip()


def _main():
    update_dynaminc_dns()


if __name__ == "__main__":
    _main()
