# -*- coding:utf-8 -*-

from ..const import *

import re


class Chat(object):
    def __init__(self, source, contact_list):
        self._chat = source
        self._html = None
        self._contact_list = contact_list

    @property
    def html_string(self):
        if not self._html:
            tmp_html = self._chat
            tmp_html = self._escape_break(tmp_html)
            tmp_html = self._escape_uri(tmp_html)
            tmp_html = self._render_to_link(tmp_html)
            self._html = tmp_html
        return self._html

    def _escape_break(self, src):
        return src.replace('\n', '<br />')

    def _escape_uri(self, src):
        regex = r"(https?:\/\/[\w\/:%#\$&\?\(\)~\.=\+\-]+)"
        repl = r'<a href="\1">\1</a>'
        return re.sub(regex, repl, src)

    def _render_to_link(self, src):
        tmp_str = src
        aid_list = []
        regex = r"\[To:(\d*)\]"
        match = re.findall(regex, tmp_str)
        for m in match:
            aid = str(m)
            if aid in aid_list:
                continue

            if aid in self._contact_list:
                av = self._contact_list[aid]['av']
                img_link = AVATAR_BASE_URL + av
            else:
                img_link = '{{ static_url("images/unknown-user.png") }}'

            link_str = '<span class="tolink"><img src="'
            link_str += img_link
            link_str += '" width="16" height="16"></span>'

            tmp_str = tmp_str.replace('[To:' + aid + ']', link_str)
            aid_list.append(aid)
        return tmp_str
