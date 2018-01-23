# clash-royale-grafana
Download stats from cr-api.com and create grafana graphs using telegraf

python3 -m venv --without-pip .venv
source .venv/bin/activate
curl -s https://bootstrap.pypa.io/get-pip.py | python
deactivate
source .venv/bin/activate

pip install -r requirements.txt
