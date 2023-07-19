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
        
        if size is None:
            # Crop only region with data
            boxes = [res['box'] for res in texts]
            box_to_crop = find_bounding_box(boxes)
            for res in texts:
                box = res['box']
                res['box'] = [box[0]-box_to_crop[0],box[1]-box_to_crop[1],box[2]-box_to_crop[0],box[3]-box_to_crop[1]]
                
            cropped_image = document_group.image[box_to_crop[1]:box_to_crop[3], box_to_crop[0]:box_to_crop[2]]
            document_group = layers.Layer(cropped_image)
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