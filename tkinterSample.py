import sys
import numpy as np
import tkinter
from tkinter import filedialog as tkFileDialog  # python3
from PIL import Image, ImageTk, ImageDraw
import time
import random
import copy

ww = 500
hh = 800


class Application(tkinter.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.BG = "white"
        self.button1 = tkinter.Button(self, text="select")
        self.button1.pack()
        self.button1.bind("<1>", self.photoselect)
        self.button2 = tkinter.Button(self, text="start")
        self.button2.pack()
        self.button2.bind("<1>", self.start)
        self.button3 = tkinter.Button(self, text="change")
        self.button3.pack()
        self.button3.bind("<1>", self.changeBG)
        self.originC = tkinter.Canvas(self, bg="white", height=hh, width=ww)
        self.originC.pack(side="left")
        self.rightC = tkinter.Canvas(self, bg=self.BG, height=hh, width=ww)
        self.rightC.pack(side="right")

    def changeBG(self, event):
        self.BG = "black" if self.BG == "white" else "white"
        self.rightC.configure(bg=self.BG)
        self.rightC.pack(side="top")

    def photoselect(self, event):
        filename = tkFileDialog.askopenfilename()
        self.img = Image.open(filename)
        if len(self.img.getbands()) == 4:
            self.img = self.img.convert("RGB")
        self.image, self.w, self.h = self.photoresize(self.img)
        self.image_ = ImageTk.PhotoImage(self.image)
        self.originC.create_image(0, 0, image=self.image_, anchor=tkinter.NW)
        self.rightC.configure(width=self.w, height=self.h)
        self.rightC.pack(side="top")

    def photoresize(self, img):
        imw, imh = img.size
        if imw/imh > ww/hh:
            return img.resize((ww, int(imh*ww/imw))), ww, int(imh*ww/imw)
        else:
            return img.resize((int(imw*hh/imh), hh)), int(imw*hh/imh), hh

    def start(self, event):
        self.evolve()

    def evolve(self):
        #originalHash = imagehash.dhash(self.img)
        originalHash = np.array(self.image)/255
        self.image1 = Image.new("RGB", (self.w, self.h), self.BG)
        draw = ImageDraw.Draw(self.image1, 'RGBA')
        generationNow = [Individual(self.w, self.h) for i in range(1)]
        self.time_ = time.time()
        self.num = 1
        for k in range(600000):
            newone = Individual(self.w, self.h)
            newone.shapes = copy.deepcopy(generationNow[0].shapes)
            generationNow.append(newone)

            for i in range(1):
                self.mutation(generationNow[i])
            self.hashReg(originalHash, generationNow, self.image1)

            generationNow = self.select1(generationNow)
            # random.shuffle(generationNow)

            if k % 100 == 0:
                print(k, time.time()-self.time_, len(generationNow[0].shapes))
                draw.rectangle([0, 0, self.w, self.h], fill=self.BG)
                for shape in generationNow[0].shapes:
                    draw.polygon(shape[0], fill=shape[1])
                self.image2 = ImageTk.PhotoImage(self.image1)
                self.rightC.create_image(
                    0, 0, image=self.image2, anchor=tkinter.NW)
                self.rightC.update()
                self.time_ = time.time()
                if k % 1000 == 0:
                    print("evolve", self.num)
                    for i in range(1):
                        draw.rectangle([0, 0, self.w, self.h], fill=self.BG)
                        for shape in generationNow[0].shapes:
                            draw.polygon(shape[0], fill=shape[1])
                        path = "tkisam/image"+format(i)+".png"
                        self.image1.save(path)

    def hashReg(self, originalHash, generationNow, image):
        draw = ImageDraw.Draw(image, 'RGBA')
        for i in range(2):
            draw.rectangle([0, 0, self.w, self.h], fill=self.BG)
            for shape in generationNow[i].shapes:
                draw.polygon(shape[0], fill=shape[1])
            comHash = np.array(image)/255
            generationNow[i].hash = np.around(
                np.sum(np.square(originalHash-comHash)))

    def select1(self, generationNow):  # エリート
        generationNext = []
        hashList = [tmp.hash for tmp in generationNow]
        index = 0 if hashList[0] <= hashList[1] else 1
        hashList.pop(index)
        self.num += 1
        generationNow[index].dd = 0
        generationNext.append(generationNow.pop(index))

        return generationNext

    def mutation(self, ind):
        rate = 700
        sl = len(ind.shapes)
        if sl > 0 and random.randrange(1500) == 0:
            ind.removeGene(random.randrange(0, sl))
            sl -= 1
        if sl < 200 and random.randrange(rate) == 0:
            ind.addGene(self.w, self.h)
            sl += 1
        if random.randrange(rate) == 0 and sl > 1:
            ind.moveGene()
        ind.mutation()


class Individual():

    def __init__(self, w, h):
        self.shapes = []
        self.dd = 0
        self.hash = 0
        self.w, self.h = w, h

    def addGene(self, w, h):
        self.dd = 1
        color = (random.randint(0, 255), random.randint(0, 255),
                 random.randint(0, 255), random.randint(25, 170))
        x1 = random.randint(0, w)
        x2 = max(0, min(x1+random.randint(-5, 5), self.w-1))
        x3 = max(0, min(x1+random.randint(-5, 5), self.w-1))
        y1 = random.randint(0, h)
        y2 = max(0, min(y1+random.randint(-5, 5), self.h-1))
        y3 = max(0, min(y1+random.randint(-5, 5), self.h-1))
        if len(self.shapes) > 0:
            index = random.randrange(0, len(self.shapes))
            self.shapes.insert(index, [[x1, y1, x2, y2, x3, y3], color])
        else:
            self.shapes.append([[x1, y1, x2, y2, x3, y3], color])

    def removeGene(self, index):
        self.dd = 1
        self.shapes.pop(index)

    def moveGene(self):
        self.dd = 1
        index = random.randrange(0, len(self.shapes))
        tmp = self.shapes.pop(index)
        index = random.randrange(0, len(self.shapes))
        self.shapes.insert(index, tmp)

    def mutation(self):
        self.shapes = [[self.changePolygon(self.shapes[i][0]), self.changeColor(
            self.shapes[i][1])] for i in range(len(self.shapes))]

    def changePolygon(self, shapes):
        rate = 1500
        if random.randrange(rate) == 0:
            self.dd = 1
            self.addPoint(shapes)
        if random.randrange(rate) == 0:
            self.dd = 1
            self.removePoint(shapes)
        shapes = [flatten for inner in [self.movePoint(
            shapes[i*2], shapes[i*2+1]) for i in range(len(shapes)//2)] for flatten in inner]
        return shapes

    def addPoint(self, shapes):
        if len(shapes) < 20:
            index = random.randrange(1, len(shapes)//2)*2
            prevx, prevy, nextx, nexty = shapes[index-2:index+2]

            newx = (prevx + nextx)//2
            newy = (prevy + nexty)//2

            shapes[index:0] = [newx, newy]

    def removePoint(self, shapes):
        if len(shapes) > 6:
            index = random.randrange(0, len(shapes)//2)*2
            del shapes[index:index+2]

    def movePoint(self, x, y):
        rate = 1500
        if random.randrange(rate) == 0:
            self.dd = 1
            x = max(0, min(x+random.randint(-100, 100), self.w-1))
            y = max(0, min(y+random.randint(-100, 100), self.h-1))
        if random.randrange(rate) == 0:
            self.dd = 1
            x = max(0, min(x+random.randint(-20, 20), self.w-1))
            y = max(0, min(y+random.randint(-20, 20), self.h-1))
        if random.randrange(rate) == 0:
            self.dd = 1
            x = max(0, min(x+random.randint(-5, 5), self.w-1))
            y = max(0, min(y+random.randint(-5, 5), self.h-1))
        return [x, y]

    def changeColor(self, color):
        rate = 1500
        c1, c2, c3, alpha = color
        if random.randrange(rate) == 0:
            self.dd = 1
            c1 = random.randint(0, 255)
        if random.randrange(rate) == 0:
            self.dd = 1
            c2 = random.randint(0, 255)
        if random.randrange(rate) == 0:
            self.dd = 1
            c3 = random.randint(0, 255)
        if random.randrange(rate) == 0:
            self.dd = 1
            alpha = random.randint(80, 170)
        color = (c1, c2, c3, alpha)
        return color


if __name__ == "__main__":
    root = tkinter.Tk()
    root.geometry(str(ww*2+50)+"x"+str(hh+50))
    app = Application(master=root)
    app.mainloop()
