# -*- coding:utf-8 -*-


class BaseModel(object):

    _all_dic = None

    ''' Base Model '''
    def __init__(self, uid, dic):
        ''' initializer '''
        self.uid = uid
        # keep all values in dic
        for key in dic.keys():
            setattr(self, key, dic.get(key, None))

    @classmethod
    def get_all(cls, all_dic=None):
        if not cls._all_dic and all_dic:
            cls._all_dic = []
            for aid in self.contact_dat.keys():
                cls._contact_list.append(cls(dic=all_dic[uid],
                                             uid=uid))
        elif not cls._contact_list:
            raise NotImplementedError('give me json!')
        return cls._contact_list
