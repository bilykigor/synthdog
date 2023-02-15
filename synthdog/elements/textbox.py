"""
Donut
Copyright (c) 2022-present NAVER Corp.
MIT License
"""
import random
import numpy as np
from synthtiger import layers
from babel.numbers import format_decimal
from random_address import real_random_address
import unidecode
import time

locales = {'ar': 'ar_SY', 'bg': 'bg_BG', 'bs': 'bs_BA', 'ca': 'ca_ES', 'cs': 'cs_CZ', 'da': 'da_DK', 'de': 'de_DE', 'el': 'el_GR', 'en': 'en_US', 'es': 'es_ES', 'et': 'et_EE', 'fa': 'fa_IR', 'fi': 'fi_FI', 'fr': 'fr_FR', 'gl': 'gl_ES', 'he': 'he_IL', 'hu': 'hu_HU', 'id': 'id_ID', 'is': 'is_IS', 'it': 'it_IT', 'ja': 'ja_JP', 'km': 'km_KH', 'ko': 'ko_KR', 'lt': 'lt_LT', 'lv': 'lv_LV', 'mk': 'mk_MK', 'nl': 'nl_NL', 'nn': 'nn_NO', 'no': 'nb_NO', 'pl': 'pl_PL', 'pt': 'pt_PT', 'ro': 'ro_RO', 'ru': 'ru_RU', 'sk': 'sk_SK', 'sl': 'sl_SI', 'sv': 'sv_SE', 'th': 'th_TH', 'tr': 'tr_TR', 'uk': 'uk_UA'}

class TextBox:
    def __init__(self, config):
        self.fill = config.get("fill", [1, 1])
        self.upper_case = config.get("upper_case", False)

    def generate(self, size, text, font):
        width, height = size

        char_layers, chars = [], []
        fill = np.random.uniform(self.fill[0], self.fill[1])
        height *= fill
        width = np.clip(width * fill, height, width)
        font = {**font, "size": int(height)}
        left, top = 0, 0

        char_scale = 1#height / char_layer.height
        
        if isinstance(text,str):
            line_width = 0
            for char in text:
                if self.upper_case:
                    char = char.upper()
                line_width += layers.TextLayer(char, **font).size[0] 
                
            char_scale = min(width/line_width,1)
            
        #--------------------------------------------- 
        for char in text:
            if char in "\r\n":
                continue
            
            if self.upper_case:
                char = char.upper()

            char_layer = layers.TextLayer(char, **font)
            char_layer.bbox = [left, top, *(char_layer.size * char_scale)]
            if char_layer.right > width:
                break

            char_layers.append(char_layer)
            chars.append(char)
            left = char_layer.right

        text = "".join(chars).strip()
        if len(char_layers) == 0 or len(text) == 0:
            return None, None

        text_layer = layers.Group(char_layers).merge()

        return text_layer, text
    
    
class CodeTextBox:
    def __init__(self, config):
        self.fill = config.get("fill", [1, 1])
        self.upper_case = config.get("upper_case", False)

    def generate(self, size, font):
        width, height = size

        char_layers, chars, not_chars = [], [], []
        fill = np.random.uniform(self.fill[0], self.fill[1])
        height *= fill
        width = np.clip(width * fill, height, width)
        font = {**font, "size": int(height)}
        char_scale = 1# height / char_layer.height
        left, top = 0, 0

        while True:
            char = np.random.choice(['1','2','3','4','5','6','7','8','9','0','/','-'],1)[0]
            if not chars:
                if char in ['0','-','/']:
                    char = '1'
            
            if char in ['-','/']:
                if len(not_chars)>=2:
                    char = np.random.choice(['1','2','3','4','5','6','7','8','9','0'],1)[0]
                else:
                    not_chars.append(char)
                    
            if self.upper_case:
                char = char.upper()

            char_layer = layers.TextLayer(char, **font)
            char_layer.bbox = [left, top, *(char_layer.size * char_scale)]
            if char_layer.right > width:
                break

            char_layers.append(char_layer)
            chars.append(char)
            left = char_layer.right

        text = "".join(chars).strip()
        if len(char_layers) == 0 or len(text) == 0:
            return None, None

        text_layer = layers.Group(char_layers).merge()

        return text_layer, text
    
    
class NumberTextBox:
    def __init__(self, config):
        self.fill = config.get("fill", [1, 1])
        self.upper_case = config.get("upper_case", False)

    def generate(self, size, font):
        width, height = size

        char_layers, chars = [], []
        fill = np.random.uniform(self.fill[0], self.fill[1])
        height *= fill
        width = np.clip(width * fill, height, width)
        font = {**font, "size": int(height)}
        char_scale = 1# height / char_layer.height
        left, top = 0, 0

        while True:
            char = str(np.random.choice([1,2,3,4,5,6,7,8,9,0],1)[0])
            if not chars:
                if char=='0':
                    char = '1'
                    
            if self.upper_case:
                char = char.upper()

            char_layer = layers.TextLayer(char, **font)
            char_layer.bbox = [left, top, *(char_layer.size * char_scale)]
            if char_layer.right > width:
                break

            char_layers.append(char_layer)
            chars.append(char)
            left = char_layer.right

        text = "".join(chars).strip()
        if len(char_layers) == 0 or len(text) == 0:
            return None, None

        text_layer = layers.Group(char_layers).merge()

        return text_layer, text


class AmountTextBox:
    def __init__(self, config):
        self.fill = config.get("fill", [1, 1])
        self.stars_before = True
        self.stars_after = True
        self.currency_symbol = False
        self.max_amount = 1000000

    def generate(self, size, font):
        width, height = size
        
        char_layers, chars = [], []
        fill = np.random.uniform(self.fill[0], self.fill[1])
        height *= fill
        width = np.clip(width * fill, height, width)
        font = {**font, "size": int(height)}
        left, top = 0, 0
        
        #---------------------------------------------
        char_layer = layers.TextLayer('5', **font)
        char_scale = 1#height / char_layer.height
        five_width = char_layer.size[0] * char_scale
        
        char_layer = layers.TextLayer('.', **font)
        decimal_separator_width = char_layer.size[0] * char_scale

        char_layer = layers.TextLayer(' ', **font)
        fraction_separator_width = char_layer.size[0] * char_scale

        char_layer = layers.TextLayer('*', **font)
        star_width = char_layer.size[0] * char_scale
        
        all_width = max([star_width,five_width,fraction_separator_width])
        #---------------------------------------------
        max_n_symbols = int((width-decimal_separator_width)/all_width)
        max_n_symbols = int(max_n_symbols/4*3)  
        #---------------------------------------------
        amount = random.randrange(1, min(10**max_n_symbols-1,self.max_amount))
        amount = round(amount/100,2)
        
        output_amount = amount
        amount = format_decimal(amount, locale=random.choice(list(locales.values())))
        amount = str(amount)
        amount = unidecode.unidecode(amount)
        #---------------------------------------------
        amount_width = 0
        for char in amount:
            char_layer = layers.TextLayer(char, **font)
            char_scale = 1# height / char_layer.height
            char_width = char_layer.size[0] * char_scale
            amount_width += char_width
        #---------------------------------------------
        if self.stars_before or self.stars_after:
            n_stars = int(max(0, width-amount_width)/star_width)
            if n_stars>0:
                if self.stars_before and self.stars_after:
                    n_stars_before = random.randrange(1, n_stars)
                    n_stars_after = n_stars-n_stars_before
                elif self.stars_before:
                    n_stars_before = n_stars
                    n_stars_after = 0
                elif self.stars_after:
                    n_stars_before = 0
                    n_stars_after = n_stars
                
                amount = '*'*n_stars_before + amount + '*'*n_stars_after
        #---------------------------------------------    
        for char in amount:
            char_layer = layers.TextLayer(char, **font)
            char_scale = 1# height / char_layer.height
            char_layer.bbox = [left, top, *(char_layer.size * char_scale)]

            char_layers.append(char_layer)
            chars.append(char)
            left = char_layer.right

        text_layer = layers.Group(char_layers).merge()

        return text_layer, output_amount


class AddressTextBox:
    def __init__(self, config):
        self.fill = config.get("fill", [1, 1])
        self.upper_case = config.get("upper_case", False)

    def generate(self, size, font):
        width, height = size
        
        char_layers, chars = [], []
        fill = np.random.uniform(self.fill[0], self.fill[1])
        height *= fill
        width = np.clip(width * fill, height, width)
        font = {**font, "size": int(height)}
        left, top = 0, 0
        #---------------------------------------------
        address = real_random_address()
        address_line1 = f"{address['address1']}"
        address_line2 = f"{address.get('city','New York')}, {address['state']} {address['postalCode']} "
        address_line = np.random.choice([address_line1,address_line2],1)[0]
        #---------------------------------------------
        address_line_width = 0
        for char in address_line:
            if self.upper_case:
                char = char.upper()
            address_line_width += layers.TextLayer(char, **font).size[0] 
            
        char_scale = min(width/address_line_width,1)
        
        for char in address_line:
            char = char.upper()
            char_layer = layers.TextLayer(char, **font)
            char_layer.bbox = [left, top, *(char_layer.size * char_scale)]

            char_layers.append(char_layer)
            chars.append(char)
            left = char_layer.right

        text = "".join(chars).strip()
        if len(char_layers) == 0 or len(text) == 0:
            return None, None

        text_layer = layers.Group(char_layers).merge()

        return text_layer, text


def generate_timestamp(start, end):
    return start + random.random() * (end - start)


months = [
    '',
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',
]


class DateTextBox:
    def __init__(self, config):
        self.fill = config.get("fill", [1, 1])
        self.format = "dmY"    # should be added to config
        self.abbreviation = False   # should be added to config
        self.separator = "/"
        self.start_date = 1577829600.0
        self.upper_case = False
        
    def format_date(self, timestamp):
        time_dict = time.localtime(timestamp)
        year = time_dict.tm_year
        month = time_dict.tm_mon
        day = time_dict.tm_mday

        if self.abbreviation:
            month = months[month]

        if self.format == "dmY":
            return f"{day}{self.separator}{month}{self.separator}{year}"
        if self.format == "mdY":
            return f"{month}{self.separator}{day}{self.separator}{year}"
        if self.format == "Ydm":
            return f"{year}{self.separator}{day}{self.separator}{month}"

        return f"{year}{self.separator}{month}{self.separator}{day}"

    def generate(self, size, font):
        width, height = size

        char_layers, chars = [], []
        fill = np.random.uniform(self.fill[0], self.fill[1])
        height *= fill
        width = np.clip(width * fill, height, width)
        font = {**font, "size": int(height)}
        left, top = 0, 0
        date_str = self.format_date(generate_timestamp(self.start_date, time.time()))
        
        date_str_line_width = 0
        for char in date_str:
            if self.upper_case:
                char = char.upper()
            date_str_line_width += layers.TextLayer(char, **font).size[0] 
        
        date_str_line_height = 0
        for char in date_str:
            if self.upper_case:
                char = char.upper()
            date_str_line_height = max(date_str_line_height,layers.TextLayer(char, **font).size[1])
            
        char_scale = min(width/date_str_line_width,1)
        
        for char in date_str:
            if char in "\r\n":
                continue

            char_layer = layers.TextLayer(char, **font)
            char_layer.bbox = [left, top, *(char_layer.size * char_scale)]

            char_layers.append(char_layer)
            chars.append(char)
            left = char_layer.right

        text = "".join(chars).strip()
        if len(char_layers) == 0 or len(text) == 0:
            return None, None

        text_layer = layers.Group(char_layers).merge()

        return text_layer, text
    
