# clash-royale-grafana
Download stats from cr-api.com and create grafana graphs using telegraf

## Requirements
Telegraf must be installed to collect the stats

`https://docs.influxdata.com/telegraf/v1.5/introduction/installation/`

InfluxDB must be installed to store the stats

`https://docs.influxdata.com/influxdb/v1.4/introduction/installation/`

Grafana must be installed to display the stats

`http://docs.grafana.org/installation/`

## Virtual Env
    python3 -m venv --without-pip .venv
    source .venv/bin/activate
    curl -s https://bootstrap.pypa.io/get-pip.py | python
    deactivate
    source .venv/bin/activate
    pip install -r requirements.txt

## Crontab
    # update the cache
    00,30 * * * * cd /path/to/dir; .venv/bin/python3 fetch_api.py -c <CLAN_KEY> update -k <API_KEY>
    # update telegraf.d
    15,45 * * * * cd /path/to/dir; .venv/bin/python3 fetch_api.py -c <CLAN_KEY> telegraf

Before running the update telegraf.d command first create a symlink to your telegraf.d directory

    ln -s /etc/telegraf/telegraf.d .

The udpate telegraf.d cron must be run as root as it reloads telegraf when new configs are created.

## cr-api.com API KEY
See `http://docs.cr-api.com/#/authentication`
