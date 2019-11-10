#random Imports
from tkinter import *
import sys
import time
import requests
import json
from datetime import datetime
# from PIL import ImageTk, Image
import threading, _thread
import cv2
import asyncio, io, glob, os, uuid
from urllib.parse import urlparse
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, SnapshotObjectType, OperationStatusType
import combo, emotiongame
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient
from msrest.authentication import CognitiveServicesCredentials

sayings = {
    'disgust' : "Are you okay?\nYou don't seem very please",
    'anger' : "You seem angry? Do you want to talk about it?",
    'happiness' : "You're looking happy today.\nWhat happened?",
    'sadness' : "You look so sad :(\nWhat's going on?",
    'surprise' : "Ooh, surprise surprise, what happened?",
    'neutral' : "How are you feeling today?"#Show some emotion"
}



#Three global variables
recognized = False
message = "Log in with face"
emotionData = None
emotionVal = ""
personVal = ""
message2 = ""

emotions = {}
def set_emotion(emotion):
    global emotions, emotionVal
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
    emotionVal = val

    return sayings[val]


#Connecting to Azure
key = "f4213b760a1e447c84cfaaa8703ad82a"
endpoint = "https://centralus.api.cognitive.microsoft.com/"
face_client = FaceClient(endpoint, CognitiveServicesCredentials(key))
speech_key, service_region = "23c5f1b4958942b889c263fb8baee340", "centralus"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
subscription_key ="72974b51685d4b6d93d91a38de4d0361"

def authenticateClient():
    credentials = CognitiveServicesCredentials(subscription_key)
    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint, credentials=credentials)
    return text_analytics_client

#function to check if person in image
def test_image():
    #declare global message variable
    global message, emotionData, message2, personVal
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
                    personVal = 'Vineet'
                    return True
                elif person.candidates[0].person_id == "dbde91bc-673d-4c03-9c03-8fb2072478ce":
                    message = 'Welcome Sam'
                    personVal = 'Sam'
                    return True
                elif person.candidates[0].person_id == "472c66f3-9508-47d1-bec3-33dea996b5e7":
                    message = 'Welcome David'
                    personVal = 'David'
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
    cap = cv2.VideoCapture(1)
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

def open_fruit_ninja(event):
    # if event.char == 'q':
    print("Starting Fruit Ninja")
    combo.startFruitNinja()

def open_emotion_game(event):
    # if event.char == 'q':
    print("Starting Fruit Ninja")
    emotiongame.startGame()

if __name__ == "__main__":
    KEYWORDS = {
        "mirror pizza ninja" : combo.startFruitNinja,
        "mirror emotion game" : emotiongame.startGame
    }
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
    # score = Label(left,font=("times", 50, "bold"), bg="black", fg="white", text="High Score:\n0")
    # score.pack(anchor=E)
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
    print("hifvojk")
    #Tick clock
    tick()

    #Start thread to detect face and update login message
    


    m.bind('q', open_fruit_ninja)
    m.bind('w', open_emotion_game)
    num = Label(mid, font=("times", 30, "bold"), bg="black", fg="white", text="Recognizing speech")
    num.config(anchor=CENTER)
    num.pack()
    m.update_idletasks()
    m.update()
    find_face()
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    def recognizeSpeech():
        result = speech_recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(result.text))
            client = authenticateClient()
            try:
                documents = [
                    {"id": "1", "language": "en", "text": result.text},
                ]

                response = client.sentiment(documents=documents)
                for document in response.documents:
                    print("Document Id: ", document.id, ", Sentiment Score: ",
                        "{:.2f}".format(document.score))
                    emotionFile = open('emotions.csv', 'a+')
                    emotionFile.write("\n{},{},{},{:.2f}".format(datetime.now(),personVal, emotionVal, document.score))
                    emotionFile.close()

            except Exception as error:
                print("Encountered exception. {}".format(error))
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized")
        elif result.reason == speechsdk.ResultReason.Canceled:
            print("Speech Recognition canceled")

    # threading.Thread(target=recognizeSpeech).start()
    def listen():
        recognizeSpeech()
        while True:
            try:
                result = speech_recognizer.recognize_once()
                print(result.text)
                if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    print("Recognized: {}".format(result.text))
                    # client = authenticateClient()
                    try:
                        for keyword in KEYWORDS.keys():
                            if keyword in result.text.lower():
                                print(f"KEYWORD FOUND {keyword}")
                                KEYWORDS[keyword]()
                    except Exception as err:
                        print("Encountered exception. {}".format(err))
                print("BBBBBBBBBBBBBBBBBBB")
                # time.sleep(0.2)
            except:
                raise




    threading.Thread(target=listen).start()
    

    num.destroy()

    m.mainloop()
