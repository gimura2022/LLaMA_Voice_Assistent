import torch
import sounddevice as sd
import time
import logging
import yaml
from yaml.loader import SafeLoader

loger = logging.getLogger("TTS")
loger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, format='[%(name)s/%(asctime)s/%(levelname)s] %(message)s')

with open("settings.yml", encoding="UTF-8") as file:
    settings = yaml.load(file, Loader=SafeLoader)

language = settings["lang"]
model_id = 'ru_v3'
sample_rate = 48000
speaker = settings["tts"]["selero_speaker"]
put_accent = True
put_yo = True
device = torch.device(settings["tts"]["selero_device"])

model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models', model='silero_tts', language=language, speaker=model_id)
model.to(device)

loger.info("tts init complected!")

def play(text):
    if text == "":
        return
    
    loger.info(f"play: {text}")

    audio = model.apply_tts(text=f"{text}..", speaker=speaker, sample_rate=sample_rate, put_accent=put_accent, put_yo=put_yo)

    sd.play(audio, sample_rate * 1.05)
    time.sleep((len(audio) / sample_rate) + 0.5)
    sd.stop()