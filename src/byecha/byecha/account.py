# -*- coding:utf-8 -*-


class Account(object):
    ''' account of ChatWork '''
    def __init__(self, aid, dic):
        ''' initializer '''
        # save all key's values temporary
        self.aid = dic.get('aid', None)
        self.av = dic.get('av', None)
        self.avid = dic.get('avid', None)
        self.cv = dic.get('cv', None)
        self.cwid = dic.get('cwid', None)
        self.dp = dic.get('dp', None)
        self.fb = dic.get('fb', None)
        self.gid = dic.get('gid', None)
        self.is_deleted = dic.get('is_deleted', None)
        self.mrid = dic.get('mrid', None)
        self.name = dic.get('name', None)
        self.nm = dic.get('nm', None)
        self.onm = dic.get('onm', None)
        self.rid = dic.get('rid', None)
        self.sp = dic.get('sp', None)
        self.tw = dic.get('tw', None)
        self.ud = dic.get('ud', None)

        self.account_id = aid
        if self.aid == self.account_id:
            raise ValueError('aid mismatch')
