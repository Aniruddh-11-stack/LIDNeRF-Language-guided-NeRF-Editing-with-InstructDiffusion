import edit_cli
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
from os import listdir
import math
import random
import sys
from argparse import ArgumentParser

from PIL import Image
from lang_sam import LangSAM

def rp_main(model,model_sam,seed,args,fd,images=""):
    edited_image= edit_cli.main(model, args, seed)  # InstructDiffusion model is called
    
    text_prompt = args.edit
    input_image = Image.open(args.input).convert("RGB")
        
    masks, boxes, phrases, logits = model_sam.predict(edited_image, text_prompt)
    mask = masks.detach().cpu()
    mask_array = mask.numpy()

    if len(mask_array)>1:
        mask_array = [np.logical_or.reduce(mask_array)]
    elif len(mask_array)==0:
        print("Return")
        input_image.save(fd+"/final_imgs_"+str(seed)+"/"+images+".jpg")
        return

    print(len(mask_array))
    print(mask_array[0].shape)
    
    m = Image.fromarray(mask_array[0])

    img_np = np.array(edited_image)
    image_masked = img_np.copy()
    image_masked[np.logical_not(mask_array[0])] = 0

    im = Image.fromarray(image_masked)
    if args.num_imgs!=1:
        im.save(fd+"/image_masked_"+str(seed)+"/image_masked_"+images+"_"+str(seed)+".jpg")
    else:
        im.save(fd+"/image_masked_"+images+"_"+str(seed)+".jpg")

    masks1, boxes1, phrases1, logits1 = model_sam.predict(input_image, text_prompt)
    mask1 = masks1.detach().cpu()
    mask_array1 = mask1.numpy()

    if len(mask_array1)>1:
        mask_array1 = [np.logical_or.reduce(mask_array1)]
    elif len(mask_array1)==0:
        print("Return")
        return
    
    m1 = Image.fromarray(mask_array1[0])

    img_np1 = np.array(input_image)
    image_masked1 = img_np1.copy()
    image_masked1[np.logical_not(mask_array1[0])] = 0

    im1 = Image.fromarray(image_masked1)
    if args.num_imgs!=1:
        im1.save(fd+"/image_masked1_"+str(seed)+"/image_masked1_"+images+"_"+str(seed)+".jpg")
    else:
        im1.save(fd+"/image_masked1_"+images+"_"+str(seed)+".jpg")
    
    bg = img_np1 - image_masked1
    final_image = bg + image_masked
    final_image = Image.fromarray(final_image)
    if args.num_imgs!=1:
        final_image.save(fd+"/final_imgs_"+str(seed)+"/"+images+".jpg")
    else:
        final_image.save(fd+"/final_imgs_"+str(seed)+"/"+images+".jpg")

def main():
    parser = ArgumentParser()
    parser.add_argument("--resolution", default=512, type=int)
    parser.add_argument("--num_imgs", default=1, type=int)
    parser.add_argument("--steps", default=100, type=int)
    parser.add_argument("--config", default="configs/instruct_diffusion.yaml", type=str)
    parser.add_argument("--ckpt", default="/home/intel-user1/checkpoints/v1-5-pruned-emaonly-adaption-task-humanalign.ckpt", type=str)
    parser.add_argument("--vae-ckpt", default=None, type=str)
    parser.add_argument("--input", required=True, type=str)
    parser.add_argument("--outdir", default="logs", type=str)
    parser.add_argument("--edit", required=True, type=str)
    parser.add_argument("--cfg-text", default=5.0, type=float)
    parser.add_argument("--cfg-image", default=1.25, type=float)
    parser.add_argument("--outdir_mask", default="LangSAM_masks/masks_InsDif", type=str)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()

    model = edit_cli.initialize(args)
    model_sam = LangSAM()
    seed = random.randint(0, 100000) if args.seed is None else args.seed
    
    if args.num_imgs==1:
        rp_main(model,model_sam,seed,args,args.outdir)
    
    elif args.num_imgs>1:
        folder_dir = args.input
        final_direc = "/home/intel-user1/InstructDiffusion/logs/RP_tests"
        print(final_direc)
        os.mkdir(final_direc+"/final_imgs_"+str(seed))
        os.mkdir(final_direc+"/image_masked_"+str(seed))
        os.mkdir(final_direc+"/image_masked1_"+str(seed))
        for images in os.listdir(folder_dir):
            if (images.endswith(".jpg")):
                args.input = folder_dir+"/"+images
                rp_main(model,model_sam,seed,args,final_direc,images[:-4])
    

if __name__ == "__main__":
    main()