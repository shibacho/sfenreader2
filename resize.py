#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# sfen.py Copyright 2016 shibacho
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
import io
import sys

from PIL import Image
from flask import request, make_response

# class ResizeHandler(webapp.RequestHandler):
class ResizeHandler():
    WIDTH = 842
    HEIGHT = 421
    logger = ""
    def __init__(self):
        self.logger = logging.getLogger('werkzeug')
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    def get(self):
        ### height:421px width:400px
        ### width will be about 800px
        # self.response.headers['Content-Type'] = 'image/png'
        ### put out resized png image which matches Twitter card.
        ### Basic concept
        ### 1: Prepare white back png which width is 800px, height is 421px.
        ### 2: put diagram image center of the images

        img = Image.new('RGBA', (self.WIDTH, self.HEIGHT), color=0xFFFFFFFF)
        ### Make white background image (800x421 px)
        
        self.logger.warn(f" url_root:{request.url_root} query_string:{request.query_string}")
        url = request.url_root + u'/sfen?' + request.query_string.decode('unicode-escape')

        diagram_img = Image.open(io.BytesIO(urllib.request.urlopen(url).read()))
        x = (self.WIDTH - diagram_img.width) // 2
        img.paste(diagram_img, (x, 0))

        with io.BytesIO() as out:
            img.save(out, format='PNG')
            response = make_response(out.getvalue())
        response.headers['Content-Type'] = 'image/png'
        return response

def resize_handler():
    handler = ResizeHandler()
    return handler.get()

def main():
    pass


if __name__ == '__main__':
    main()
