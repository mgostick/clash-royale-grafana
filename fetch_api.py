#!/usr/bin/env python

import argparse
import requests
import json
import os


def show_clan(args):
    data = read_cache(args.clan)
    data.pop('members', None)
    print(json.dumps(data, indent=2))


def show_member(args):
    data = read_cache(args.clan)
    for member in data['members']:
        if args.tag == member['tag']:
            print(json.dumps(member, indent=2))
            return


def create_telegraf_configs(args):
    data = read_cache(args.clan)
    os.system('rm /etc/telegraf/telegraf.d/*')
    for member in data['members']:
        tag = member['tag']
        telegraf_file = 'telegraf.d/{}.conf'.format(tag)
        with open(telegraf_file, 'w') as f:
            f.write('''[[inputs.exec]]
  command = "/home/swarm/therebellion/fetch_api.py member {}"
  timeout = "10s"
  name_override = "therebellion_members"
  data_format = "json"
  tag_keys = ["name"]
'''.format(tag))
        print('wrote {}'.format(telegraf_file))
    # telegraf needs a bump to pickup the new configs
    os.system('service telegraf reload')


def list_members(args):
    data = read_cache(args.clan)
    members = []
    for row in data['members']:
        name = row['name']
        tag = row['tag']
        members.append('{:<30} {}'.format(name, tag))
    for member in sorted(members, key=lambda s: s.lower()):
        print(member)


def update_cache(args):
    cache_file = '/tmp/{}.json'.format(args.clan)
    url = 'http://api.cr-api.com/clan/{}'.format(args.clan)
    resp = requests.get(url, headers={'auth': args.apikey})
    if resp.status_code == 200:
        data = json.loads(resp.text)
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
    print('wrote {}'.format(cache_file))


def read_cache(clan):
    cache_file = '/tmp/{}.json'.format(clan)
    with open(cache_file, 'r') as f:
        return json.load(f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clan', type=str, default='92090Y', help='clan tag')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_update = subparsers.add_parser('update', help='update stats and cache to tmp')
    parser_update.add_argument('-k', '--apikey', type=str, required=True,
                               help='api.cr-api.com api key (see http://docs.cr-api.com/#/authentication)')
    parser_update.set_defaults(func=update_cache)

    parser_clan = subparsers.add_parser('clan', help='show clan info')
    parser_clan.set_defaults(func=show_clan)

    parser_members = subparsers.add_parser('members', help='list all members')
    parser_members.set_defaults(func=list_members)

    parser_member = subparsers.add_parser('member', help='show member info')
    parser_member.add_argument('tag', type=str, help='clan member tag')
    parser_member.set_defaults(func=show_member)

    parser_telegraf = subparsers.add_parser('telegraf', help='write telegraf configs')
    parser_telegraf.set_defaults(func=create_telegraf_configs)

    args = parser.parse_args()
    args.func(args)
