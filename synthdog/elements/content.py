"""
Donut
Copyright (c) 2022-present NAVER Corp.
MIT License
"""
from collections import OrderedDict
import numpy as np
from synthtiger import components

from elements.textbox import TextBox, AddressTextBox, AmountTextBox, DateTextBox, NumberTextBox, CodeTextBox, MICRTextBox
from layouts import GridStack,SampleStack
import inflect

class TextReader:
    def __init__(self, path, cache_size=2 ** 28, block_size=2 ** 20):
        self.fp = open(path, "r", encoding="utf-8")
        self.length = 0
        self.offsets = [0]
        self.cache = OrderedDict()
        self.cache_size = cache_size
        self.block_size = block_size
        self.bucket_size = cache_size // block_size
        self.idx = 0

        while True:
            text = self.fp.read(self.block_size)
            if not text:
                break
            self.length += len(text)
            self.offsets.append(self.fp.tell())

    def __len__(self):
        return self.length

    def __iter__(self):
        return self

    def __next__(self):
        char = self.get()
        self.next()
        return char

    def move(self, idx):
        self.idx = idx

    def next(self):
        self.idx = (self.idx + 1) % self.length

    def prev(self):
        self.idx = (self.idx - 1) % self.length

    def get(self):
        key = self.idx // self.block_size

        if key in self.cache:
            text = self.cache[key]
        else:
            if len(self.cache) >= self.bucket_size:
                self.cache.popitem(last=False)

            offset = self.offsets[key]
            self.fp.seek(offset, 0)
            text = self.fp.read(self.block_size)
            self.cache[key] = text

        self.cache.move_to_end(key)
        char = text[self.idx % self.block_size]
        return char


class Content:
    def __init__(self, config):
        self.config = config
        self.margin = config.get("margin", [0, 0.1])
        self.reader = TextReader(**config.get("text", {}))
        self.font = components.BaseFont(**config.get("font", {}))
        self.align = config['layout']['align']
        self.micr_font = components.BaseFont(paths=['resources/font/sup'], weights=[1]).sample()

        self.textbox_color = components.Switch(components.Gray(), **config.get("textbox_color", {}))
        self.content_color = components.Switch(components.Gray(), **config.get("content_color", {}))

    def generate(self, meta):
        # width, height = (meta["w"],meta['h'])

        # layout_left = width * np.random.uniform(self.margin[0], self.margin[1])
        # layout_top = height * np.random.uniform(self.margin[0], self.margin[1])
        # layout_width = max(width - layout_left * 2, 0)
        # layout_height = max(height - layout_top * 2, 0)
        # layout_bbox = [layout_left, layout_top, layout_width, layout_height]

        text_layers, texts = [], []
        
        layout = SampleStack(meta['path'],self.align)
        
        layouts = layout.generate()
        
        self.reader.move(np.random.randint(len(self.reader)))

        amount = None
        for layout in layouts:
            base_font = self.font.sample()
            
            for bbox, align, title, upper_case, bold in layout:
                if title not in ['Amount']:
                    continue
                
                font = base_font.copy()
                font['bold'] = bold
                
                x, y, w, h = bbox
                
                upper_case = upper_case>0.5
                
                tb_config = self.config.get("textbox", {})
                tb_config['upper_case'] = upper_case
                
                amounttextbox = AmountTextBox(tb_config)
                text_layer, amount = amounttextbox.generate((w, h), font)
                
                if text_layer is None:
                    continue

                text_layer.center = (x + w / 2, y + h / 2)
                if align == "left":
                    text_layer.left = x
                if align == "right":
                    text_layer.right = x + w

                self.textbox_color.apply([text_layer])
                text_layers.append(text_layer)
                
        cheque_number = None
        for layout in layouts:
            base_font = self.font.sample()
            
            for bbox, align, title, upper_case, bold in layout:
                if title not in ['Cheque number']:
                    continue
                
                font = base_font.copy()
                font['bold'] = bold
                
                x, y, w, h = bbox
                
                upper_case = upper_case>0.5
                
                tb_config = self.config.get("textbox", {})
                tb_config['upper_case'] = upper_case
                
                numbertextbox = NumberTextBox(tb_config)
                text_layer, cheque_number = numbertextbox.generate((w, h), font)
                
                if text_layer is None:
                    continue

                text_layer.center = (x + w / 2, y + h / 2)
                if align == "left":
                    text_layer.left = x
                if align == "right":
                    text_layer.right = x + w

                self.textbox_color.apply([text_layer])
                text_layers.append(text_layer)
        
        for layout in layouts:
            base_font = self.font.sample()
            
            for bbox, align, title, upper_case, bold in layout:
                font = base_font.copy()
                font['bold'] = bold
                
                x, y, w, h = bbox
                
                upper_case = upper_case>0.5
                
                tb_config = self.config.get("textbox", {})
                tb_config['upper_case'] = upper_case
                
                if title in ['Remove','Amount','Cheque number']:
                    continue
                elif title in ['Address']:
                    addresstextbox = AddressTextBox(tb_config)
                    text_layer, text = addresstextbox.generate((w, h), font)
                elif title in ['Code']:
                    codetextbox = CodeTextBox(tb_config)
                    text_layer, text = codetextbox.generate((w, h), font)
                elif title in ['Date']:
                    datetextbox = DateTextBox(tb_config)
                    text_layer, date_text = datetextbox.generate((w, h), font)
                elif title in ['Amount text']:
                    p = inflect.engine()
                    text =p.number_to_words(amount).replace(',','')
                    textbox = TextBox(tb_config)
                    text_layer, text = textbox.generate((w, h), text, font)
                elif title in ['MICR']:
                    micrbox = MICRTextBox(tb_config)
                    text_layer, text = micrbox.generate((w, h), self.micr_font, cheque_number)
                else:
                    textbox = TextBox(tb_config)
                    text_layer, text = textbox.generate((w, h), self.reader, font)
                    self.reader.prev()

                if text_layer is None:
                    continue

                text_layer.center = (x + w / 2, y + h / 2)
                if align == "left":
                    text_layer.left = x
                if align == "right":
                    text_layer.right = x + w

                self.textbox_color.apply([text_layer])
                text_layers.append(text_layer)
                #texts.append(text)

        self.content_color.apply(text_layers)

        return text_layers, {'amount':amount,'date':date_text}
