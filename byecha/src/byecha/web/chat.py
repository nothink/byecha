# -*- coding:utf-8 -*-

from ..const import *

import os
import time
import re


class Chat(object):
    def __init__(self, source, contact_list):
        self._chat = source
        self._html = None
        self._contact_list = contact_list

    def _get_avatar(self, aid):
        if aid in self._contact_list:
            av = self._contact_list[aid]['av']
            img_url = AVATAR_BASE_URL + av
        else:
            img_url = os.path.join(STATIC_BASE,
                                   AVATAR_PATH,
                                   DEFAULT_AVATAR)
        return img_url

    def _get_name(self, aid):
        if aid in self._contact_list:
            return self._contact_list[aid]['nm']
        else:
            return 'コンタクトなし (ID:' + aid + ')'

    @property
    def html_string(self):
        if not self._html:
            tmp_html = self._chat
            tmp_html = self._escape_break(tmp_html)
            tmp_html = self._escape_uri(tmp_html)
            tmp_html = self._render_to_link(tmp_html)
            tmp_html = self._render_to_reply(tmp_html)
            tmp_html = self._render_quote(tmp_html)
            tmp_html = self._render_info(tmp_html)
            tmp_html = self._render_deleted(tmp_html)
            tmp_html = self._render_sytem_message(tmp_html)
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

            link_str = '<span class="tolink"><img src="'
            link_str += self._get_avatar(aid)
            link_str += '" width="16" height="16" data-aid="'
            link_str += aid
            link_str += '"></span>'

            tmp_str = tmp_str.replace('[To:' + aid + ']', link_str)

            aid_list.append(aid)
        return tmp_str

    def _render_to_reply(self, src):
        tmp_str = src
        reply_list = []
        regex = r"\[rp aid=(\d*) to=(\d*)-(\d*)\]"
        match = re.findall(regex, tmp_str)
        for m in match:
            aid = str(m[0])
            room_id = str(m[1])
            message_id = str(m[2])

            if (room_id, message_id) in reply_list:
                continue

            link_str = '<span class="relink" data-reid="'
            link_str += room_id + '-' + message_id
            link_str += '"><img src="'
            link_str += self._get_avatar(aid)
            link_str += '" width="16" height="16" data-aid="'
            link_str += aid
            link_str += '"></span>'

            tmp_str = tmp_str.replace('[rp aid=' + aid +
                                      ' to=' + room_id +
                                      '-' + message_id + ']', link_str)

            reply_list.append((room_id, message_id))
        return tmp_str

    def _render_quote(self, src):
        tmp_str = src
        tmp_str = self._render_quote_pre_long(tmp_str)
        tmp_str = self._render_quote_pre_short(tmp_str)
        tmp_str = self._render_quote_post(tmp_str)
        return tmp_str

    def _render_quote_pre_long(self, src):
        tmp_str = src
        quote_list = []
        regex = r"\[qt\]\[qtmeta aid=(\d*) time=(\d*)\]"
        match = re.findall(regex, tmp_str)
        for m in match:
            aid = str(m[0])
            epoch = str(m[1])

            if (aid, epoch) in quote_list:
                continue

            q_str = '<blockquote>\n'
            q_str += '<div class="meta"><img src="'
            q_str += self._get_avatar(aid)
            q_str += '" width="12" height="12" /><b>'
            q_str += self._get_name(aid)
            q_str += '</b> '
            q_str += time.strftime('%Y年%-m月%-d日 %H:%M:%S',
                                   time.localtime(int(epoch)))
            q_str += '</div>\n'
            q_str += '<div class="quote">'

            tmp_str = tmp_str.replace('[qt][qtmeta aid=' + aid +
                                      ' time=' + epoch + ']', q_str)

            quote_list.append((aid, epoch))
        return tmp_str

    def _render_quote_pre_short(self, src):
        tmp_str = src
        quote_list = []
        regex = r"\[qt\]\[qtmeta aid=(\d*)\]"
        match = re.findall(regex, tmp_str)
        for m in match:
            aid = str(m[0])
            if aid in quote_list:
                continue

            q_str = '<blockquote>\n'
            q_str += '<div class="meta"><img src="'
            q_str += self._get_avatar(aid)
            q_str += '" width="12" height="12" /><b>'
            q_str += self._get_name(aid)
            q_str += '</b></div>\n'
            q_str += '<div class="quote">'

            tmp_str = tmp_str.replace('[qt][qtmeta aid=' + aid + ']', q_str)

            quote_list.append(aid)
        return tmp_str

    def _render_quote_post(self, src):
        return src.replace('[/qt]', '</div>\n</blockquote>')

    def _render_info(self, src):
        tmp_str = src
        tmp_str = self._render_info_pre_title(tmp_str)
        tmp_str = self._render_info_post_title(tmp_str)
        tmp_str = self._render_info_pre_no_title(tmp_str)
        tmp_str = self._render_info_post(tmp_str)
        return tmp_str

    def _render_info_pre_title(self, src):
        return src.replace('[info][title]',
                           '<div class="info">\n<div class="info_head">')

    def _render_info_post_title(self, src):
        return src.replace('[/title]',
                           '</div>\n<div class="info_body">')

    def _render_info_pre_no_title(self, src):
        return src.replace('[info]',
                           '<div class="info">\n<div class="info_body">')

    def _render_info_post(self, src):
        return src.replace('[/info]', '</div>\n</div>')

    def _render_deleted(self, src):
        return src.replace('[deleted]',
                           '<div class="deleted">メッセージは削除されました</div>')

    def _render_sytem_message(self, src):
        tmp_str = src
        dtext_list = []
        regex = r"\[dtext:(\w*)\]"
        match = re.findall(regex, tmp_str)
        for m in match:
            dtext_key = m
            if dtext_key in dtext_list:
                continue
            elif dtext_key not in DTEXT_DICT or not DTEXT_DICT[dtext_key]:
                sys_msg = '<span style="color: red;">[不明なシステムメッセージ: '
                sys_msg += dtext_key
                sys_msg += ']</span>'
            else:
                sys_msg = DTEXT_DICT[dtext_key]
            tmp_str = tmp_str.replace('[dtext:' + dtext_key + ']', sys_msg)

            dtext_list.append(dtext_key)
        return tmp_str

    def _render_thumbnail(self, src):
        tmp_str = src
        pid_list = []
        regex = r"\[preview id=(\d*) ht=(\d*)\]"
        match = re.findall(regex, tmp_str)
        for m in match:
            pid = str(m[0])
            height = str(m[1])
            if pid in pid_list:
                continue
            elif dtext_key not in DTEXT_DICT or not DTEXT_DICT[dtext_key]:
                sys_msg = '<span style="color: red;">[不明なシステムメッセージ: '
                sys_msg += dtext_key
                sys_msg += ']</span>'
            else:
                sys_msg = DTEXT_DICT[dtext_key]
            tmp_str = tmp_str.replace('[dtext:' + dtext_key + ']', sys_msg)

            pid_list.append(dtext_key)
        return tmp_str
