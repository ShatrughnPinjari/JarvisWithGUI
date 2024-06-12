try:
    # importing prebuilt modules
    import webbrowser
    import threading
    import os
    import logging
    import pyttsx3
    import pyautogui
    import pywhatkit
    from datetime import datetime
    import re
    from PyQt5 import QtWidgets, QtCore, QtGui, uic
    from PyQt5.QtCore import QTimer, QTime, QDate, Qt, pyqtSignal, QThread
    from PyQt5.QtGui import QMovie , QTextCharFormat, QBrush, QColor   
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5.uic import loadUiType
    from threading import Thread
    logging.disable(logging.WARNING)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # disabling warnings for gpu requirements
    import time
    from keras_preprocessing.sequence import pad_sequences
    import numpy as np
    from keras.models import load_model
    from pickle import load
    import speech_recognition as sr
    import sys
    #sys.path.insert(0, os.path.expanduser('~') + "/PycharmProjects/Virtual_Voice_Assistant")
    sys.path.insert(0, os.path.expanduser('~')+"/JARVIS- Personal Voice Assistant") # adding voice assistant directory to system path
    # importing modules made for assistant
    from database import *
    from image_generation import generate_image
    from gmail import *
    from API_functionalities import *
    from system_operations import *
    from browser import *
    from gui import Ui_MainWindow
   
except (ImportError, SystemError, Exception, KeyboardInterrupt) as e:
    print("ERROR OCCURRED WHILE IMPORTING THE MODULES")
    exit(0)

recognizer = sr.Recognizer()

engine = pyttsx3.init()

voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)

sys_ops = SystemTasks()
tab_ops = TabOpt()
win_ops = WindowOpt()

# load trained model
model = load_model('..\\Data\\chat_model')

# load tokenizer object
with open('..\\Data\\tokenizer.pickle', 'rb') as handle:
    tokenizer = load(handle)

# load label encoder object
with open('..\\Data\\label_encoder.pickle', 'rb') as enc:
    lbl_encoder = load(enc)
    

def speak(text):
    print("ASSISTANT -> " + text)
    try:
        engine.say(text)
        engine.runAndWait()
    except KeyboardInterrupt or RuntimeError:
        return

def chat(text):
    # parameters
    max_len = 20
    while True:
        result = model.predict(pad_sequences(tokenizer.texts_to_sequences([text]),
                                                                          truncating='post', maxlen=max_len), verbose=False)
        intent = lbl_encoder.inverse_transform([np.argmax(result)])[0]
        return intent

class TextStream(QtCore.QObject):
    newText = QtCore.pyqtSignal(str)

    def write(self, text):
        self.newText.emit(text) 
        
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.startTask)
        self.ui.pushButton_2.clicked.connect(self.exit_program)
        self.text_stream = TextStream(self.ui.textBrowser_3)
        sys.stdout = self.text_stream
        self.text_stream.newText.connect(self.appendText)
        
        # Add the following lines to set the text color for textBrowser, textBrowser_2, and textBrowser_3
        text_format = QTextCharFormat()
        text_format.setForeground(QBrush(QColor(QtCore.Qt.white)))
        self.ui.textBrowser.setCurrentCharFormat(text_format)
        self.ui.textBrowser_2.setCurrentCharFormat(text_format)
        self.ui.textBrowser_3.setCurrentCharFormat(text_format)
        
        self.listening_thread = None
        self.main_thread = None
    def __del__(self):
        sys.stdout = sys.__stdout__
    
    def appendText(self, text):
        self.ui.textBrowser_3.append(text)
    
    def startTask(self):
        self.ui.movie = QMovie("D:\\Full_Jarvis\\Backend\\Plugins\\utils\\images\\live_wallpaper.gif")
        self.ui.label.setMovie(self.ui.movie)
        self.ui.movie.start()
        self.ui.movie = QMovie("D:\\Full_Jarvis\\Backend\\Plugins\\utils\\images\\initiating.gif")
        self.ui.label_2.setMovie(self.ui.movie)
        self.ui.movie.start()
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)
        # startExecution.start()
        self.start_listening()
        self.startup("initial text for query")
    
    def startup(self, query):
        speak("Initializing Jarvis")
        speak("Starting all systems applications")
        speak("Installing and checking all drivers")
        speak("Calibrating and examining all the core processors")
        speak("Checking the internet connection")
        speak("Wait a moment sir")
        speak("All drivers are up and running")
        speak("All systems have been activated")
        speak("Now I am online")
        speak("I am Jarvis. Online and ready sir. Please tell me how may I help you")
        
    def start_listening(self):
        if self.listening_thread is None or not self.listening_thread.is_alive():
            self.listening_thread = Thread(target=self.listen_audio)
            self.listening_thread.start()
        
    def exit_program(self):
        self.close()
    
 
    def showTime(self):
        current_time = QTime.currentTime().toString('hh:mm:ss')
        current_date = QDate.currentDate().toString(Qt.ISODate)
        self.ui.textBrowser.setText(current_date)
        self.ui.textBrowser_2.setText(current_time)
        
    def listen_audio(self):
        try:
            while True:
                print("listening")
                response = record()
                if response is None:
                    continue
                else:
                    main(response)
        except KeyboardInterrupt:
            return
  


def record():
    with sr.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic)
        recognizer.dynamic_energy_threshold = True
        audio = recognizer.listen(mic, 5000)       
        try:
            text = recognizer.recognize_google(audio, language='us-in').lower()
        except:
            return None
    print("USER -> " + text)
    return text



def main(query):
        add_data(query)
        intent = chat(query)
        done = False 
        if ("google" in query and "search" in query) or ("google" in query and "how to" in query) or "google" in query:
            googleSearch(query)
            return
        elif ("youtube" in query and "search" in query) or "play" in query or ("how to" in query and "youtube" in query):
            youtube(query)
            return
        elif "distance" in query or "map" in query:
            get_map(query)
            return
        if intent == "joke" and "joke" in query:
            joke = get_joke()
            if joke:
                speak(joke)
                done = True
        elif intent == "news" and "news" in query:
            news = get_news()
            if news:
                speak(news)
                done = True
        elif intent == "ip" and "ip" in query:
            ip = get_ip()
            if ip:
                speak(ip)
                done = True
        elif intent == "movies" and "movies" in query:
            speak("Some of the latest popular movies are as follows :")
            get_popular_movies()
            done = True                
        elif intent == "tv_series" and "tv series" in query:
            speak("Some of the latest popular tv series are as follows :")
            get_popular_tvseries()
            done = True
        elif intent == "weather" and "weather" in query:
            city = re.search(r"(in|of|for) ([a-zA-Z]*)", query)
            if city:
                city = city[2]
                weather = get_weather(city)
                speak(weather)
            else:
                weather = get_weather()
                speak(weather)
            done = True
        elif intent == "internet_speedtest" and "internet" in query:
            speak("Getting your internet speed, this may take some time")
            speed = get_speedtest()
            if speed:
                speak(speed)
                done = True
        elif intent == "system_stats" and "stats" in query:
            stats = system_stats()
            speak(stats)
            done = True
     
        elif intent == "image_generation" and "image" in query:
            speak("what kind of image you want to generate?")
            text = record()
            speak("Generating image please wait..")
            generate_image(text)
            done = True
        elif intent == "system_info" and ("info" in query or "specs" in query or "information" in query):
            info = systemInfo()
            speak(info)
            done = True
        elif intent == "email" and "email" in query:
            speak("Type the Receiver Email-id : ")
            receiver_id = input()
            while not check_email(receiver_id):
                speak("Invalid email id\nType reciever id again : ")
                receiver_id = input()
            speak("Tell the subject of email")
            subject = record()
            speak("tell the body of email")
            body = record()
            success = send_email(receiver_id, subject, body)
            if success:
                speak('Email sent successfully')
            else:
                speak("Error occurred while sending email")
            done = True
        elif intent == "select_text" and "select" in query:
            sys_ops.select()
            done = True
        elif intent == "copy_text" and "copy" in query:
            sys_ops.copy()
            done = True
        elif intent == "paste_text" and "paste" in query:
            sys_ops.paste()
            done = True
        elif intent == "delete_text" and "delete" in query:
            sys_ops.delete()
            done = True
        elif intent == "new_file" and "new" in query:
            sys_ops.new_file()
            done = True
        elif intent == "switch_tab" and "switch" in query and "tab" in query:
            tab_ops.switchTab()
            done = True
        elif intent == "close_tab" and "close" in query and "tab" in query:
            tab_ops.closeTab()
            done = True
        elif intent == "new_tab" and "new" in query and "tab" in query:
            tab_ops.newTab()
            done = True
        elif intent == "close_window" and "close" in query:
            win_ops.closeWindow()
            done = True
        elif intent == "switch_window" and "switch" in query:
            win_ops.switchWindow()
            done = True
        elif intent == "minimize_window" and "minimize" in query:
            win_ops.minimizeWindow()
            done = True
        elif intent == "maximize_window" and "maximize" in query:
            win_ops.maximizeWindow()
            done = True
        elif intent == "screenshot" and "screenshot" in query:
            win_ops.Screen_Shot()
            done = True
        elif intent == "stopwatch":
            pass        
        elif intent == "wikipedia" and ("tell" in query or "about" in query):
            description = tell_me_about(query)
            if description:
                speak(description)
            else:
                googleSearch(query)
            done = True
        elif intent == "math":
            answer = get_general_response(query)
            if answer:
                speak(answer)
                done = True
        elif intent == "open_website":
            completed = open_specified_website(query)
            if completed:
                done = True
        elif intent == "open_app":
            completed = open_app(query)
            if completed:
                done = True
        elif intent == "note" and "note" in query:
            speak("what would you like to take down?")
            note = record()
            take_note(note)
            done = True
        elif intent == "get_data" and "history" in query:
            get_data()
            done = True
        elif intent == "exit" and ("exit" in query or "terminate" in query or "quit" in query):
            exit(0)
        
        if not done:
            answer = get_general_response(query)
            if answer:
                speak(answer)
            else:
                speak("Sorry, not able to answer your query")
        return


if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        jarvis = MainWindow()
        jarvis.show()
        sys.exit(app.exec_())
    except Exception as e:
        print("EXITED", e)