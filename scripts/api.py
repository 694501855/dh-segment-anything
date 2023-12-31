
 
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
from PIL import Image
import numpy as np
import cv2


import os



#
#import cv2
#img = cv2.imread(imagePath)
#img_cv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)


 




#kk = masks
file=os.path.join(os.path.dirname(os.path.dirname(__file__)),"models","sam_vit_h_4b8939.pth")
sam = sam_model_registry["default"](checkpoint=str(file))
def img_masks(img) :
    img_np = np.array(img.convert("RGB"))
    mask_generator = SamAutomaticMaskGenerator(sam)
    annotations = mask_generator.generate(img_np)
    annotations = sorted(annotations, key=lambda x: x['area'])
    imgs=[]
    for idx, annotation in enumerate(annotations):
        img_tmp = np.zeros((img_np.shape[0], img_np.shape[1], 3))
        img_tmp[annotation['segmentation']] = img_np[annotation['segmentation']]
        img_np[annotation['segmentation']] = np.array([0, 0, 0])
        img_tmp = Image.fromarray(img_tmp.astype(np.uint8))
        imgs.append(img_tmp)
    return imgs
       
    

if __name__ == '__main__':
    imagePath=os.path.join(os.path.dirname(os.path.dirname(__file__)),"scripts","001.jpg")  
    img=Image.open(imagePath)
    imgs=img_masks(img)
    dirname=os.path.join(os.path.dirname(os.path.dirname(__file__)),"imgs")
    if not os.path.exists(dirname) : os.makedirs(dirname)
    for i,item in enumerate(imgs) :
        file=os.path.join(dirname, f"{i}.png")
        item.save(file)


from fastapi import FastAPI, Body
from modules.api.models import *
from modules.api import api
def sam_api(_, app: FastAPI):
    @app.post("/segment_anything/get_img_masks")
    async def get_img_masks(input_image: str = Body(""), model:str=Body("sam_vit_h_4b8939.pth")):
        img0 =api.decode_base64_to_image(input_image)
        imgs=img_masks(img0)
        img_texts=[]
        for i,item in enumerate(imgs) :
            rimg=api.encode_pil_to_base64(item)
            img_texts.append(rimg)
        return {"masks": img_texts}


import logging
logger = logging.getLogger(__name__)

try:
    import modules.script_callbacks as script_callbacks

    script_callbacks.on_app_started(sam_api)
    logger.debug("sam_api API logger")
except:
    pass
