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

import urllib.parse
import logging
import os
from html import escape
from flask import request, make_response

# class TwiimgHandler(webapp.RequestHandler):
class TwiimgHandler():
    DEFAULT_TITLE = u'局面図'
    EDITING_STRING_EN = u'Edit another dialog from this dialog'
    EDITING_STRING_JA = u'この局面を引き継いで別の局面を作る'
    CARD_WIDTH = 842
    CARD_HEIGHT = 421
    ### カード画像・ページのキャッシュ秒数 (同じ URL なら同じ内容なのでキャッシュさせる)
    CACHE_SECONDS = 86400

    def get(self):
        ### 共有用URLの基点。環境変数 PUBLIC_BASE_URL があればそれを使う
        ### (Cloud Run のURLではなく https://sfenreader2.appspot.com に統一するため)
        ### 無ければクエリ文字列を含まない URL からディレクトリ部分を取り出す
        ### (request.url はクエリ内の %2F もデコードされるため使わない)
        path = os.environ.get('PUBLIC_BASE_URL', '').rstrip('/')
        if path == '':
            path = request.base_url.rsplit('/', 1)[0]

        query_string = request.query_string.decode('latin-1')
        pageurl = f"{path}/twiimg?{query_string}"
        sfenurl = f"{path}/sfen?{query_string}"
        resizeurl = f"{path}/resize?{query_string}"

        sfen = request.args.get('sfen', default='')
        sfen = sfen.replace('\r', '').replace('\n', '')
        black_name = request.args.get('sname', default='')
        white_name = request.args.get('gname', default='')
        title = request.args.get('title', default='')

        ### summary_large_image カードは title が必須なので、無い場合は既定値を使う
        card_title = title if title != '' else self.DEFAULT_TITLE
        if black_name != '' and white_name != '':
            card_description = f'{black_name} vs {white_name}'
        elif black_name != '' or white_name != '':
            card_description = black_name or white_name
        else:
            card_description = sfen
        image_alt = f'{card_title} ({card_description})'

        edit_query = self.create_sfen_query(sfen, black_name, white_name, title)

        ### HTML に埋め込む値はエスケープする
        e = lambda v: escape(v, quote=True)

        output = f'''<!DOCTYPE html>
<html lang="ja">
    <head>
        <meta charset="UTF-8" />
        <title>{e(card_title)}</title>
        <meta property="og:type" content="website" />
        <meta property="og:site_name" content="SFEN Reader" />
        <meta property="og:url" content="{e(pageurl)}" />
        <meta property="og:title" content="{e(card_title)}" />
        <meta property="og:description" content="{e(card_description)}" />
        <meta property="og:image" content="{e(resizeurl)}" />
        <meta property="og:image:type" content="image/png" />
        <meta property="og:image:width" content="{self.CARD_WIDTH}" />
        <meta property="og:image:height" content="{self.CARD_HEIGHT}" />
        <meta property="og:image:alt" content="{e(image_alt)}" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="{e(card_title)}" />
        <meta name="twitter:description" content="{e(card_description)}" />
        <meta name="twitter:image" content="{e(resizeurl)}" />
        <meta name="twitter:image:alt" content="{e(image_alt)}" />
    </head>
    <body>
        <div style="text-align:center;">{e(title)}</div><br>
        <img src="{e(sfenurl)}" alt="{e(image_alt)}" /><br>
        <span style="text-align:left;"><a href="./ja/create_board.html{e(edit_query)}">{self.EDITING_STRING_JA}</a></span><br>
        <span style="text-align:left;"><a href="./en/create_board.html{e(edit_query)}">{self.EDITING_STRING_EN}</a></span><br>
    </body>
</html>
'''
        response = make_response(output)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Cache-Control'] = f'public, max-age={self.CACHE_SECONDS}'
        return response

    def create_sfen_query(self, sfen, black_name, white_name, title):
        params = []
        if sfen != "":
            params.append(('sfen', sfen))
        if black_name != "":
            params.append(('sname', black_name))
        if white_name != "":
            params.append(('gname', white_name))
        if title != "":
            params.append(('title', title))
        if not params:
            return ""
        return "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

def twiimg_handler():
    handle = TwiimgHandler()
    return handle.get()    

def main():
    pass


if __name__ == '__main__':
    main()
