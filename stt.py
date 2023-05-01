import vosk
import sys
import sounddevice as sd
import queue
import json
import logging
import yaml
from yaml.loader import SafeLoader

loger = logging.getLogger("STT")
loger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, format='[%(name)s/%(asctime)s/%(levelname)s] %(message)s')

vosk.SetLogLevel(-1)

with open("settings.yml", encoding="UTF-8") as file:
    settings = yaml.load(file, Loader=SafeLoader)

model = vosk.Model(settings["stt"]["vosk_model_path"])
samplerate = 16000
device = settings["stt"]["audio_device"]

q = queue.Queue()

loger.info("stt init complected!")

def callback_(indata, frames, time, status):
    q.put(bytes(indata))

def start_audio_stream(callback):
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device, dtype='int16', channels=1, callback=callback_):
        rec = vosk.KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                text = json.loads(rec.Result())["text"]

                if text != "":
                    loger.info(f"row text: {text}")

                callback(text)