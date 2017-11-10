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
    ap.add_argument('-o', '--output', help='output path')

    args = ap.parse_args()
    user_id = args.id
    if args.password:
        password = args.password
    else:
        password = getpass('Password for ' + args.id + ': ')

    DEFAULT_OUT_PATH = '_out'
    out_dir = args.output if args.output else DEFAULT_OUT_PATH
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    bc = ByeCha(user_id=user_id, password=password, out_dir=out_dir)
    bc.login()

    for room_id in bc.room_dat.keys():
        bc.get_all_chat(room_id)


if __name__ == '__main__':
    main()
