"""
Donut
Copyright (c) 2022-present NAVER Corp.
MIT License
"""
from synthtiger import components, layers
from .utils import  read_annotations, clean_texture

class Paper:
    def __init__(self, config):
        self.image = components.BaseTexture(**config.get("image", {}))

    def generate(self, size):
        paper_layer = layers.RectLayer(size, (255, 255, 255, 255))
        self.image.apply([paper_layer])

        return paper_layer


class CheckPaper:
    def __init__(self, config):
        self.image = components.BaseTexture(**config.get("image", {}))

    def generate(self, size=None):
        meta = self.image.sample(None)
        texture = self.image.data(meta)
        
        size = (meta["w"],meta['h'])
        
        path = meta['path']
        path = ''.join(path.split('.')[:-1])+'.json'
        annotation_objects = read_annotations(path)
        
        texture = clean_texture(texture, annotation_objects,meta["alpha"])
        
        paper_layer = layers.RectLayer(size, (255, 255, 255, 255))
        paper_layer.image = texture

        return paper_layer, meta
    