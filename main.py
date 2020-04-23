# -*- coding:utf-8 -*-
#
# main.py Copyright shibacho 2019
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

# [START sfenreader2]
from flask import Flask, send_from_directory
from flask import Response

from sfen import sfen_handler
from twiimg import twiimg_handler
from resize import resize_handler

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__, static_folder="htdocs", static_url_path="")

app.add_url_rule('/sfen', 'sfen', sfen_handler)
app.add_url_rule('/resize', 'resize', resize_handler)
app.add_url_rule('/twiimg', 'twiimg', twiimg_handler)

@app.route('/')
def index():
    return send_from_directory("htdocs", "index.html")

# @app.route('/sfen')
# def sfen():
#     pass
# #   script: sfen.py

# @app.route('/twiimg')
# def twiimg():
#     pass
# #   script: twiimg.py

# @app.route('/resize')
# def resize():
#     pass
#   script: resize.py

# @app.route('/')
# def hello():
#     """Return a friendly HTTP greeting."""
#     return 'Hello World!'


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    print(f"app.url_map:{app.url_map}")
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
