import cv2
import os
from PIL import Image
from tkinter import filedialog as fd

def convert (file,name="frame") :
    vid = cv2.VideoCapture(file)
    success,image = vid.read()
    out = os.getcwd() + "\\temp"
    cv2.imwrite(out+"\\size.jpg", image)
    count = 0
    while success:
        cv2.imwrite(out+"\\"+name+"%d.jpg" % count, image)
        im = Image.open(out+"\\"+name+"%d.jpg" % count)
        im.convert()
        im.save(out+"\\"+name+"%d.tiff" % count)
        try:
            if (os.path.exists(out+"\\"+name+"%d.jpg" % count)): os.remove(out+"\\"+name+"%d.jpg" % count)
        except: pass
        success,image = vid.read()
        print("Read a new frame: " + str(success))
        count += 1
    return count

def render (framerate, vidname) :
    image_folder = os.getcwd() + "\\temp"
    video_name = vidname
    if ".mp4" in video_name == False:
        video_name += ".mp4"

    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    print(images)
    frame = cv2.imread(os.path.join(image_folder, images.pop()))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, framerate, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))
        print(image)

    cv2.destroyAllWindows()
    video.release()

def getFramerate (file):
    cap = cv2.VideoCapture(file)
    return cap.get(cv2.CAP_PROP_FPS)

def getFirstFrame (file):
    vid = cv2.VideoCapture(file)
    success,image = vid.read()
    out = os.getcwd() + "\\temp"
    cv2.imwrite(out+"\\tmp.jpg", image)
    im = Image.open(out+"\\tmp.jpg")
    im.convert()
    im.save(out+"\\init-frame.tiff")
    return (out+"\\init-frame.tiff")

def getFrame (file, i):
    print("\n\nI IS %d\n\n" % i)
    cap = cv2.VideoCapture(file)
    cap.set(cv2.CAP_PROP_POS_FRAMES,i)
    success,image = cap.read()
    if success == False:
        return None
    else:
        out = os.getcwd() + "\\temp"
        cv2.imwrite(out+"\\tmp.jpg", image)
        im = Image.open(out+"\\tmp.jpg")
        im.convert()
        im.save(out+"\\tmp.tiff")
        return (out+"\\tmp.tiff")
    
