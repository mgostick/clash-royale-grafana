# clash-royale-grafana
Download stats from cr-api.com and create grafana graphs using telegraf

## Virtual Env
    python3 -m venv --without-pip .venv
    source .venv/bin/activate
    curl -s https://bootstrap.pypa.io/get-pip.py | python
    deactivate
    source .venv/bin/activate
    pip install -r requirements.txt

## Crontab
    # update the cache
    00,30 * * * * cd /path/to/dir; ./fetch_api.py -u -k <API_KEY> -c <CLAN_KEY>
    # update telegraf.d
    15,45 * * * * cd /path/to/dir; ./fetch_api.py -t -k <API_KEY> -c <CLAN_KEY>

Note: the udpate telegraf.d cron must be run as root as it reloads telegraf when new configs are created.
