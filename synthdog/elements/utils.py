
import math
import cv2
import numpy as np
import json
from PIL import Image

def preprocess_image(image):
    #image = np.array(source_image) 
    # Convert RGB to BGR 
    image = image[:, :, ::-1].copy() 
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    image = Image.fromarray(thresh)
    return image


def read_annotations(path):
    with open(path) as json_file:
        annotation_objects = json.load(json_file)
        
    return annotation_objects
  
    
def clean_texture(texture, annotation_objects,alpha):
    formated_objects = []
    for obj in annotation_objects:
        name = obj['title']
        bbox = obj['bbox']
        top, left, height, width = bbox['top'], bbox['left'], bbox['height'], bbox['width']
        right = left + width
        bottom = top + height
        left_top     = [left,  top]
        right_top    = [right, top]
        right_bottom = [right, bottom]
        left_bottom  = [left,  bottom]
        formated_objects.append([name, [left_top, right_top, right_bottom, left_bottom]])
    
    texture = inpaint_box(texture[..., :3].astype(np.uint8), formated_objects)
    texture = Image.fromarray(texture.astype(np.uint8))
    texture = texture.convert("RGBA")
    texture = np.array(texture, dtype=np.float32)
    texture[..., 3] *= alpha
    
    return texture


def clean_texture2(image, annotation_objects,alpha):
    image = preprocess_image(image[..., :3].astype(np.uint8))
    
    image_cv2 = np.array(image) 
    mask = np.zeros(image_cv2.shape, dtype='uint8')
    image_cv2_reverse = cv2.bitwise_not(image_cv2)

    for obj in annotation_objects:
        bbox = obj['bbox']
        top, left, height, width = bbox['top'], bbox['left'], bbox['height'], bbox['width']
        right = left + width
        bottom = top + height
        mask[top:bottom, left:right] = image_cv2_reverse[top:bottom, left:right]

    #mask[157:157+30, 1221:1221+205] = image_cv2_reverse[157:157+30, 1221:1221+205]
    
    image_cv2 = cv2.inpaint(image_cv2,mask,3,cv2.INPAINT_TELEA)
    
    image = Image.fromarray(image_cv2.astype(np.uint8))
    image = image.convert("RGBA")
    image = np.array(image, dtype=np.float32)
    image[..., 3] *= alpha
    
    return image
    
       
def midpoint(x1, y1, x2, y2):
    x_mid = int((x1 + x2)/2)
    y_mid = int((y1 + y2)/2)
    return (x_mid, y_mid)


def inpaint_box(image, boxes):
    mask = np.zeros(image.shape[:-1], dtype='uint8')
    
    for _, box in boxes:
        x0, y0 = box[0]
        x1, y1 = box[1]
        x2, y2 = box[2]
        x3, y3 = box[3]

        x_mid0, y_mid0 = midpoint(x1, y1, x2, y2)
        x_mid1, y_mi1 = midpoint(x0, y0, x3, y3)

        thickness = int(math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 ))

        cv2.line(mask, (x_mid0, y_mid0), (x_mid1, y_mi1), 255,  thickness)
        inpainted_img = cv2.inpaint(image, mask, 7, cv2.INPAINT_NS)
        
    return inpainted_img