# -*- coding:utf-8 -*-
#
# sfenreader2.appspot.com -> Cloud Run 中継 (リバースプロキシ)
# パスとクエリ文字列をそのまま Cloud Run に投げ、応答をそのまま返す。
#
import os
import urllib.error
import urllib.request
from urllib.parse import quote

UPSTREAM_URL = os.environ.get(
    'UPSTREAM_URL', 'https://sfenreader2-226232565265.asia-northeast1.run.app'
).rstrip('/')
TIMEOUT = 50

# 上流へ渡すリクエストヘッダ
FORWARD_REQUEST_HEADERS = [
    'Accept', 'Accept-Language', 'Accept-Encoding', 'User-Agent',
    'If-None-Match', 'If-Modified-Since', 'Content-Type', 'Referer',
]
# クライアントへ返さないレスポンスヘッダ (hop-by-hop 等)
DROP_RESPONSE_HEADERS = {
    'connection', 'keep-alive', 'transfer-encoding', 'te', 'trailer',
    'upgrade', 'proxy-authenticate', 'proxy-authorization',
    'content-length', 'server', 'date', 'alt-svc',
}

STATUS_TEXT = {200: 'OK', 301: 'Moved Permanently', 302: 'Found',
               304: 'Not Modified', 404: 'Not Found'}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    # 上流のリダイレクトは追いかけずにそのままクライアントへ返す
    def redirect_request(self, *args, **kwargs):
        return None


_opener = urllib.request.build_opener(_NoRedirect)


def app(environ, start_response):
    method = environ.get('REQUEST_METHOD', 'GET')
    # PATH_INFO は WSGI 仕様で latin-1 デコード済みなので元のバイト列に戻す
    path = environ.get('PATH_INFO', '/').encode('latin-1').decode('utf-8', 'replace')
    url = UPSTREAM_URL + quote(path, safe="/%:@!$&'()*+,;=-._~")
    query = environ.get('QUERY_STRING', '')
    if query:
        url += '?' + query

    headers = {}
    for name in FORWARD_REQUEST_HEADERS:
        value = environ.get('HTTP_' + name.upper().replace('-', '_'))
        if name == 'Content-Type':
            value = environ.get('CONTENT_TYPE') or value
        if value:
            headers[name] = value
    host = environ.get('HTTP_HOST', '')
    if host:
        headers['X-Forwarded-Host'] = host
    headers['X-Forwarded-Proto'] = 'https'

    body = None
    if method in ('POST', 'PUT', 'PATCH'):
        length = int(environ.get('CONTENT_LENGTH') or 0)
        body = environ['wsgi.input'].read(length) if length > 0 else b''

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = _opener.open(req, timeout=TIMEOUT)
    except urllib.error.HTTPError as e:
        resp = e  # 4xx/5xx/3xx もそのまま返す
    except Exception as e:  # 上流に繋がらない
        start_response('502 Bad Gateway', [('Content-Type', 'text/plain; charset=utf-8')])
        return [f'Bad Gateway: {e}\n'.encode('utf-8')]

    status = resp.status if hasattr(resp, 'status') else resp.code
    data = resp.read()
    out_headers = []
    for name, value in resp.headers.items():
        if name.lower() in DROP_RESPONSE_HEADERS:
            continue
        if name.lower() == 'location' and value.startswith(UPSTREAM_URL) and host:
            value = 'https://' + host + value[len(UPSTREAM_URL):]
        out_headers.append((name, value))
    out_headers.append(('Content-Length', str(len(data))))
    start_response(f'{status} {STATUS_TEXT.get(status, "")}'.rstrip(), out_headers)
    return [data] if method != 'HEAD' else []
