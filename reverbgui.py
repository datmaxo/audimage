import tkinter as tk
import reverb
import io
import os
import sys
import threading
import time
import mp4toimages as m2i
from functools import partial
from tkinter import filedialog as fd
from PIL import Image, ImageFile, ImageTk

#TODO:
#   - decide if i'm using camel case or the underscore thing. this code is stylistically pretty inconsistent!
#   - get video rendering working
#   - implement effect pipeline
#   - investigate whether it's possible to render a single frame with many threads
#   - add a variety of effects! may require learning C++ for translation purposes

class testWin:
    def __init__ (self,root):
        self.tk = root
        self.img = ""
        self.raw = ""
        self.path = os.path.dirname(os.path.realpath(__file__)) #the dir of this file
        self.inputFilePath = ""
        self.renderThreads = 2
        self.params = []

        # determines how to write paths in a silly way, os.join is probably a better solution        
        self.slashString = "\\"
        if sys.platform.lower() != 'windows':
            self.slashString = '/'
        self.out = f"{self.slashString}temp{self.slashString}tmp.tiff"

        self.tk.title("Audimage")
        self.tk.geometry("900x450")

        #Establish Image preview window
        imfr = tk.Frame(self.tk, relief='groove', bd=3, padx=10, pady=5, width=600, height=400)
        imfr.pack(side="left", fill="both", expand=True, padx=3,pady=3)
        topfr = tk.Frame(imfr)
        topfr.pack(side="top", pady=5)
        tk.Label(topfr, text="Image Preview: ").pack(side='left',padx=3)
        self.tkimg = tk.Label(imfr)
        self.tkimg.pack(side='left',padx=3)
        imfr.pack_propagate(0)

        #Establish editor window
        fr = tk.Frame(self.tk, relief='groove', bd=3, padx=10, pady=5, width=300, height=400)
        fr.pack(side="right", fill="both", expand=True, padx=3,pady=3)
        selfr = tk.Frame(fr)
        selfr.pack(side="top", pady=5)
        tk.Label(selfr, text="Editor: ").pack(side='left',padx=3)
        self.baseFrame = fr
        self.baseFrame.pack_propagate(0)

        #Create 'open image' button - functionality handled by select_img()
        b = tk.Button(self.baseFrame, width=80, padx=3, pady=3, text="Open Image", command=partial(self.select_img))
        b.pack(side="top", padx=10, anchor="w")
        tk.Label(self.baseFrame).pack()

        #Create the reverb editing frame, set up the parameter names & default values
        paramNames = ["Delay Passes", "Delay", "Alpha", "T_60", "'B'", "'C'", "Output Gain", "Wet Gain", "Dry Gain"]
        df = [4, 0, 0.4, 1.5, 1, 1, 0.5, 1, 1]
        colour = "#a0bce8"
        fr = tk.Frame(self.baseFrame, relief='ridge', bd=3 , bg=colour, padx=10, pady=5)
        fr.pack(side="top", anchor="n", fill="x", padx=10)

        #Loop through all the parameters and render their input boxes :)
        self.tk.update_idletasks()
        for x in range(0,len(paramNames)):
            self.params.append(tk.DoubleVar())
            self.params[-1].set(df[x])
            newF = tk.Frame(fr, bg=colour)
            newF.pack(side="top", anchor="nw", fill="x", expand=False)
            l = tk.Label(newF, text=paramNames[x], bg=colour, justify="left")
            l.pack(side="left", padx=10, anchor="w")
            e = tk.Entry(newF, width=10, textvariable=self.params[-1], bg=colour, justify="right")
            e.pack(side="right", anchor="e", padx=10)
        self.effectFrame = fr
        self.tk.update_idletasks()

        #Create buttons to apply effects and save output -
        #functionality handled by apply_effects(), and !!!
        spacer_lol = tk.Label(self.baseFrame).pack(side="bottom")
        renderFrame = tk.Frame(self.baseFrame)
        renderFrame.pack(side="bottom", anchor="s")
        preview_b = tk.Button(renderFrame, width=15, padx=2, pady=8, text="Apply Changes", command=partial(self.apply_effects))
        preview_b.pack(side="left", anchor="w", padx=10)
        render_b = tk.Button(renderFrame, width=15, padx=2, pady=8, text="Save", command=partial(self.render))
        render_b.pack(side="right", anchor="e", padx=10)

        self.tk.mainloop()

    def select_img (self,_=''):
        #select file, overwrite the temp pic saved in local files with it
        #if a video file is selected, we first need to make a pic to preview
        self.inputFilePath = fd.askopenfilename()
        if (self.inputFilePath[-4:] == ".mp4"):
            self.img = Image.open(m2i.getFirstFrame(self.inputFilePath))
        else:
            self.img = Image.open(self.inputFilePath)
        file = self.path + self.out
            
        self.img.save(file)
        self.raw = bytearray(open(file, "r+b").read())
        pic = Image.open(file).resize((560,380), Image.LANCZOS)
        self.show_img(pic)

    #actually apply image to frame
    def show_img (self, pic):
        render = ImageTk.PhotoImage(pic)
        self.tkimg.configure(image=render)
        self.tkimg.image = render
        self.tk.update_idletasks()

    #run the reverby process on the selected image
    #i'm gonna use a different function for video rendering but for code neatness i should merge it down to one at some point!
    def apply_effects(self,_=''):
        if (self.img != ""):
            ps = []
            for i in self.params: ps.append(i.get())
            header = 3044 #int( len(self.raw) * 0.0008 )
            out = self.raw[:header] + reverb.apply_reverb(self.raw, ps)[header:]

            pic = Image.open(io.BytesIO(out))
            pic.save(self.path + f"{self.slashString}temp{self.slashString}tmp_edited.tiff")
            pic = Image.open(self.path + f"{self.slashString}temp{self.slashString}tmp_edited.tiff").resize((560,380), Image.LANCZOS)
            self.show_img(pic)
            return pic
        return False

    #default rendering function
    #if a video has been selected, pass all the hard work over to render_video()
    #if an image has been selected, just save the temp_edited.tiff image somewhere else lmao
    def render(self,_=''):
        outpath = fd.asksaveasfilename()
        if len(outpath) > 0:
            if (self.inputFilePath[-4:] == ".mp4"):
                self.render_video(outpath)
            else:
                if ('.' not in outpath): outpath += ".png" #default file extension
                final_pic = self.apply_effects()
                if type(final_pic) != bool:
                    #final_pic = Image.open(io.BytesIO(self.path, f"temp{self.slashString}tmp_edited.tiff"))
                    final_pic.save(outpath)
                else:
                    tk.messagebox.showerror(title='Save Error', message='The saving process has unfortunately failed :(\nPlease try again.')

    """i've had a thought - why am i splitting the video into pieces before executing the threads?
    m2i has functionality to get a specific frame based on index
    so maybe it'd be better to just let the threads request specific frames as and when they need them?
    I'm gonna implement it the 'normal' way first but it's worth giving a go!
    """
    def render_video(self, outpath):
        #split video into individual frames, load effect parameters, get framerate
        self.totalFrames = m2i.convert(self.inputFilePath)
        params = []
        for i in self.params: params.append(i.get())
        framerate = m2i.getFramerate(self.inputFilePath)

        renderTime = time.time()        
        threads = []
        for i in range(0, self.renderThreads):
            n = "Render-Thread#" + str(i + 1)
            t = threading.Thread(target=partial(self.render_frame, i, params), name=n)
            threads.append(t)
            t.start()
            print(n + " started >:)")

        #wait for all threads to finish execution
        for thread in threads: thread.join()
        m2i.render(framerate, outpath)
        print("rendered in %d seconds!" % round(time.time() - renderTime, 5))

    def render_frame(self, current_frame, params):
        f = "frame%d" % current_frame
        rawframe = bytearray(open(self.path + f"{self.slashString}temp{self.slashString}" + f + ".tiff", "r+b").read())
        header = 3044
        out = rawframe[:header] + reverb.apply_reverb(rawframe, params)[header:]

        #save the altered frame - delete the original .tiff
        frameNo = format(current_frame, '06d')
        pic = Image.open(io.BytesIO(out))
        pic.save(self.path + f"{self.slashString}temp{self.slashString}frame{frameNo}.png")
        try: os.remove(self.path + f"{self.slashString}temp{self.slashString}{f}.tiff")
        except: pass
        #print(current_frame) #test to see threads starting okay

        #if there's more to render, jump to the next frame
        nextFrame = current_frame + self.renderThreads
        if (nextFrame < self.totalFrames):
            self.render_frame(nextFrame, params)

x = testWin(tk.Tk())
