"""
Donut
Copyright (c) 2022-present NAVER Corp.
MIT License
"""
import os
import numpy as np
from synthtiger import components, layers
from .utils import  read_annotations, clean_texture, clean_texture2

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
        meta = self.image.sample(size)
        texture = self.image.data(meta)
        
        size = (meta["w"],meta['h'])
        
        path = meta['path']
        path = ''.join(path.split('.')[:-1])+'.json'
        annotation_objects = read_annotations(path)
        
        texture = clean_texture2(texture, annotation_objects,meta["alpha"])
        
        paper_layer = layers.Layer(texture)

        return paper_layer, meta
    
    
class RemittancePaper:
    def __init__(self, config):
        image_config = config.get("image", {})
        self.image_path = image_config['paths'][0]
        image_files = os.listdir(self.image_path)
        self.image_files = [x for x in image_files if x.split('.')[-1]!='json']
        
        self.image = components.BaseTexture(**config.get("image", {}))

    def generate(self, size=None):
        image_path = os.path.join(self.image_path,np.random.choice(self.image_files))
        meta = self.image.sample({'path':image_path})
        texture = self.image.data(meta)
        
        size = (meta["w"],meta['h'])
        
        path = meta['path']
        path = ''.join(path.split('.')[:-1])+'.json'
        annotation_objects = read_annotations(path)
        
        texture = clean_texture2(texture, annotation_objects,meta["alpha"])
        
        paper_layer = layers.Layer(texture)

        return paper_layer, meta
    