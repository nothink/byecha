#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from byecha.byecha import ByeCha

from argparse import ArgumentParser
from getpass import getpass


def main():
    ap = ArgumentParser()
    ap.add_argument('id',
                    help='your chatwork id')
    ap.add_argument('-p', '--password',
                    help='your chatwork password')

    args = ap.parse_args()
    user_id = args.id
    if args.password:
        password = args.password
    else:
        password = getpass('Password for ' + args.id + ': ')

    bc = ByeCha(user_id=user_id, password=password)
    bc.login()


if __name__ == '__main__':
    main()
