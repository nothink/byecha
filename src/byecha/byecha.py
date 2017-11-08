#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from byecha.byecha import ByeCha

import os
from argparse import ArgumentParser
from getpass import getpass


def main():
    ap = ArgumentParser()
    ap.add_argument('id', help='your chatwork id')
    ap.add_argument('-p', '--password', help='your chatwork password')

    args = ap.parse_args()
    user_id = args.id
    if args.password:
        password = args.password
    else:
        password = getpass('Password for ' + args.id + ': ')

    OUT_PATH = '_out'
    if not os.path.exists(OUT_PATH):
        os.makedirs(OUT_PATH)

    bc = ByeCha(user_id=user_id, password=password, out_dir=OUT_PATH)
    bc.login()

    for room in bc.rooms:
        bc.get_all_chat(room.room_id)


if __name__ == '__main__':
    main()
