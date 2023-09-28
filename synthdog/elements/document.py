"""
Donut
Copyright (c) 2022-present NAVER Corp.
MIT License
"""
import numpy as np
from synthtiger import components

from synthdog.elements.content import CheckContent,RemittanceContent
from synthdog.elements.paper import Paper, CheckPaper,RemittancePaper
from synthtiger import layers
import cv2
import random


class Document:
    def __init__(self, config):
        self.fullscreen = config.get("fullscreen", 0.5)
        self.landscape = config.get("landscape", 0.5)
        self.short_size = config.get("short_size", [480, 1024])
        self.aspect_ratio = config.get("aspect_ratio", [1, 2])
        self.paper = Paper(config.get("paper", {}))
        self.content = Content(config.get("content", {}))
        self.effect = components.Iterator(
            [
                components.Switch(components.ElasticDistortion()),
                components.Switch(components.AdditiveGaussianNoise()),
                components.Switch(
                    components.Selector(
                        [
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                        ]
                    )
                ),
            ],
            **config.get("effect", {}),
        )

    def generate(self, size=None):
        paper_layer, paper_meta = self.paper.generate(size)
        
        text_layers, texts = self.content.generate(paper_meta)
        
        self.effect.apply([*text_layers, paper_layer])

        return paper_layer, text_layers, texts
    
    
class CheckDocument:
    def __init__(self, parent_path, config):
        self.fullscreen = config.get("fullscreen", 0.5)
        self.landscape = config.get("landscape", 0.5)
        self.short_size = config.get("short_size", [480, 1024])
        self.aspect_ratio = config.get("aspect_ratio", [1, 2])
        self.paper = CheckPaper(config.get("paper", {}))
        self.content = CheckContent(parent_path, config.get("content", {}))
        self.effect = components.Iterator(
            [
                components.Switch(components.ElasticDistortion()),
                components.Switch(components.AdditiveGaussianNoise()),
                components.Switch(
                    components.Selector(
                        [
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                        ]
                    )
                ),
            ],
            **config.get("effect", {}),
        )

    def generate(self, size):
        paper_layer, paper_meta = self.paper.generate(None)
        text_layers, texts = self.content.generate(paper_meta)
        document_group = layers.Group([*text_layers, paper_layer]).merge()
        
        if size is not None:
            max_width,max_height = size
            width, height = document_group.size
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            document_group = layers.Layer(cv2.resize(document_group.image,(new_width,new_height)))
    
        #self.effect.apply([document_group])

        return document_group, texts


def resize_box_coordinates(box, original_size, new_size):
    """
    Resize box coordinates based on the resizing factor between the original size and the new size.
    Args:
        box (tuple): Tuple of box coordinates (x_min, y_min, x_max, y_max).
        original_size (tuple): Tuple of the original image size (width, height).
        new_size (tuple): Tuple of the new image size (width, height).
    Returns:
        tuple: Tuple of the resized box coordinates (x_min_resized, y_min_resized, x_max_resized, y_max_resized).
    """
    x_min, y_min, x_max, y_max = box
    original_width, original_height = original_size
    new_width, new_height = new_size

    x_scale = new_width / original_width
    y_scale = new_height / original_height

    x_min_resized = int(x_min * x_scale)
    y_min_resized = int(y_min * y_scale)
    x_max_resized = int(x_max * x_scale)
    y_max_resized = int(y_max * y_scale)

    return [x_min_resized, y_min_resized, x_max_resized, y_max_resized]


class RemittanceDocument:
    def __init__(self, parent_path, config):
        self.fullscreen = config.get("fullscreen", 0.5)
        self.landscape = config.get("landscape", 0.5)
        self.short_size = config.get("short_size", [480, 1024])
        self.aspect_ratio = config.get("aspect_ratio", [1, 2])
        self.paper = RemittancePaper(config.get("paper", {}))
        self.content = RemittanceContent(parent_path, config.get("content", {}))
        self.effect = components.Iterator(
            [
                components.Switch(components.ElasticDistortion()),
                components.Switch(components.AdditiveGaussianNoise()),
                components.Switch(
                    components.Selector(
                        [
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                            components.Perspective(),
                        ]
                    )
                ),
            ],
            **config.get("effect", {}),
        )

    def generate(self, size):
        paper_layer, paper_meta = self.paper.generate(None)
        text_layers, texts = self.content.generate(paper_meta)
        document_group = layers.Group([*text_layers, paper_layer]).merge()


        # get blocks and sort by area

        blocks = [item['box'] for item in texts if item['label'] == 'block']
        if blocks != []:
            blocks.sort(key=lambda item: (item[2] - item[0]) * (item[3] - item[1]), reverse=True)

            # textboxes to blocks
            new_texts = []

            block_to_textboxes = {encode_block(block): [] for block in blocks}

            for textbox in texts:
                if textbox['label'] == 'block':
                    continue

                box = textbox['box']
                for block in blocks:
                    if check_box(box, block):
                        block_to_textboxes[encode_block(block)].append({'box': [box[0] - block[0], box[1] - block[1], box[2] - block[0], box[3] - block[1]], 'text': textbox['text'], 'label': textbox['label']})
                        break


            w = paper_meta['w']
            h = paper_meta['h']
            already_placed = []
            origin = []

            prev_image = document_group.image

            blank_image = prev_image.copy()
            blank_image[:,:] = 255

            random_placed = True

            for block in blocks:
                place_x = int(random.random() * (w - (block[2] - block[0])))
                place_y = int(random.random() * (h - (block[3] - block[1])))

                pot_placed = [place_x, place_y, place_x + (block[2] - block[0]), place_y + (block[3] - block[1])]

                counter = 200
                block_placed = True

                while(rule(pot_placed, already_placed)):
                    counter -= 1
                    if counter == 0:
                        block_placed = False
                        break
                    place_x = int(random.random() * (w - (block[2] - block[0])))
                    place_y = int(random.random() * (h - (block[3] - block[1])))

                    pot_placed = [place_x, place_y, place_x + (block[2] - block[0]), place_y + (block[3] - block[1])]
                
                if block_placed:
                    already_placed.append(pot_placed)
                    origin.append(block)
                    for textbox in block_to_textboxes[encode_block(block)]:
                        new_texts.append({'box': [place_x + textbox['box'][0], place_y + textbox['box'][1], place_x + textbox['box'][2], place_y + textbox['box'][3]], 'text': textbox['text'], 'label': textbox['label']})
                else:
                    random_placed = False
                    break

            if random_placed:
                for blank, orig in zip(already_placed, origin):
                    # print(blank)
                    # print(orig)
                    blank_image[blank[1]:blank[3], blank[0]:blank[2]] = prev_image[orig[1]:orig[3], orig[0]:orig[2]]
                
                texts = new_texts
                document_group = layers.Layer(blank_image)

        if size is None:
            # Crop only region with data
            # boxes = [res['box'] for res in texts]
            # box_to_crop = find_bounding_box(boxes)
            # for res in texts:
            #     box = res['box']
            #     res['box'] = [box[0]-box_to_crop[0],box[1]-box_to_crop[1],box[2]-box_to_crop[0],box[3]-box_to_crop[1]]
                
            # cropped_image = document_group.image[box_to_crop[1]:, box_to_crop[0]:]
            # document_group = layers.Layer(cropped_image)
            #-----------------------------------------
            
            # Random resize of document_group
            scale = random.uniform(0.9, 1.1)
            width,height = document_group.size
            new_width = int(width * scale)
            new_height = int(height*new_width/width)
            
            document_group = layers.Layer(cv2.resize(document_group.image,(new_width,new_height)))
            
            for res in texts:
                res['box'] = resize_box_coordinates(res['box'], (width,height), (new_width,new_height))
            #-----------------------------------------
        else:
            max_width,max_height = size
            width, height = document_group.size
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            document_group = layers.Layer(cv2.resize(document_group.image,(new_width,new_height)))
    
        #self.effect.apply([document_group])

        return document_group, texts


def find_bounding_box(boxes):
    # Initialize min and max coordinates with the first box
    min_x = min([x[0] for x in boxes])
    min_y = min([x[1] for x in boxes])
    max_x = max([x[2] for x in boxes])
    max_y = max([x[3] for x in boxes])
    
    return [min_x, min_y, max_x, max_y]

def check_box(box, block):
    if block[0] <= box[0] and box[2] <= block[2] and block[1] <= box[1] and box[3] <= block[3]:
        return True
    
    return False

def encode_block(block):
    return f'{block[0]}{block[1]}{block[2]}{block[3]}'

def intersect(range1, range2):
    if (range1[0] <= range2[1] and range1[0] >= range2[0]) or (range1[1] <= range2[1] and range1[1] >= range2[0]) or (range2[0] <= range1[1] and range2[0] >= range1[0]) or (range2[1] <= range1[1] and range2[1] >= range1[0]):
        return True
    
    return False

def overlap(block1, block2):
    if intersect([block1[0], block1[2]], [block2[0], block2[2]]) and intersect([block1[1], block1[3]], [block2[1], block2[3]]):
        return True
    
    return False

def rule(block, already_placed):
    for placed in already_placed:
        if overlap(block, placed):
            return True
        
    return False