#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# sfen.py Copyright 2011-2016 shibacho
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

from PIL import Image
from flask import request, make_response
import io

import urllib
import logging
import os
import re
import math
import sys

class BadSfenStringException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PieceKindException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# class SfenHandler(webapp.RequestHandler):
class SfenHandler():
    board_img = ''
    board_alphabet_img = ''
    draw_board_img = ''

    piece_img = {}
    piece_alphabet_img = {}
    piece_international_img = {}
    draw_piece_img = {}

    number_img = {}
    black_img = ()
    white_img = ()
    last_move_img = ''
    string_img = {}
    string_img_obj = {}

    exist_title_flag = False
    max_title_height = 0
    title_height = 0

    TITLE_Y = 5

    IMAGE_WIDTH  = 400
    IMAGE_HEIGHT = 400

    PIECE_IMAGE_WIDTH   = 24
    PIECE_IMAGE_HEIGHT  = 24
    NUMBER_IMAGE_WIDTH  = 12
    NUMBER_IMAGE_HEIGHT = 12

    BLACK_MARK_X = 360
    BLACK_MARK_Y = 5

    WHITE_MARK_X = 10
    WHITE_MARK_Y = 310
    WHITE_TITLE_MARK_X = 5

    BLACK_MARK_WIDTH  = 24
    BLACK_MARK_HEIGHT = 24
    BLACK_MARK_SMALL_WIDTH = 16
    BLACK_MARK_SMALL_HEIGHT = 16
    WHITE_MARK_WIDTH  = 24
    WHITE_MARK_HEIGHT = 24
    WHITE_MARK_SMALL_WIDTH = 16
    WHITE_MARK_SMALL_HEIGHT = 16

    BOARD_X = 50
    BOARD_Y = 15
    BOARD_WIDTH  = 306
    BOARD_HEIGHT = 304

    SQUARE_ORIGIN_X = 6
    SQUARE_ORIGIN_Y = 16
    SQUARE_MULTIPLE_X = 31
    SQUARE_MULTIPLE_Y = 32

    ### 持ち駒の数を右揃えにするパディング値
    NUMBER_IMAGE_PADDING_X = 12
    IMAGE_PADDING_X = 4
    IMAGE_PADDING_Y = 4
    TITLE_PADDING_Y = 8

    BLACK = 0
    WHITE = 1

    DEFAULT_FONT_SIZE = 20

    ### 一度に合成出来る画像の最大数
    # COMPOSITE_MAX_NUM = 15
    COMPOSITE_MAX_NUM = 1000
    logger = ""

    def __init__(self):
        # self.logger = logging.getLogger('flask.app')
        self.logger = logging.getLogger('werkzeug')
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


    def img_init(self, piece_kind = 'kanji'):
        if piece_kind == 'kanji':
            self.piece_img_init()
            self.draw_piece_img = self.piece_img
            self.board_img_init()
            self.draw_board_img = self.board_img
        elif piece_kind == 'alphabet':
            self.piece_alphabet_img_init()
            self.draw_piece_img = self.piece_alphabet_img
            self.board_alphabet_img_init()
            self.draw_board_img = self.board_alphabet_img
        elif piece_kind == 'international':
            self.piece_international_img_init()
            self.draw_piece_img = self.piece_international_img
            self.board_alphabet_img_init()
            self.draw_board_img = self.board_alphabet_img
        else:
            raise PieceKindException('No piece kind (' + piece_kind + ')')

        self.mark_img_init()

    def piece_img_init(self):
        ### 画像の初期化が終わっていたらいちいち再読み込みを行わない
        ### Google App Engineでは前の呼び出し時のインスタンスを
        ### 覚えていることがまれによくある
        if self.piece_img != {}:
            return

        self.logger.info('Loading Kanji Piece Image...')

        fu_img = Image.open("img/fu.png")
        ky_img = Image.open("img/ky.png")
        ke_img = Image.open("img/ke.png")
        gi_img = Image.open("img/gi.png")
        ki_img = Image.open("img/ki.png")
        hi_img = Image.open("img/hi.png")
        ka_img = Image.open("img/ka.png")
        ou_img = Image.open("img/ou.png")
        to_img = Image.open("img/to.png")
        ny_img = Image.open("img/ny.png")
        nk_img = Image.open("img/nk.png")
        ng_img = Image.open("img/ng.png")
        ry_img = Image.open("img/ry.png")
        um_img = Image.open("img/um.png")

        self.piece_img['l']  = (ky_img, ky_img.rotate(180))
        self.piece_img['n']  = (ke_img, ke_img.rotate(180))
        self.piece_img['s']  = (gi_img, gi_img.rotate(180))
        self.piece_img['g']  = (ki_img, ki_img.rotate(180))
        self.piece_img['r']  = (hi_img, hi_img.rotate(180))
        self.piece_img['b']  = (ka_img, ka_img.rotate(180))
        self.piece_img['k']  = (ou_img, ou_img.rotate(180))
        self.piece_img['+p'] = (to_img, to_img.rotate(180))
        self.piece_img['+l'] = (ny_img, ny_img.rotate(180))
        self.piece_img['+n'] = (nk_img, nk_img.rotate(180))
        self.piece_img['+s'] = (ng_img, ng_img.rotate(180))
        self.piece_img['+r'] = (ry_img, ry_img.rotate(180))
        self.piece_img['+b'] = (um_img, um_img.rotate(180))
        self.piece_img['+g'] = (ki_img, ki_img.rotate(180))
        self.piece_img['p']  = (fu_img, fu_img.rotate(180))

    def piece_alphabet_img_init(self):
        if self.piece_alphabet_img != {}:
            return

        self.logger.info('Loading Alphabet Piece Image...')

        fu_img = Image.open("img/fu_alphabet.png")
        ky_img = Image.open("img/ky_alphabet.png")
        ke_img = Image.open("img/ke_alphabet.png")
        gi_img = Image.open("img/gi_alphabet.png")
        ki_img = Image.open("img/ki_alphabet.png")
        hi_img = Image.open("img/hi_alphabet.png")
        ka_img = Image.open("img/ka_alphabet.png")
        ou_img = Image.open("img/ou_alphabet.png")
        to_img = Image.open("img/to_alphabet.png")
        ny_img = Image.open("img/ny_alphabet.png")
        nk_img = Image.open("img/nk_alphabet.png")
        ng_img = Image.open("img/ng_alphabet.png")
        ry_img = Image.open("img/ry_alphabet.png")
        um_img = Image.open("img/um_alphabet.png")

        self.piece_alphabet_img['p']  = (fu_img, fu_img.rotate(180))
        self.piece_alphabet_img['l']  = (ky_img, ky_img.rotate(180))
        self.piece_alphabet_img['n']  = (ke_img, ke_img.rotate(180))
        self.piece_alphabet_img['s']  = (gi_img, gi_img.rotate(180))
        self.piece_alphabet_img['g']  = (ki_img, ki_img.rotate(180))
        self.piece_alphabet_img['r']  = (hi_img, hi_img.rotate(180))
        self.piece_alphabet_img['b']  = (ka_img, ka_img.rotate(180))
        self.piece_alphabet_img['k']  = (ou_img, ou_img.rotate(180))
        self.piece_alphabet_img['+p'] = (to_img, to_img.rotate(180))
        self.piece_alphabet_img['+l'] = (ny_img, ny_img.rotate(180))
        self.piece_alphabet_img['+n'] = (nk_img, nk_img.rotate(180))
        self.piece_alphabet_img['+s'] = (ng_img, ng_img.rotate(180))
        self.piece_alphabet_img['+r'] = (ry_img, ry_img.rotate(180))
        self.piece_alphabet_img['+b'] = (um_img, um_img.rotate(180))
        self.piece_alphabet_img['+g'] = (ki_img, ki_img.rotate(180))

    def piece_international_img_init(self):
        if self.piece_international_img != {}:
            return

        self.logger.info('Loading International Piece Image...')

        fu_img = Image.open("img/fu_international.png")
        ky_img = Image.open("img/ky_international.png")
        ke_img = Image.open("img/ke_international.png",)
        gi_img = Image.open("img/gi_international.png")
        ki_img = Image.open("img/ki_international.png")
        hi_img = Image.open("img/hi_international.png")
        ka_img = Image.open("img/ka_international.png")
        ou_img = Image.open("img/ou_international.png")
        to_img = Image.open("img/to_international.png")
        ny_img = Image.open("img/ny_international.png")
        nk_img = Image.open("img/nk_international.png")
        ng_img = Image.open("img/ng_international.png")
        ry_img = Image.open("img/ry_international.png")
        um_img = Image.open("img/um_international.png",)

        self.piece_international_img['p']  = (fu_img, fu_img.rotate(180))
        self.piece_international_img['l']  = (ky_img, ky_img.rotate(180))
        self.piece_international_img['n']  = (ke_img, ke_img.rotate(180))
        self.piece_international_img['s']  = (gi_img, gi_img.rotate(180))
        self.piece_international_img['g']  = (ki_img, ki_img.rotate(180))
        self.piece_international_img['r']  = (hi_img, hi_img.rotate(180))
        self.piece_international_img['b']  = (ka_img, ka_img.rotate(180))
        self.piece_international_img['k']  = (ou_img, ou_img.rotate(180))
        self.piece_international_img['+p'] = (to_img, to_img.rotate(180))
        self.piece_international_img['+l'] = (ny_img, ny_img.rotate(180))
        self.piece_international_img['+n'] = (nk_img, nk_img.rotate(180))
        self.piece_international_img['+s'] = (ng_img, ng_img.rotate(180))
        self.piece_international_img['+r'] = (ry_img, ry_img.rotate(180))
        self.piece_international_img['+b'] = (um_img, um_img.rotate(180))
        self.piece_international_img['+g'] = (ki_img, ki_img.rotate(180))


    def board_img_init(self):
        if self.board_img == '':
            self.logger.info('Loading Board Image...')
            self.board_img = Image.open("img/board.png")

    def board_alphabet_img_init(self):
        if self.board_alphabet_img == '':
            self.logger.info('Loading Alphabet Board Image...')
            self.board_alphabet_img = Image.open("img/board_alphabet.png")

    def mark_img_init(self):
        if self.black_img == ():
            self.logger.info('Loading Black Image...')
            img = Image.open("img/black.png")
            self.black_img = (img, img.rotate(180), img.resize((16, 16)))

        if self.white_img == ():
            self.logger.info('Loading White Image...')
            img = Image.open("img/white.png")
            self.white_img = (img, img.rotate(180), img.resize((16, 16)))

    def number_img_init(self, num):
        self.logger.debug(f'number_img_init:{num}')
        if not num in self.number_img:
            self.logger.info('Loading ' + str(num) + '.png ...')
            num_img = Image.open("img/" + str(num) + ".png")
            self.number_img[num] = (num_img, num_img.rotate(180))

    def last_move_img_init(self):
        if self.last_move_img == '':
            self.logger.info('Loading lm.png ...')
            self.last_move_img = Image.open("img/lm.png")

    def get_string_img(self, string, font_size = 16):
        '''
        Get String Image by Google Charts API.
        Google Charts API can convert Japanese characters to an image.
        This function maybe raise urllib.urlopen()'s exception.
        If string is empty, the return value is (None, None).

        日本語を含む文字列を画像にしてGoogle Charts APIから取ってくる
        urllib.urlopen() が投げる例外を送出する可能性がある
        空の文字列が渡されたら(None, None)が帰ります

        '''
        if string == '' or string is None:
             return (None, None)

        if self.string_img.get(string) == None:
            url = 'http://chart.apis.google.com/chart?chst=d_text_outline'\
                  '&chld=000000|' + str(font_size) + '|l|000000|_|'
            url += urllib.parse.quote(string)

            self.logger.info(string + ' -> URL:' + url)
            img = urllib.request.urlopen(url).read()
            # img_obj = Image(img) ### for width,height
            img_obj = Image.open(io.BytesIO(img))

            self.string_img_obj[string] = img_obj
            self.logger.warn(f" img_obj: format:{img_obj.format} mode:{img_obj.format} width:{img_obj.width} height:{img_obj.height}")
            self.string_img[string] = img_obj.resize((img_obj.width, img_obj.height))

        return (self.string_img[string], self.string_img_obj[string])

    def draw_turn_mark(self, img_list, x, y):
        self.last_move_img_init()
        image = self.last_move_img.resize((self.BLACK_MARK_WIDTH + 10,
                                           self.BLACK_MARK_HEIGHT + 10))

        img_list.append( (image, x - 5, y - 5, 1.0) )
        return self.composite(img_list)

    def sort_hand_array(self, hand_dict):
        '''
        Sort hand dict to
        rook -> bishop -> gold -> silver -> knight -> lance -> pawn.
        飛 -> 角 -> 金 -> 銀 -> 桂 -> 香 -> 歩 の順番にarrayに入れる
        '''
        result = []
        if 'r' in hand_dict:
            result.append( ('r', hand_dict['r']) )

        if 'b' in hand_dict:
            result.append( ('b', hand_dict['b']) )

        if 'g' in hand_dict:
            result.append( ('g', hand_dict['g']) )

        if 's' in hand_dict:
            result.append( ('s', hand_dict['s']) )

        if 'n' in hand_dict:
            result.append( ('n', hand_dict['n']) )

        if 'l' in hand_dict:
            result.append( ('l', hand_dict['l']) )

        if 'p' in hand_dict:
            result.append( ('p', hand_dict['p']) )

        return result

    def sfen_parse(self, sfen):
        board = {}
        white_hand = {}
        black_hand = {}
        move_count = '0'

        sfen_tokens = sfen.split(' ')
        self.logger.info('sfen:' + sfen + ' :token_num:' + str(len(sfen_tokens)))
        if len(sfen_tokens) == 4:
            pieces = sfen_tokens[0]
            turn = sfen_tokens[1]
            inhand = sfen_tokens[2]
            move_count = sfen_tokens[3]
        elif len(sfen_tokens) == 3:
            pieces = sfen_tokens[0]
            turn = sfen_tokens[1]
            inhand = sfen_tokens[2]
        elif len(sfen_tokens) == 2:
            pieces = sfen_tokens[0]
            turn = sfen_tokens[1]
        elif len(sfen_tokens) == 1:
            pieces = sfen_tokens[0]
            turn = '-' ### 省略時はbでもwでもない値
        else:
            raise BadSfenStringException('Token number is too much.')

        rows = pieces.split('/')
        if len(rows) != 9:
            raise BadSfenStringException('Row number is not enough.')

        for i, a_row in enumerate(rows):
            col_num = i + 1
            col_str = str(col_num)
            chars = list(a_row)
            row_counter = 9
            row_str = str(row_counter)

            promote_flag = False
            for a_char in chars:
                if a_char.isdigit():
                    row_counter -= int(a_char)
                    row_str = str(row_counter)
                elif a_char == '+':
                    promote_flag = True
                else:
                    if promote_flag == True:
                        board[row_str + col_str] = '+' + a_char
                        promote_flag = False
                    else:
                        board[row_str + col_str] = a_char
                    row_counter -= 1
                    row_str = str(row_counter)

        if len(sfen_tokens) >= 3 and inhand != '-':
            hands = list(inhand)
            hand_num = 0
            self.logger.warn('hand:{}'.format(hands))
            for a_hand in hands:
                if a_hand.isdigit():
                    if hand_num != 0: ### 2ケタの場合
                        hand_num = hand_num * 10 + int(a_hand)
                    else:
                        hand_num = int(a_hand)
                elif a_hand.isupper():
                    if hand_num == 0:
                        hand_num = 1

                    self.logger.warn('black_hand:[' + str(a_hand) + '] = ' + str(hand_num))
                    a_hand = a_hand.lower() ### For sort after
                    black_hand[a_hand] = hand_num

                    hand_num = 0
                elif a_hand.islower():
                    if hand_num == 0:
                        hand_num = 1
                    self.logger.warn('white_hand:[' + str(a_hand) + '] = ' + str(hand_num))
                    white_hand[a_hand] = hand_num
                    hand_num = 0

        return (board, black_hand, white_hand, turn, move_count)

    def draw_hand_pieces(self, img, hand_tuples, x, y, turn):
        img_list = [(img, 0, 0, 1.0)]
        ### 黒の場合は数字は右寄せにする
        if turn == self.BLACK:
            two_digit_x = x ### 2ケタ目
            one_digit_x = x + self.NUMBER_IMAGE_PADDING_X ### 1ケタ目
        elif turn == self.WHITE:
            two_digit_x = x + self.NUMBER_IMAGE_PADDING_X ### 2ケタ目
            one_digit_x = x ### 1ケタ目

        for hand_tuple in hand_tuples:
            img_list.append((self.draw_piece_img[hand_tuple[0]][turn],
                             x, y, 1.0))

            self.logger.warn('Drawing HandPiece:|{}| num:{} x:{} y:{} turn:{}'.format(hand_tuple[0], hand_tuple[1], x, y, turn))

            ### 持ち駒が複数ある時は数字の描画をする
            if hand_tuple[1] > 1:
                num = hand_tuple[1]

                ### 数字を描画する前
                if turn == self.BLACK:
                    y += (self.PIECE_IMAGE_HEIGHT + self.IMAGE_PADDING_Y)
                else:
                    y -= (self.NUMBER_IMAGE_HEIGHT + self.IMAGE_PADDING_Y)

                ### 10以上の時は2ケタ目を描画
                if num >= 10:
                    hand_str = num // 10
                    if not hand_str in self.number_img:
                        self.number_img_init(hand_str)

                    self.logger.warn('Drawing HandPiece\'s number|{}| x:{} y:{}'.format(hand_str, two_digit_x, y))
                    img_list.append((self.number_img[hand_str][turn],
                                     two_digit_x , y, 1.0))
                    num %= 10 ### 1ケタ目にする

                hand_str = num
                if not hand_str in self.number_img:
                    self.number_img_init(hand_str)

                self.logger.warn('Drawing HandPiece\'s num:{} x:{} y:{}'.format(hand_str, one_digit_x, y))
                img_list.append((self.number_img[hand_str][turn],
                                 one_digit_x, y, 1.0))

                ### 数字を描画し終わった後
                if turn == self.BLACK:
                    y += (self.NUMBER_IMAGE_HEIGHT + self.IMAGE_PADDING_Y)
                else:
                    y -= (self.PIECE_IMAGE_HEIGHT + self.IMAGE_PADDING_Y)
            else:
                if turn == self.BLACK:
                    y += (self.PIECE_IMAGE_HEIGHT + self.IMAGE_PADDING_Y)
                else:
                    y -= (self.PIECE_IMAGE_HEIGHT + self.IMAGE_PADDING_Y)

            if len(img_list) == self.COMPOSITE_MAX_NUM:
                (img, img_list) = self.composite(img_list)

        ### 最後にまとめて描画
        (img, img_list) = self.composite(img_list)
        return (img, img_list)

    def create_arrow_img(self, img_list, arrow_str, board_y):
        '''
        Create arrow image and add img_list.

        img_list: Original img_list
        arrow_str: String given arrow argument (e.g: 77,76 11,12|12,13)
        board_y: board_y
        return value:(Image, Image List)

        This method cannot be run,
        because I don't know image rotating WebAPI for any degree.

        矢印の回転画像を合成し追加する
        現在は矢印画像を任意の向きに回転させるWebAPIが見つからないため動きません
        '''
        return self.composite(img_list)

#        arrow_tokens = arrow_str.split('|')
#        arrow_positions = []
        ### 文字列を解析して 矢印のリストを作る
#        for arrow_token in arrow_tokens:
#            positions = arrow_token.split(',')
#            if len(positions) == 2:
#                begin_pos = positions[0]
#                end_pos = positions[1]
#                arrow_positions.append( (begin_pos, end_pos) )

#        for arrow_pos in arrow_positions:
#            begin_x = 0
#            begin_y = 0
#            end_x = 0
#            end_y = 0

#        return self.composite(img_list)



    ### 一旦描画して描画済みの(img, img_list)のtupleを返す
    def composite(self, img_list):
        if len(img_list) == 1:
            return (img_list[0][0], img_list)
        
        img = Image.new('RGBA', (self.IMAGE_WIDTH, self.IMAGE_HEIGHT + self.max_title_height), color=0xFFFFFFFF)
        for im in img_list:
            self.logger.warn(f" composite: x:{im[1]} y:{im[2]}")
            if im[0].mode == "RGBA":
                img.paste(im[0], (im[1], im[2]), mask=im[0])
            else:
                img.paste(im[0], (im[1], im[2]))

            
        img_list = [(img, 0, 0, 1.0)]
        self.logger.debug("composite success:")
        return (img, img_list)

    def get(self):
        sfen = urllib.parse.unquote(request.args.get('sfen', default=''))
        last_move = urllib.parse.unquote(request.args.get('lm', default=''))
        piece_kind = urllib.parse.unquote(request.args.get('piece', default='kanji'))
        arrow_str = urllib.parse.unquote(request.args.get('arrow', default=''))
        turn_str = urllib.parse.unquote(request.args.get('turn', default='on'))
        move_at = urllib.parse.unquote(request.args.get('ma', default='off'))
        self.logger.info('sfen:' + sfen + ' last_move:' + last_move)
        self.logger.debug(f' sfen:{sfen} lm:{last_move} piece_kind:{piece_kind} arrow_str:{arrow_str} turn_str:{turn_str} move_at:{move_at}')
        if sfen == '':
            return make_response("Please, specify SFEN string.")

        ### If Move At(ma) is on, draw nth move count.
        if piece_kind == 'kanji':
            move_count_prefix = ''
            move_count_suffix = u' 手目'
        else:
            move_count_prefix = 'at '
            move_count_suffix = ''

        ### Remove CR LF
        sfen = sfen.replace('\r','')
        sfen = sfen.replace('\n','')

        black_name = urllib.parse.unquote(request.args.get('sname', default=''))
        white_name = urllib.parse.unquote(request.args.get('gname', default=''))
        title = urllib.parse.unquote(request.args.get('title', default=''))

        font_size_str = urllib.parse.unquote(request.args.get('fontsize', default=''))
        if font_size_str.isdigit():
            font_size = int(font_size_str)
        else:
            font_size = self.DEFAULT_FONT_SIZE

        try:
            self.img_init(piece_kind = piece_kind)
            img_list = []
            (board, black_hand, white_hand, turn_sfen, move_count) = self.sfen_parse(sfen)
            (black_name_img, black_name_img_obj) = self.get_string_img(black_name, font_size)
            (white_name_img, white_name_img_obj) = self.get_string_img(white_name, font_size)
            (title_img, title_img_obj) = self.get_string_img(title, font_size)

            if move_at == 'on' and move_count != '0':
                move_count_str = move_count_prefix + move_count + move_count_suffix
                (move_count_img, move_count_img_obj) = self.get_string_img(move_count_str, font_size)
        except BadSfenStringException as e:
            self.logger.error('Invalid sfen string:' + str(e))
            return make_response('Invalid sfen string:' + str(e))
        except PieceKindException as e:
            self.logger.error('Invalid piece kind:' + str(e))
            return make_response('Invalid piece kind:' + str(e))
        except IOError as e:
            self.logger.error('Cannot create string image:' + str(e))
            return make_response('Cannot create string image:' + str(e))

        if black_name != '' or white_name != '' or title != '' or move_count != '0':
            self.exist_title_flag = True
            if black_name is not None:
                self.logger.info('black_name:' + black_name)

            if white_name is not None:
                self.logger.info(u'white_name:' + white_name)

            if title is not None:
                self.logger.info('title:' + title)

            if move_count != '0':
                self.logger.info('move_count:' + move_count)
        else:
            self.logger.info('No titles found.')
            self.exist_title_flag = False
            self.max_title_height = 0
            self.title_height = 0

        ### タイトル等が存在したら最大の高さを求めて必要に応じて描画する
        if self.exist_title_flag == True:
            self.max_title_height = self.BLACK_MARK_SMALL_HEIGHT
            if black_name_img_obj is not None and black_name_img_obj.height > self.max_title_height:
                self.max_title_height = black_name_img_obj.height

            if white_name_img_obj is not None and white_name_img_obj.height > self.max_title_height:
                self.max_title_height = white_name_img_obj.height

            if title_img_obj is not None and title_img_obj.height > self.max_title_height:
                self.max_title_height = title_img_obj.height

            self.logger.info('max_title_height:' + str(self.max_title_height))

            self.title_height = self.TITLE_Y + (self.max_title_height * 2) + self.IMAGE_PADDING_Y

            ### 先手のマークを書く位置を画像の右端から求める
            if black_name_img is not None:
                self.logger.info('Drawing Black Name:' + black_name +
                             ' width:' + str(black_name_img_obj.width) +
                             ' height:' + str(black_name_img_obj.height))

                black_title_x_left = self.IMAGE_WIDTH - (black_name_img_obj.width +
                                                         self.BLACK_MARK_SMALL_WIDTH +
                                                         self.IMAGE_PADDING_X)

                black_title_x = black_title_x_left
                img_list.append( (self.black_img[2], black_title_x,
                                  self.TITLE_Y, 1.0) )

                black_title_x += self.BLACK_MARK_SMALL_WIDTH + self.IMAGE_PADDING_X
                img_list.append( (black_name_img, black_title_x,
                                  self.TITLE_Y, 1.0) )

            ### 後手のマークと名前を描画する
            if white_name_img is not None:
                self.logger.info('Drawing White Name:' + white_name +
                             ' width:' + str(white_name_img_obj.width) +
                             ' height:' + str(white_name_img_obj.height) )
                white_title_x = self.WHITE_TITLE_MARK_X
                img_list.append( (self.white_img[2], white_title_x,
                                  self.TITLE_Y, 1.0) )

                white_title_x += self.WHITE_MARK_SMALL_WIDTH + self.IMAGE_PADDING_X
                img_list.append( (white_name_img, white_title_x,
                                  self.TITLE_Y, 1.0) )
                white_title_x_right = (white_title_x +
                                       white_name_img_obj.width +
                                       self.IMAGE_PADDING_X)


            ### 中央タイトルの描画
            if title_img is not None:
                center = self.IMAGE_WIDTH // 2

                ### 文字の長さに合わせて描画開始位置を調整
                center_x = center - title_img_obj.width // 2
                img_list.append( (title_img, center_x,
                                  self.TITLE_Y + self.max_title_height + self.IMAGE_PADDING_Y,
                                  1.0) )

            if move_at == 'on' and move_count != '0':
                center = self.IMAGE_WIDTH // 2
                center_x = center - move_count_img_obj.width // 2
                img_list.append( (move_count_img, center_x, self.TITLE_Y, 1.0) )


        self.logger.info('max_title_height:' + str(self.max_title_height))
        if len(img_list) != 0:
            (img, img_list) = self.composite(img_list)

        ### 飛 -> 角 -> 金 -> 銀 -> 桂 -> 香 -> 歩 の順番にarrayに入れる
        white_hand_array = self.sort_hand_array(white_hand)
        black_hand_array = self.sort_hand_array(black_hand)

        ### 最終着手マスの描画
        ### 最終着手マスは &lm=76 (７六のマスを強調表示)のような形式で渡される
        ### TODO: チェス方式(76 -> 7f) も対応したい
        if last_move != '':
            m = re.compile('^([1-9])([1-9])$').match(last_move)
            if m is not None:
                self.logger.info('Valid last_move:')
                self.last_move_img_init()
                col = int(m.group(1))
                row = int(m.group(2))
                lm_x = (self.SQUARE_ORIGIN_X - 1 + self.BOARD_X +
                        self.SQUARE_MULTIPLE_X * (9 - int(col)) )
                lm_y = (self.SQUARE_ORIGIN_Y - 1 + self.BOARD_Y +
                        self.title_height +
                        self.SQUARE_MULTIPLE_Y * (int(row) - 1) )
                img_list.append((self.last_move_img, lm_x, lm_y, 0.5))

        ### 盤の描画
        ### 最終着手マスより後に書くのは盤上の星が上に来て欲しいため
        img_list.append( (self.draw_board_img, self.BOARD_X,
                          self.BOARD_Y + self.title_height,
                          1.0) )

        ### 盤上の駒の描画
        for pos, piece in board.items():
            turn = self.BLACK
            piece_kind = piece.replace('+','')
            if piece_kind.isupper():
                turn = self.BLACK
            elif piece_kind.islower():
                turn = self.WHITE

            [col, row] = list(pos)
            piece_lower = piece.lower()

            ### 駒を書く場所を決める
            x = self.BOARD_X + self.SQUARE_ORIGIN_X + self.SQUARE_MULTIPLE_X * (9 - int(col))
            y = self.BOARD_Y + self.SQUARE_ORIGIN_Y + self.title_height + self.SQUARE_MULTIPLE_Y * (int(row) - 1)
            self.logger.warn("x:" + str(x) + " y:" + str(y) +
                         " pos:" + pos + " piece:" + piece_lower +
                         " turn:" + str(turn))
            img_list.append((self.draw_piece_img[piece_lower][turn],
                             x, y, 1.0))

            if len(img_list) == self.COMPOSITE_MAX_NUM:
                (img, img_list) = self.composite(img_list)

        (img, img_list) = self.composite(img_list)
        self.logger.info('Success to draw pieces.')

        ### 手番を書く
        if turn_str == 'on':
            self.logger.info('draw_turn:' + turn_sfen +
                         ' title_height:' + str(self.title_height))
            if turn_sfen == 'b':
                (img, img_list) = self.draw_turn_mark(img_list, self.BLACK_MARK_X,
                                                      self.BLACK_MARK_Y +
                                                      self.title_height)
            elif turn_sfen == 'w':
                (img, img_list) = self.draw_turn_mark(img_list, self.WHITE_MARK_X,
                                                      self.WHITE_MARK_Y +
                                                      self.title_height)

        ### 先手のマークを表示する
        img_list.append( (self.black_img[0], self.BLACK_MARK_X,
                          self.BLACK_MARK_Y + self.title_height,
                          1.0) )

        ### 後手のマークを表示する
        img_list.append( (self.white_img[1], self.WHITE_MARK_X,
                          self.WHITE_MARK_Y + self.title_height,
                          1.0) )
        (img, img_list) = self.composite(img_list)
        self.logger.info('Success to draw black/white marks.')

        ### 後手の手持ちの駒を描画
        pos_x = self.WHITE_MARK_X
        pos_y = self.WHITE_MARK_Y + self.title_height - (self.PIECE_IMAGE_HEIGHT + self.IMAGE_PADDING_Y)

        (img, img_list) = self.draw_hand_pieces(img, white_hand_array,
                                                pos_x, pos_y, self.WHITE)

        ### 先手の手持ちの駒を描画
        pos_x = self.BLACK_MARK_X
        pos_y = self.BLACK_MARK_Y + self.title_height + (self.BLACK_MARK_HEIGHT + self.IMAGE_PADDING_Y)
        (img, img_list) = self.draw_hand_pieces(img, black_hand_array,
                                                pos_x, pos_y, self.BLACK)

        ### 矢印を書く(予定)
#        if arrow_str != '':
#            (img, img_list) = self.create_arrow_img(img_list, arrow_str)
#            (img, img_list) = self.composite(img_list)

        with io.BytesIO() as out:
            img.save(out, format="PNG")
            response = make_response(out.getvalue())
        response.headers['Content-Type'] = 'image/png'
        return response

def sfen_handler():
    handle = SfenHandler()
    return handle.get()

def main():
    pass


if __name__ == '__main__':
    main()
