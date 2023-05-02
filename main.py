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

loger.info("loading settings...")
with open("settings.yml", encoding="UTF-8") as file:
    settings = yaml.load(file, Loader=SafeLoader)
loger.info("loading settings done!")

loger.info("loading commands...")
with open("commands.yml", encoding="UTF-8") as file:
    commands = yaml.load(file, Loader=SafeLoader)
loger.info("loading commands done!")

translator = googletrans.Translator()
called = False
histry = []

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

def read_command_file(cmd):
    with open(f"commands\\{cmd}", encoding="UTF-8") as file:
        cmd_yaml = yaml.load(file.read(), Loader=SafeLoader)

    return cmd_yaml

def get_command(text: str):
    proc = [fuzz.WRatio(text, read_command_file(command)["activation_phrase"]) for command in commands]

    most_likely_command_index = proc.index(max(proc))
    if proc[most_likely_command_index] < 80:
        return "other.yml"
    
    return commands[most_likely_command_index]

@lru_cache()
def gen_(): 
    loger.info("text generation...")
    os.system("gen.bat")
    loger.info("text generation done!")

def gen(text):
    histry.append(text)

    if len(histry) > settings["experimental"]["history_memorization_size"]:
        histry.pop(0)
    
    if settings["experimental"]["history_memorization"]:
        with open("input.txt", "w", encoding="UTF-8") as file:
            file.write("\n".join(histry))
    
    else:
        with open("input.txt", "w", encoding="UTF-8") as file:
            file.write(text)

    gen_()

loger.info("LLaMA assistent init complected!")

def main(text):
    global called

    command = get_command(text)
    command_yml = read_command_file(command)

    if command_yml["type"] != "none":
        loger.info(f"command found: {command}")

    if fuzz.ratio(text, settings["activation"]["activation_phrase"]) >= settings["activation"]["percentage_match_for_activation"]:
        tts.play(settings["activation"]["response_phrase"])
        called = True

    elif called and text != "" and command_yml["type"] == "other":
        loger.info("request translation...")
        en_text = translator.translate(text, src=settings["lang"]).text
        loger.info("request translation done!")

        gen(en_text)
        loger.info(f"cache info:\nhits-{gen_.cache_info().hits}\nmisses-{gen_.cache_info().misses}\nmaxsize-{gen_.cache_info().maxsize}\ncurrsize-{gen_.cache_info().currsize}")

        try:
            with open("output.txt", encoding="UTF-8") as file:
                answer_text = file.read()

        except:
            with open("output.txt", "w", encoding="UTF-8") as file:
                ...

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

    elif command_yml["type"] == "run":
        loger.info(f"start command: {command_yml['command']}")
        os.system(command_yml["command"])

        tts.play(command_yml["answer"])

stt.start_audio_stream(main)