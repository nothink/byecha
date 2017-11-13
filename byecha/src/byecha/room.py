# -*- coding:utf-8 -*-

from .basemodel import BaseModel

from enum import Enum


class RoomType(Enum):
    ''' room type of ChatWork (my/direct/group) '''
    MY = 1
    DIRECT = 2
    GROUP = 3


class Room(BaseModel):
    ''' room of ChatWork '''
    # TODO Obsolete!

    _room_list = None

    def __init__(self, dic, room_id, myid):
        ''' initializer '''
        # MY:
        #       c, f, lt, m, mid, mt, mute, r, s, t, tp
        # Direct:
        #       c, f, lt, m, mid, mute, r, t, tp
        # Group:
        #       c, f, ic, ln, lt, m, mid, mr, mute, n, p, r, t, tp,
        super().__init__(dic)

        self.room_id = room_id
        self.myid = myid

    @property
    def room_type(self):
        if len(self.m) == 1 and self.myid in self.m.keys():
            return RoomType.MY
        elif len(self.m) == 2 and self.myid in self.m.keys():
            return RoomType.DIRECT
        elif len(self.m) > 0 and self.n:
            return RoomType.GROUP
        else:
            raise AttributeError('Unknown room type')

    @classmethod
    def rooms(cls, json):
        if not cls._room_list and json:
            room_list = []
            for room_id in self.room_dat.keys():
                room_list.append(cls(dic=self.room_dat[room_id],
                                     room_id=room_id,
                                     myid=self.myid))
            self._room_list = room_list
        return self._room_list
