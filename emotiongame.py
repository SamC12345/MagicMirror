import pygame, sys
from pygame.locals import *
import random
import time
import cv2
import sys, uuid, requests
from urllib.parse import urlparse
from io import BytesIO
# from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
import asyncio, io, glob, os
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, SnapshotObjectType, OperationStatusType


#Connecting to Azure
key = "f4213b760a1e447c84cfaaa8703ad82a"
endpoint = "https://centralus.api.cognitive.microsoft.com/"
face_client = FaceClient(endpoint, CognitiveServicesCredentials(key))

EMOTIONS = {
'anger',
'contempt',
'disgust',
'fear',
'happiness',
'neutral',
'sadness',
'surprise'
}

emotionDic = {}
# def set_emotion(emotion):
#     global emotionDic
#     emotionDic['anger'] = emotion.anger
#     emotionDic['contempt'] = emotion.contempt
#     emotionDic['disgust'] = emotion.disgust
#     emotionDic['fear'] = emotion.fear
#     emotionDic['happiness'] = emotion.happiness
#     emotionDic['neutral'] = emotion.neutral
#     emotionDic['sadness'] = emotion.sadness
#     emotionDic['surprise'] = emotion.surprise
#
# def get_emotion(emotion, obj):
#     if emotion == "happiness":
#         return obj.face_attributes.emotion.happiness
#     elif emotion == "anger":
#         return obj.face_attributes.emotion.anger
#     elif emotion == "contempt":
#         return obj.face_attributes.emotion.contempt
#     elif emotion == "disgust":
#         return obj.face_attributes.emotion.disgust
#     elif emotion == "fear":
#         return obj.face_attributes.emotion.fear
#     elif emotion == "neutral":
#         return obj.face_attributes.emotion.neutral
#     elif emotion == "sadness":
#         return obj.face_attributes.emotion.sadness
#     elif emotion == "surprise":
#         return obj.face_attributes.emotion.surprise


def getHigher(emotionStr):
    global emotionDic
    group_photo = 'emotion_img.jpg'
    IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    test_image_array = glob.glob(os.path.join(IMAGES_FOLDER, group_photo))
    image = open(test_image_array[0], 'r+b')

    PERSON_GROUP_ID = 'unique-group-id3'
    #Send faces to API
    prev = time.time()
    faces = face_client.face.detect_with_stream(image = image, return_face_attributes=['emotion'])

    maxi = 0

    get_emotion = lambda x: x.face_attributes.emotion

    for i in range(len(faces)):
        face = faces[i]
        emotionDic = {emotion : getattr(get_emotion(face), emotion) for emotion in EMOTIONS}
        print(i, emotionDic)

    emotion_scores = [getattr(get_emotion(face), emotionStr) for face in faces]

    if not emotion_scores:
        return -1

    max_index = max(range(len(emotion_scores)), key=lambda i: emotion_scores[i])
    print(max_index, emotion_scores)

    if emotion_scores[max_index] < 0.1:
        return -1
    # for i in range(len(faces)):
    #     face = faces[i]
    #     max_face = faces[maxi]
    #     # set_emotion(faces[i].face_attributes.emotion)
    #     if getattr(get_emotion(face), emotionStr) > getattr(get_emotion(max_face), emotionStr):
    #         maxi = i
    #     print(emotionDic)
    # if len(faces) > 1 and getattr(get_emotion(faces[0]), emotionStr) == getattr(get_emotion(faces[1]), emotionStr):
    #     return -1
    return max_index

def startGame():
    pygame.init()

    roundNum = 1
    # X = 3200
    # Y = 1800
    X = 1600
    Y = 900

    disp = pygame.display.set_mode((X, Y), pygame.FULLSCREEN)

    pointA = 0
    pointB = 0

    crashed = False
    clock = pygame.time.Clock()

    green = (0, 255, 0)
    blue = (0, 0, 128)
    white = (255, 255, 255)
    black = (0,0,0)
    font = pygame.font.Font('comic-sans.ttf', 32)

    emotions = ['anger', 'contempt', 'disgust', 'fear', 'happiness', 'sadness', 'neutral', 'surprise']
    random.shuffle(emotions)


    cap = cv2.VideoCapture(0)
    val = " "
    while not crashed:
        _, frame = cap.read()
        #Read faces
        timer = 0
        curr = emotions.pop()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    crashed = True
        round = font.render('Round ' + str(roundNum), True, white, black)
        roundRect = round.get_rect()
        roundRect.center = (X // 2, Y * 0.35)
        disp.blit(round, roundRect)

        emotion = font.render(curr, True, white, black)
        emotionRect = emotion.get_rect()
        emotionRect.center = (X // 2, Y * 0.4)
        disp.blit(emotion, emotionRect)

        ptA = font.render(str(pointA), True, white, black)
        ptARect = ptA.get_rect()
        ptARect.center = (X // 2 - 500, Y * 0.35)
        disp.blit(ptA, ptARect)

        ptB = font.render(str(pointB), True, white, black)
        ptBRect = ptB.get_rect()
        ptBRect.center = (X // 2 + 500, Y * 0.35)
        disp.blit(ptB, ptBRect)

        a = font.render('Prev: ' + str(val), True, white, black)
        aRect = a.get_rect()
        aRect.center = (X // 2, Y * 0.45)
        disp.blit(a, aRect)



        roundNum += 1
        while timer < 3:
            disp.fill(black)
            timer += 1
            timeV = font.render(str(4-timer), True, white, black)
            timeVRect = timeV.get_rect()
            timeVRect.center = (X // 2 , Y //2)

            disp.blit(timeV, timeVRect)
            disp.blit(round, roundRect)
            disp.blit(emotion, emotionRect)
            disp.blit(ptA, ptARect)
            disp.blit(ptB, ptBRect)
            disp.blit(a, aRect)
            time.sleep(1)
            pygame.display.update()
        print('\n\n'+curr)
        cv2.imwrite(filename='emotion_img.jpg', img=frame)
        val = getHigher(curr)
        print("val "+str(val))
        if val == 0:
            pointA += 1
        elif val == 1:
            pointB += 1

        disp.fill(black)
        if len(emotions) == 0:
            break
    time.sleep(2)
    disp.fill(black)
    victory_text = ("Player 1" if pointA > pointB else "Player 2") + " wins"
    if pointA == pointB:
        victory_text = "It's a tie!"
    a = font.render(victory_text, True, white, black)
    aRect = a.get_rect()
    aRect.center = (X // 2, Y * 0.45)
    disp.blit(a, aRect)
    pygame.display.update()
    time.sleep(2)
    pygame.quit()

if __name__ == "__main__":
    startGame()
