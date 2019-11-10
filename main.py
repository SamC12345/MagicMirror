#random Imports
from tkinter import *
import sys
import time
import requests
import json
from PIL import ImageTk, Image
import threading
import cv2
import asyncio, io, glob, os, uuid
from urllib.parse import urlparse
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, SnapshotObjectType, OperationStatusType


sayings = {
    'disgust' : 'You look disgusted.\nDon\'t be.',
    'anger' : "Life is beautiful. Don't be angry",
    'happiness' : "You're looking happy today.\nThat's great.\nLife is amazing",
    'sadness' : "Don't be so sad.\nBe glad!",
    'surprise' : "Surprise motherf*ker!",
    'neutral' : "Show some emotion"
}

#Three global variables 
recognized = False
message = "Log in with face"
emotionData = None

message2 = ""

emotions = {}
def set_emotion(emotion):
    global emotions
    emotions['anger'] = emotion.anger
    emotions['contempt'] = emotion.contempt
    emotions['disgust'] = emotion.disgust
    emotions['fear'] = emotion.fear
    emotions['happiness'] = emotion.happiness
    emotions['neutral'] = emotion.neutral
    emotions['sadness'] = emotion.sadness
    emotions['surprise'] = emotion.surprise
    val = max(emotions.items(), key = lambda x: x[1])[0]
    if val == 'contempt':
        val = 'anger'
    if val =='fear':
        val = 'surprise'

    return sayings[val]


#Connecting to Azure
key = "f4213b760a1e447c84cfaaa8703ad82a"
endpoint = "https://centralus.api.cognitive.microsoft.com/"
face_client = FaceClient(endpoint, CognitiveServicesCredentials(key))

#function to check if person in image
def test_image():
    #declare global message variable
    global message, emotionData, message2
    #Get image from file
    group_photo = 'saved_img.jpg'
    IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    test_image_array = glob.glob(os.path.join(IMAGES_FOLDER, group_photo))
    image = open(test_image_array[0], 'r+b')

        
    PERSON_GROUP_ID = 'unique-group-id3'
    #Send faces to API
    face_ids = []
    faces = face_client.face.detect_with_stream(image, return_face_attributes=['emotion'])
    for face in faces:
        message2 = set_emotion(face.face_attributes.emotion)
        print(message2)
        face_ids.append(face.face_id)
    if len(face_ids) > 0:
        results = face_client.face.identify(face_ids, PERSON_GROUP_ID)
        #Collect results
        if not results:
            print('No person identified in the person group for faces from the {}.'.format(os.path.basename(image.name)))
        for person in results:
            if len(person.candidates) > 0:
                #Change message based on who it detected
                if person.candidates[0].person_id == "6b3bd011-5a79-4d07-a8d9-9e0bf44be947":
                    message = 'Welcome Vineet'
                    return True
                elif person.candidates[0].person_id == "dbde91bc-673d-4c03-9c03-8fb2072478ce":
                    message = 'Welcome Sam'
                    return True
                elif person.candidates[0].person_id == "472c66f3-9508-47d1-bec3-33dea996b5e7":
                    message = 'Welcome David'
                    return True

            else:
                message = 'Person not recognized'
                print("Person can't be identified")
            log.config(text=message)
    return False

#Function to find face
def find_face():
    #Create global variable log: Label on screen
    global recognized, log, log2
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    print(recognized)
    while not recognized:
        _, frame = cap.read()
        #Read faces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        key = cv2.waitKey(1)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) > 0:
            #If found face try and recognize face
            # Write picture to file
            cv2.imwrite(filename='saved_img.jpg', img=frame)
            recognized = test_image()
            # If face couldnt be recognized, sleep for three seconds so API calls not maxed out
            if not recognized:
                time.sleep(3)
        # Code for bounding boxes on faces
        # for (x, y, w, h) in faces:
        #     cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        if key == 27:
            break
    # Change logging message on screen through global var
    log.config(text=message)
    log2.config(text=message2)
    # Release carmera vars
    cap.release()
    cv2.destroyAllWindows()




#Main code to display UI
url = "https://api.darksky.net/forecast/cccddf3bdea1714ab4fb33a10653811f/40.7357,-74.1724"
response = requests.get(url)
val = response.json()['currently']
def close(event):
    m.destroy()

#Update clock
time_string = ""
def tick():
    time_string=time.strftime("%I:%M")
    clock.config(text=time_string)
    clock.after(200,tick)

#Create root
m = Tk()
m.attributes("-fullscreen", True)
m.configure(background='black')
m.bind('<Escape>', close)

#Make left and right frame
mid = Frame(m)
mid.pack()
mid.config(background='black')
left = Frame(m)
left.pack(side=LEFT)
right = Frame(m)
right.pack(side=RIGHT)

#Clock label
clock=Label(mid, font=("times", 80, "bold"), bg="black", fg="white")
clock.config(anchor=CENTER)
clock.pack()
right.config(background='black')

#Show face to log in
log = Label(mid, font=("times", 30, "bold"), bg="black", fg="white", text=message)
log.config(anchor=CENTER)
log.pack()

log2 = Label(mid, font=("times", 30, "bold"), bg="black", fg="white", text=message2)
log2.config(anchor=CENTER)
log2.pack()

#Score Label
score = Label(left,font=("times", 50, "bold"), bg="black", fg="white", text="High Score:\n0")
score.pack(anchor=E)
#Weather stuff
# image = ImageTk.PhotoImage(Image.open("{}.png".format(val['icon'])))
# canvas = Canvas(right, width = 300, height = 300) 
# canvas.pack()
# canvas.create_image(1,1,anchor=NW,  image=image)   
# Label to display temperature
temperature = Label(right, font=("times", 50, 'bold'), bg='black', fg='white', text=val['summary'])
temperature.pack()
temperature2 = Label(right, font=("times", 30, 'bold'), bg='black', fg='white', text="{0:.0f}°".format(val['temperature']))
temperature2.pack()

myvar=Label(m, text = time_string, compound = CENTER)

myvar.place(x=0, y=0)
print("hi")
#Tick clock
tick()

#Start thread to detect face and update login message
t1 = threading.Thread(target=find_face)
t1.start()

m.mainloop()

