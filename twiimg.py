#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# sfen.py Copyright 2015-2016 shibacho
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import urllib
import logging
import re
from time import time
from flask import request, make_response

# class TwiimgHandler(webapp.RequestHandler):
class TwiimgHandler():
    DEFAULT_TITLE = u'局面図'
    EDITING_STRING_EN = u'Edit another dialog from this dialog'
    EDITING_STRING_JA = u'この局面を引き継いで別の局面を作る'
    def get(self):
        url = request.url
        m = re.search(r'(.+)\/(.+)', url)
        path = m.group(1)
        
        sfen_raw = request.args.get('sfen', default='')
        sfen = urllib.parse.unquote(sfen_raw)
        sfenurl = f"{path}/sfen?{request.query_string.decode('unicode-escape')}"
        resizeurl = f"{path}/resize?{request.query_string.decode('unicode-escape')}"

        sfen = sfen.replace('\r','')
        sfen = sfen.replace('\n','')

        black_name = urllib.parse.unquote(request.args.get('sname', default=''))
        white_name =  urllib.parse.unquote(request.args.get('gname', default=''))
        title = request.args.get('title')

        height = 421
        # If board has no name, the image height is smaller.
        if black_name == '' and white_name == '' and request.args.get('title') == '':
            height = 400

        query = self.create_sfen_query(sfen_raw, black_name, white_name, title)

        output = f'''<!DOCTYPE html>
<html>
    <head>
        <meta name="twitter:id" content="{str(time())[:-3]}" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:site" content="@sfenreader_gae" />
        <meta name="twitter:description" content="@sfenreader_gae" />
        <meta name="twitter:title" content="{title}" />
'''
        if black_name != '' and white_name != '':
            output += f'<meta name=\"twitter:description" content="{black_name} vs {white_name}" />'
        else:
            output += f'<meta name="twitter:description" content="{title}" />'
        
        output += f'''
        <meta name="twitter:image" content="{resizeurl}" />
        <meta name="twitter:image:width" content="842" />
        <meta name="twitter:image:height" content="421" />
        <meta name="twitter:url" content="{resizeurl}" />
        <meta charset="UTF-8" />
    </head>
    <body>
        <p>
            <div style="text-align:center;">{title}</div><br>
            <img src="{sfenurl}" /><br>
        <span style="text-align:left;"><a href="./ja/create_board.html{query}">{self.EDITING_STRING_JA}</a></span><br>
        <span style="text-align:left;"><a href="./en/create_board.html{query}">{self.EDITING_STRING_EN}</a></span><br>
    </body>
</html>
'''
        return make_response(output)

    def create_sfen_query(self, sfen, black_name, white_name, title):
        query = ""
        if sfen != "":
            query += "sfen=" + sfen + "&"
        if black_name != "":
            query += "sname=" + black_name + "&"
        if white_name != "":
            query += "gname=" + white_name + "&"
        if title != "":
            query += "title=" + title + "&"
        if query[-1] == "&":
            query = "?" + query[:-1]
        return query

def twiimg_handler():
    handle = TwiimgHandler()
    return handle.get()    

def main():
    pass


if __name__ == '__main__':
    main()
