#! /usr/bin/env python
# Requires pillow:
# pip install pillow
import os
import sys
import glob
from PIL import Image
from fractions import Fraction


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
    return fs+"_"+str(width)+"x"+str(height)+"_"+fbasename


def getnamenosize(fbasename):
    import re
    return re.sub(r"\d+ ?(x|_|-) ?\d+(_|-)?", "", fbasename)


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


def resize(file):
    targetratio = 16/9  # w/h
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
    newimg.save(targetpath+getnamenosize(os.path.basename(file)))
    img.close()


def main(action, inpath):
    for ext in ["jpg", "jpeg", "png"]:
        for file in glob.glob(inpath + "/*."+ext):
            fbasename = os.path.basename(file)
            fpath = os.path.dirname(file)
            # fpathname, file_extension = os.path.splitext(file)
            width, height, ratio = getimagesize(file)
            if  action == "remove" and str(width) in fbasename:
               sys.stdout.write(
                    "File name (%s) already contains width (%s)\n" % (fbasename, width))
               newname = getnamenosize(fbasename)
               sys.stdout.write("renaming %s -> %s\n" %
                                     (fbasename, newname))
               os.rename(file, fpath+"/"+newname)
            elif action == "remove" and str(height) in fbasename:
               sys.stdout.write(
                    "File name (%s) already contains height (%s)\n" % (fbasename, height))
               newname = getnamenosize(fbasename)
               sys.stdout.write("renaming %s -> %s\n" %
                                     (fbasename, newname))
               os.rename(file, fpath+"/"+newname)
            elif action == "rename":
                    newname = getnamefromsize(getnamenosize(fbasename), width, height, ratio)
                    sys.stdout.write("renaming %s -> %s\n" %
                                     (fbasename, newname))
                    os.rename(file, fpath+"/"+newname)
            elif action == "resize":
                resize(file)

def usage():
    sys.stdout.write("Usage: %s rename|remove|resize <images path>\n" % sys.argv[0])


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 1:
        main(args[0], args[1])
    else:
        usage()
