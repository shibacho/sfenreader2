# -*- coding:utf-8 -*-
#
# sfenreader2.appspot.com -> Cloud Run リダイレクタ
# パスとクエリ文字列をそのまま引き継いでリダイレクトする
#
import os

REDIRECT_TO = os.environ.get(
    'REDIRECT_TO', 'https://sfenreader2-226232565265.asia-northeast1.run.app'
).rstrip('/')
STATUS = {'301': '301 Moved Permanently', '302': '302 Found'}.get(
    os.environ.get('REDIRECT_STATUS', '302'), '302 Found')


def app(environ, start_response):
    # PATH_INFO は WSGI 仕様で latin-1 デコード済みなので元のバイト列に戻す
    path = environ.get('PATH_INFO', '/').encode('latin-1').decode('utf-8', 'replace')
    from urllib.parse import quote
    location = REDIRECT_TO + quote(path, safe="/%:@!$&'()*+,;=-._~")
    query = environ.get('QUERY_STRING', '')
    if query:
        location += '?' + query
    start_response(STATUS, [
        ('Location', location),
        ('Content-Type', 'text/plain; charset=utf-8'),
        ('Cache-Control', 'no-store' if STATUS.startswith('302') else 'public, max-age=86400'),
    ])
    return [f'Moved to {location}\n'.encode('utf-8')]
