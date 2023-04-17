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

def getimagesize(file):
    im = Image.open(file)
    width, height = im.size
    ratio = width/height
    im.close()
    return width, height, ratio

def ratiotostring(ratio):
     frac = Fraction(str(ratio)).limit_denominator(100)
     return str(frac).replace("/", "x")

def getnamefromsize(fbasename, width, height, ratio):
    fs = ratiotostring(ratio)
    rstr = str(round(ratio, 2)).replace(".", "-")
    return f"{rstr}_{fs}_{fbasename}"

def getnamenosize(fbasename,addrnd=False):
    clean = re.sub(r"(\d(x| |_|-)?)+", "", fbasename)
    if addrnd:
        clean = str(random.randint(0, 999))+clean
    return clean

def getmeancolor(img):
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


def resize(file, targetratio= 16/9):
    # targetratio= 16/9   # w/h
    img = Image.open(file)
    newwidth, newheigth = imgwidth, imgheight = img.size
    dx = dy = 0
    imgratio = imgwidth / imgheight
    if imgratio > targetratio:  # too wide, increase height
        newheigth = int(newwidth / targetratio)
        dy = int((newheigth - imgheight)/2)
        newimg = Image.new('RGB', (newwidth, newheigth), getmeancolor(img))#uniform background color for top/bottom bands
        newimg.paste(img, (dx, dy))
    elif imgratio < targetratio:  # too high, increase width
        newwidth = int(newheigth * targetratio)
        dx = int((newwidth - imgwidth)/2)
        newimg = img.resize((newwidth, newheigth))#stretch - stretched bg works fine for added width, not height
        newimg.paste(img, (dx, dy))
    else:
        newimg = img.copy()
    targetpath = os.path.dirname(file)+"/resize_"+ratiotostring(targetratio)+"/"
    if not(os.path.exists(targetpath)):
         os.mkdir(targetpath)
    #newimg.save(targetpath+getnamenosize(os.path.basename(file)))
    newimg.save(targetpath+"resized_"+os.path.basename(file))
    img.close()

def checkname(fpath,newname):
    return os.path.isfile(fpath+"/"+newname)

def main(action, inpath, targetratio):
    for ext in ["jpg", "jpeg", "png"]:
        for file in glob.glob(inpath + "/*."+ext):
            fbasename = os.path.basename(file)
            fpath = os.path.dirname(file)
            # fpathname, file_extension = os.path.splitext(file)
            width, height, ratio = getimagesize(file)
            if  action == "remove" and (str(width) in fbasename or str(height) in fbasename):
                newname = getnamenosize(fbasename)
                while checkname(fpath,newname):
                    newname = getnamenosize(fbasename,True)
                print(f"renaming {fbasename} -> {newname}" )
                os.rename(file, fpath+"/"+newname)
            elif action == "rename":
                newname = getnamefromsize(getnamenosize(fbasename), width, height, ratio)
                while checkname(fpath,newname):
                    newname = getnamefromsize(getnamenosize(fbasename,True), width, height, ratio)
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
