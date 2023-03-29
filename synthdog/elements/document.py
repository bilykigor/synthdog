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
            document_group = layers.Layer(document_group.image)
        else:
            max_width,max_height = size
            width, height = document_group.size
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            document_group = layers.Layer(cv2.resize(document_group.image,(new_width,new_height)))
    
        #self.effect.apply([document_group])

        return document_group, texts
