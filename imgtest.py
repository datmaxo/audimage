"""
Okay so I'm probably being silly and not understanding things
But can i just like, get these glitchy effects from direct manipulation of image file data
Let's find out! Lol
"""

import os
import shutil
import threading
import io
import tkinter as tk
from tkinter import filedialog as fd
from PIL import Image, ImageFile
from functools import partial
from copy import deepcopy as dcopy
import reverb as r

ImageFile.LOAD_TRUNCATED_IMAGES = True
path = "K:\\Normal Stuff\\Documents\\Audify\\experimental"

#thank christ, I already have code that saves images from raw binary
def rawToPNG (raw):
    pic = Image.open(io.BytesIO(raw))
    pic.save(os.getcwd() + "\\what.png")
    try: os.remove(path)
    except: pass

img = bytearray(open(fd.askopenfilename(filetypes=[("tiffs? lol?", "*.tiff")]), "r+b").read())
print(img[10])
print(type(img))

#boring - let's just multiply everything beyond the first couple lines by like 0.5
begin = int( len(img) * 0.0025 )
header = img[0:begin]
end = int( len(img) )
#for i in range(begin , end):
#    img[i] = min(int(img[i] * 1.5), 255)

rev = dcopy(img)
rev[begin:] = r.apply_reverb(img)[begin:]

rawToPNG(bytes(rev))
