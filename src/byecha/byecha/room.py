# -*- coding:utf-8 -*-

from enum import Enum


class RoomType(Enum):
    ''' room type of ChatWork (my/direct/group) '''
    MY = 1
    DIRECT = 2
    GROUP = 3


class Room(object):
    ''' room of ChatWork '''
    def __init__(self, myid, room_id, dic):
        ''' initializer '''
        self.room_id = room_id

        # save all key's values temporary
        # MY:
        #       c, f, lt, m, mid, mt, mute, r, s, t, tp
        # Direct:
        #       c, f, lt, m, mid, mute, r, t, tp
        # Group:
        #       c, f, ic, ln, lt, m, mid, mr, mute, n, p, r, t, tp,
        self.c = dic.get('c', None)
        self.f = dic.get('f', None)
        self.ic = dic.get('ic', None)   # icon path
        self.ln = dic.get('ln', None)
        self.lt = dic.get('lt', None)
        self.m = dic.get('m', {})
        self.mid = dic.get('mid', None)
        self.mr = dic.get('mr', [])
        self.mt = dic.get('mt', None)
        self.mute = dic.get('mute', None)  # mute flag
        self.n = dic.get('n', None)
        self.p = dic.get('p', None)
        self.r = dic.get('r', None)
        self.s = dic.get('s', None)
        self.t = dic.get('t', None)
        self.tp = dic.get('tp', None)

        if len(self.m) == 1 and myid in self.m.keys():
            self.room_type = RoomType.MY
            # TODO 自分の名前入れる
        elif len(self.m) == 2 and myid in self.m.keys():
            self.room_type = RoomType.DIRECT
            # TODO 相手の名前入れる
        elif len(self.m) > 0 and self.n:
            self.room_type = RoomType.GROUP
            self.name = self.n
        else:
            raise AttributeError(dic)
