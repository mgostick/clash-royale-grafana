#!/usr/bin/env python

import argparse
import requests
import json
import hashlib
import time
import os


def download_stats(member=None):
    data = read_stats()
    members = {}
    if member is None:
        del data['members']
    else:
        for row in data['members']:
            if member == hashlib.sha256(row['name'].encode('utf-8')).hexdigest():
                members = row
                break
        data = members
    print(json.dumps(data, indent=2))


def create_telegraf_configs():
    data = read_stats()
    for row in data['members']:
        hash = hashlib.sha256(row['name'].encode('utf-8')).hexdigest()
        telegraf_file = '/etc/telegraf/telegraf.d/' + hash + '.conf'
        f = open(telegraf_file, 'w')
        f.write('[[inputs.exec]]\n')
        f.write('  command = "/home/swarm/therebellion/fetch_api.py -m \'' + hash + '\'"\n')
        f.write('  timeout = "10s"\n')
        f.write('  name_override = "therebellion_members"\n')
        f.write('  data_format = "json"\n')
        f.write('  tag_keys = ["name"]\n')
        f.close()
    # telegraf needs a bump to pickup the new configs
    os.system('service telegraf reload')


def update_stats(apikey):
    cache_file = '/tmp/therebellion_stats.json'
    url = 'http://api.cr-api.com/clan/92090Y'
    resp = requests.get(url, headers = {'auth': apikey})
    if resp.status_code == 200:
        data = json.loads(resp.text)
        f = open(cache_file, 'w')
        f.write(json.dumps(data))
        f.close()
    else:
        print(resp)


def read_stats():
    cache_file = '/tmp/therebellion_stats.json'
    f = open(cache_file, 'r')
    data = json.loads(f.read())
    f.close()
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--member", type=str, default=None, help="Pull stats for specific member (sha256)")
    parser.add_argument("-t", "--telegraf", default=False, action='store_true', help="Create telegraf configs")
    parser.add_argument("-u", "--update", default=False, action='store_true', help="Update the cache")
    parser.add_argument("-k", "--apikey", type=str, default=None, help="Update the cache")
    args = parser.parse_args()

    if args.telegraf:
        create_telegraf_configs()
    elif args.update:
        update_stats(args.apikey)
    else:
        download_stats(args.member)
