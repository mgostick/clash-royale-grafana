#!/usr/bin/env python

import argparse
import requests
import json
import os
from terminaltables import SingleTable


def color(s: str, c: int) -> str:
    return '\x1b[6;{}m{}\x1b[0m'.format(c, s)


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
    clan = args.clan
    data = read_cache(clan)
    os.system('rm ./telegraf.d/{}_*'.format(clan))
    for member in data['members']:
        tag = member['tag']
        telegraf_file = 'telegraf.d/{}_{}.conf'.format(clan, tag)
        with open(telegraf_file, 'w') as f:
            f.write('''[[inputs.exec]]
  command = "/home/swarm/therebellion/fetch_api.py -c {} member {}"
  timeout = "10s"
  name_override = "therebellion_members"
  data_format = "json"
  tag_keys = ["name"]
'''.format(clan, tag))
        print('wrote {}'.format(telegraf_file))
    # telegraf needs a bump to pickup the new configs
    os.system('service telegraf reload')


def list_members(args):
    data = read_cache(args.clan)

    table = []
    table.append(['Name', 'Tag', 'Role', 'Clan Crown Chests',
                  'Donations', 'Donations %', 'Donations +/-'])

    for row in data['members']:
        name = row['name']
        tag = row['tag']

        def role():
            x = row['role'] or 0
            try:
                return {
                    "leader": color("Leader", 34),
                    "coLeader": color("Co-leader", 36),
                    "elder": color("Elder", 33),
                    "member": "Member",
                }[x]
            except KeyError:
                return "Unknown"

        def donations():
            x = row['donations'] or 0
            if x <= 0:
                return color(x, 31)
            return x

        donationsPercent = row['donationsPercent'] or 0
        donationsDelta = row['donationsDelta'] or 0

        def clanChestCrowns():
            x = row['clanChestCrowns'] or 0
            if x <= 0:
                return color(x, 31)
            if x >= 32:
                return color(x, 32)
            return color(x, 0)

        table.append([
            name,
            tag,
            role(),
            clanChestCrowns(),
            donations(),
            donationsPercent,
            donationsDelta,
        ])

    print(SingleTable(table).table)


def update_cache(args):
    cache_file = '/tmp/{}.json'.format(args.clan)
    url = 'http://api.cr-api.com/clan/{}'.format(args.clan)
    resp = requests.get(url, headers={'auth': args.apikey})
    if resp.status_code == 200:
        data = json.loads(resp.text)
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
    print('wrote {}'.format(cache_file))


def read_cache(clan: str):
    cache_file = '/tmp/{}.json'.format(clan)
    with open(cache_file, 'r') as f:
        return json.load(f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clan', type=str,
                        default='92090Y', help='clan tag')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_update = subparsers.add_parser(
        'update', help='update stats and cache to tmp')
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

    parser_telegraf = subparsers.add_parser(
        'telegraf', help='write telegraf configs')
    parser_telegraf.set_defaults(func=create_telegraf_configs)

    args = parser.parse_args()
    args.func(args)
