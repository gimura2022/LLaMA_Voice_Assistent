import stt
import tts
import os
import logging
import googletrans
import yaml
from yaml.loader import SafeLoader
from fuzzywuzzy import fuzz
from num2words import num2words
from functools import lru_cache
from datetime import datetime

loger = logging.getLogger("MAIN")
date = datetime.now()
loger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, format='[%(name)s/%(asctime)s/%(levelname)s] %(message)s')

with open("settings.yml", encoding="UTF-8") as file:
    settings = yaml.load(file, Loader=SafeLoader)

translator = googletrans.Translator()
called = False

def convert_num(string: str):
    string_nums = []

    num = ""
    num_ = False

    for i in string:
        if i.isnumeric():
            num_ = True
            num += i

        else:
            if num_:
                string_nums.append(num)
                num_ = False
            
            num = ""

    string_nums_set = list(set(string_nums))
    string_nums_converted = [num2words(i, lang=settings["lang"]) for i in string_nums_set]

    for i in range(len(string_nums_set)):
        string = string.replace(string_nums_set[i], string_nums_converted[i])

    return string

@lru_cache()
def gen():
    loger.info("text generation...")
    os.system("gen.bat")
    loger.info("text generation done!")

loger.info("LLaMA assistent init complected!")

def main(text):
    global called

    if fuzz.ratio(text, settings["activation"]["activation_phrase"]) >= settings["activation"]["percentage_match_for_activation"]:
        tts.play(settings["activation"]["response_phrase"])
        called = True

    elif called and text != "":
        loger.info("request translation...")
        en_text = translator.translate(text, src=settings["lang"]).text
        loger.info("request translation done!")

        with open("input.txt", "w", encoding="UTF-8") as file:
            file.write(en_text)

        gen()
        loger.info(f"cache info:\nhits-{gen.cache_info().hits}\nmisses-{gen.cache_info().misses}\nmaxsize-{gen.cache_info().maxsize}\ncurrsize-{gen.cache_info().currsize}")

        with open("output.txt", encoding="UTF-8") as file:
            answer_text = file.read()

        loger.info("translation answer...")
        lang_text = translator.translate(answer_text, dest=settings["lang"], src="en").text
        loger.info("translation answer done!")

        loger.info("convertion nums...")
        num_convert_text = convert_num(lang_text)
        loger.info("convertion nums done!")

        tts.play(num_convert_text)

        called = False

stt.start_audio_stream(main)