import pygame
import random
import cv2
import numpy as np
import threading
import time
# import keyboard
import math
import os
from multiprocessing import Process, Queue
from numpy.linalg import lstsq
from numpy import ones,vstack
display_width = 1400
display_height = 800

os.environ['SDL_VIDEO_CENTERED'] = '1'

class Item:
    yacc = 0.28
    def __init__(self,image):
        if random.randint(0,1)==0:#move right
            self.x = random.randint(0, int(display_width/2))
            self.y = display_height
            self.yvel = random.randint(-22,-19)
            self.xvel = random.randint(3,6)
        else:
            self.x = random.randint(int(display_width/2), display_width)
            self.y = display_height
            self.yvel = random.randint(-22,-19)
            self.xvel = random.randint(-6,-3)
        if image != "pineapple.png" and image != "shrooms.png":
            self.width=200
            self.height=200
        else:
            self.width=140
            self.height=240
        self.isBomb= (image=="bomb.png")
        image = pygame.image.load(image)
        image = pygame.transform.scale(image, (self.width, self.height))
        self.image = image


    def move(self):
        self.x += self.xvel
        self.y += self.yvel
        self.yvel += self.yacc

    def isCollided(self, x, y):
        if (math.pow((int(self.x+self.width/2)-x),2) + math.pow((int(self.y+self.height/2)-y),2))<10000:
            return True
        else:
            return False

class Explosion:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.width=200
        self.height=200
        image = pygame.image.load("nuke.png")
        image = pygame.transform.scale(image, (self.width, self.height))
        self.image = image


    def decreaseSize(self):
        self.width -=1
        self.height -=1
        if self.width==0 or self.height==0:
            return True
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        return False


def game(xyq, otherxyq):
    pygame.init()
    disp = pygame.display.set_mode((display_width,display_height))
    clock = pygame.time.Clock()

    cursor = pygame.image.load("cursor.jpg")
    cursor = pygame.transform.scale(cursor, (50,50))
    cursorx,cursory=0,0
    othercursor = pygame.image.load("cursor.jpg")
    othercursor = pygame.transform.scale(othercursor, (50,50))
    othercursorx,othercursory=0,0

    # define the RGB value for white,
    #  green, blue colour .
    white = (255, 255, 255)
    green = (0, 255, 0)
    black = (0, 0, 0)
    font = pygame.font.Font('freesansbold.ttf', 48)
    square = pygame.image.load("redsquare.png")

    try:
        # time.sleep(2)
        limits={"tl":0, "tr":0, "bl":0, "br":0}
        cornerCords={"tl":(0,0), "tr":(display_width-100,0), "bl":(0,display_height-100), "br":(display_width-100,display_height-100)}
        for pos in limits.keys():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt
            print('Put hand in ' +pos+' corner')
            # create a text suface object,
            # on which text is drawn on it.
            text = font.render('Put hand in each corner', True, green, black)
            textRect = text.get_rect()
            textRect.center = (display_width // 2,display_height // 2)
            disp.blit(text,textRect)
            disp.blit(square, cornerCords[pos])

            pygame.display.update()
            for i in range(10):
                time.sleep(0.1)
            startTime=time.time()
            while not xyq.empty():#empty queue
                xyq.get()
            cursorx,cursory=0,0
            while int(time.time())-int(startTime)<3:
                if not xyq.empty():
                    avgx, avgy=0,0
                    count=0
                    while not xyq.empty():
                        val=xyq.get()
                        avgx+=val[0]
                        avgy+=val[1]
                        count+=1
                    avgx=int(avgx/count)
                    avgy=int(avgy/count)
                    avgx=int((avgx+cursorx)/2)
                    avgy=int((avgy+cursory)/2)
                    cursorx,cursory=avgx,avgy
            print(cursorx,cursory)
            limits[pos]={"x":cursorx,"y":cursory}
        bounds={}
        bounds["ty"]=(limits["tl"]["y"]+limits["tr"]["y"])/2
        bounds["by"]=(limits["bl"]["y"]+limits["br"]["y"])/2
        bounds["lx"]=(limits["tl"]["x"]+limits["bl"]["x"])/2
        bounds["rx"]=(limits["tr"]["x"]+limits["br"]["x"])/2
    except KeyboardInterrupt:
        return

    def cameraCordtoGameCord(pt):
        x=pt[0]
        y=pt[1]
        pointsy = [(bounds["ty"],0),(bounds["by"],display_height)]
        x_coords, y_coords = zip(*pointsy)
        A = vstack([x_coords,ones(len(x_coords))]).T
        m, c = lstsq(A, y_coords)[0]
        outY=int(m*y+c)

        pointsx = [(bounds["lx"],0),(bounds["rx"],display_width)]
        x_coords, y_coords = zip(*pointsy)
        A = vstack([x_coords,ones(len(x_coords))]).T
        m, c = lstsq(A, y_coords)[0]
        outX=int(m*x+c)
        return (outX,outY)

    crashed = False
    objects = set()
    nukes=set()
    score=0
    while not crashed:
        newi = random.randint(0,200)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True

        if newi == 5 :
            objects.add(Item("pineapple.png"))
        elif newi == 8:
            objects.add(Item("shrooms.png"))
        elif newi == 9:
            objects.add(Item("tomato.png"))
        elif newi == 10:
            objects.add(Item("peppparooooooni.png"))
        elif newi == 11:
            objects.add(Item("bomb.png"))

        disp.fill((0, 0, 0))
        # disp.blit(cursor, (cursorx,cursory))
        # disp.blit(othercursor, (othercursorx,othercursory))
        text = font.render('Score: '+str(score), True, green, black)
        textRect = text.get_rect()
        textRect.center = (display_width // 2,display_height // 2)
        disp.blit(text,textRect)

        for item in objects:
                item.move()
                disp.blit(item.image, (item.x, item.y))
        removeItems = []
        for item in objects:
            if item.x - 100 > display_width or item.y > display_height:
                removeItems.append(item)
            elif item.isCollided(cursorx,cursory) or item.isCollided(othercursorx,othercursory):
                if item.isBomb:
                    score=-1
                score+=1
                removeItems.append(item)
        for item in removeItems:
            if (item.isCollided(cursorx,cursory) or item.isCollided(othercursorx,othercursory)) and item.isBomb:
                nukes.add(Explosion(item.x, item.y))
            objects.remove(item)

        removeItems = []
        for item in nukes:
            if item.decreaseSize():
                removeItems.append(item)
            disp.blit(item.image, (item.x, item.y))

        for item in removeItems:
            nukes.remove(item)

        if not xyq.empty():
            # avgx, avgy=0,0
            # count=0
            # while not xyq.empty():
            #     val=xyq.get()
            #     avgx+=val[0]
            #     avgy+=val[1]
            #     count+=1
            # avgx=int(avgx/count)
            # avgy=int(avgy/count)
            # # avgx=int((avgx+cursorx)/2)
            # # avgy=int((avgy+cursory)/2)
            # cursorx,cursory=avgx,avgy
            newCord=cameraCordtoGameCord(xyq.get())
            if (math.pow((cursorx-newCord[0]),2) + math.pow((cursory-newCord[1]),2))>1600:
                cursorx=newCord[0]
                cursory=newCord[1]
            # print("----")
            # print(newCord)
            # print(cursorx,cursory)
            # print(count)

        if not otherxyq.empty():
            newCord=cameraCordtoGameCord(otherxyq.get())
            if (math.pow((othercursorx-newCord[0]),2) + math.pow((othercursory-newCord[1]),2))>1600:
                othercursorx=newCord[0]
                othercursory=newCord[1]
            print("----")
            print(newCord)
            print(othercursorx,othercursory)
        pygame.display.update()
        clock.tick(60)
    pygame.quit()
    return

def video(xyq, otherxyq):
    prevTime=time.time()
    cap = cv2.VideoCapture(1)
    cap.set(3,1280);
    cap.set(4,720);
    try:
        while True:
            # print("-----------")
            # print(time.time()-prevTime)
            # prevTime=time.time()
            # frame=frameQueue.get()
            _, frame = cap.read()
            frame = cv2.flip(frame,1)
            median = cv2.medianBlur(frame,1)
            hsv = cv2.cvtColor(median, cv2.COLOR_BGR2HSV)

            # blur = cv2.GaussianBlur(hsv,(5,5), 100000)
            # lower = np.array([140, 10, 50])
            # upper = np.array([179,255,200])
            lower = np.array([145, 80, 30])
            upper = np.array([179,255,255])
            # mask = cv2.inRange(blur,lower, upper)
            otherMask = cv2.inRange(hsv,lower, upper)
            lower = np.array([0, 80, 30])
            upper = np.array([8,255,140])
            newMask = cv2.inRange(hsv,lower, upper)
            otherNewMask = otherMask | newMask
            kernel = np.ones((5, 5), np.uint8)
            # dilate = cv2.dilate(otherMask,kernel,iterations = 1)
            opening = cv2.morphologyEx(otherNewMask, cv2.MORPH_OPEN, kernel)

            # cv2.medianBlur(otherMask, 3)
            # blurMask=cv2.GaussianBlur(otherMask,(45,45), 100000)


            contours, _ = cv2.findContours(opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) !=0:
                cv2.drawContours(frame, contours, -1, (255, 0, 0), 3)
                c = max(contours, key = cv2.contourArea)
                area = cv2.contourArea(c)
                if area>1000:
                    # print(c)
                    x,y,w,h = cv2.boundingRect(c)
                    # draw the book contour (in green)
                    cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                    # print(x,y)
                    xyq.put((x,y))
                    contours=[contour for contour in contours if cv2.contourArea(contour)!=cv2.contourArea(c)]
                    if len(contours) != 0:
                        c2 = max(contours, key = cv2.contourArea)
                        if cv2.contourArea(c2)>1000:
                            x,y,w,h = cv2.boundingRect(c2)
                            # draw the book contour (in green)
                            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                            # print(x,y)
                            otherxyq.put((x,y))
            # cv2.imshow('opening', opening)
            # cv2.imshow('erosion', erosion)
            # cv2.imshow('blur',blur)
            # cv2.imshow('mask',mask)
            # cv2.imshow('blurMask',blurMask)
            # cv2.imshow('median',median)
            # cv2.imshow('newMask',newMask)
            # cv2.imshow('otherNewMask',otherNewMask)
            # cv2.imshow('otherMask',otherMask)
            # cv2.imshow ("Frame", frame)

            # c = cv2.waitKey(7) % 0x100
            # if c == 27 or c == 10:
            #     break

    except KeyboardInterrupt:
        pass
    cap.release()
    cv2.destroyAllWindows()
    return

def getFrames(frameQueue):
    cap = cv2.VideoCapture(1)
    cap.set(3,1280);
    cap.set(4,720);
    try:
        while True:
            time.sleep(0.01)
            _, frame = cap.read()
            if frameQueue.qsize()<3:
                frameQueue.put(frame)
    except KeyboardInterrupt:
        pass

    cap.release()
    return

def startFruitNinja():
    xyq=Queue()
    otherxyq=Queue()
    Process(target = game, args=(xyq,otherxyq,)).start()
    # Process(target = getFrames, args=(frameQueue,)).start()
    Process(target = video, args=(xyq,otherxyq,)).start()

if __name__=="__main__":
    startFruitNinja()
# video()
