#! /usr/bin/env python
# Requires pillow:
# pip install pillow
import os
import sys
import glob
from PIL import Image
from fractions import Fraction
import random
import re

def get_image_size(file):
    im = Image.open(file)
    width, height = im.size
    ratio = width/height
    im.close()
    return width, height, ratio

def ratio_to_string(ratio):
     frac = Fraction(str(ratio)).limit_denominator(100)
     return str(frac).replace("/", "x")

def choose_name_from_size(fbasename, width, height, ratio):
    rounded_ratio = str(round(ratio, 2)).replace(".", "-")
    ratio_string = ratio_to_string(ratio)
    return f"{rounded_ratio}_{ratio_string}_{fbasename}"

def remove_size_from_name(fbasename,addrnd=False):
    clean = re.sub(r"(\d(x| |_|-)?)+", "", fbasename)
    if addrnd:
        clean = str(random.randint(0, 999))+clean
    return clean

def get_mean_color(img):
    rgb_im = img.convert('RGB')
    imgwidth, imgheight = img.size
    sumr = sumg = sumb = nb = 0
    for x in range(0, imgwidth, int(imgwidth/100)):
        for y in range(0, imgheight, int(imgheight/100)):
            r, g, b = rgb_im.getpixel((x, y))
            sumr += r
            sumg += g
            sumb += b
            nb += 1
    return (int(sumr/nb), int(sumg/nb), int(sumb/nb))


def resize(file, target_ratio= 16/9):
    # targetratio= 16/9   # w/h
    img = Image.open(file)
    new_width, new_heigth = imgwidth, imgheight = img.size
    dx = dy = 0
    img_ratio = imgwidth / imgheight
    if img_ratio > target_ratio:  # too wide, increase height
        new_heigth = int(new_width / target_ratio)
        dy = int((new_heigth - imgheight)/2)
        newimg = Image.new('RGB', (new_width, new_heigth), get_mean_color(img))#uniform background color for top/bottom bands
        newimg.paste(img, (dx, dy))
    elif img_ratio < target_ratio:  # too high, increase width
        new_width = int(new_heigth * target_ratio)
        dx = int((new_width - imgwidth)/2)
        newimg = img.resize((new_width, new_heigth))#stretch - stretched bg works fine for added width, not height
        newimg.paste(img, (dx, dy))
    else:
        newimg = img.copy()
    targetpath = os.path.dirname(file)+"/resize_"+ratio_to_string(target_ratio)+"/"
    if not(os.path.exists(targetpath)):
         os.mkdir(targetpath)
    #newimg.save(targetpath+remove_size_from_name(os.path.basename(file)))
    newimg.save(targetpath+"resized_"+os.path.basename(file))
    img.close()

def check_name(fpath,newname):
    return os.path.isfile(fpath+"/"+newname)

def main(action, inpath, targetratio):
    for ext in ["jpg", "jpeg", "png"]:
        for file in glob.glob(inpath + "/*."+ext):
            fbasename = os.path.basename(file)
            fpath = os.path.dirname(file)
            # fpathname, file_extension = os.path.splitext(file)
            width, height, ratio = get_image_size(file)
            if  action == "remove" and (str(width) in fbasename or str(height) in fbasename):
                newname = remove_size_from_name(fbasename)
                while check_name(fpath,newname):
                    newname = remove_size_from_name(fbasename,True)
                print(f"renaming {fbasename} -> {newname}" )
                os.rename(file, fpath+"/"+newname)
            elif action == "rename":
                newname = choose_name_from_size(remove_size_from_name(fbasename), width, height, ratio)
                while check_name(fpath,newname):
                    newname = choose_name_from_size(remove_size_from_name(fbasename,True), width, height, ratio)
                print(f"renaming {fbasename} -> {newname}" )
                os.rename(file, fpath+"/"+newname)
            elif action == "resize":
                print(f"resizing {fbasename} to {targetratio}")
                resize(file, targetratio)

def usage():
    print(f"Usage: {sys.argv[0]} rename|remove|resize <images path> <resize target ratio>")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 1:
        action = args[0]
        inpath = args[1]
        assert action in ["rename","remove","resize"]
        assert os.path.exists(inpath) is True
        targetratio = None
        if len(args) > 2:
            assert args[2].replace('.','',1).isdigit() #isdigit doesnt handle decimals, just remove the . for the test
            targetratio = float(args[2])
        main(action, inpath, targetratio)
    else:
        usage()
