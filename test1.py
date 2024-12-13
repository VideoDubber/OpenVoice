
import os
import torch
import html
from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from melo.api import TTS
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
from google.cloud import texttospeech
import shutil
import os
import sys
import uuid
import json
import subprocess
from time import sleep
os.environ['TOKENIZERS_PARALLELISM'] = "false"
default_english_text=""
texts_={"bengali":'''নতুন দিনের আলোয়, কলাবাগান এলাকার ড. বিনয় বসু, যিনি কলকাতা বিশ্ববিদ্যালয়ের একজন প্রখ্যাত ভাষাবিজ্ঞানী, বাংলা ভাষার বিভিন্ন ধ্বনিভেদ নির্ধারণের জন্য একটি মিশনে বের হলেন। তার সঙ্গে ছিল তার সহকারী, মীনাক্ষী সেনগুপ্ত। তারা কলকাতার বিভিন্ন অঞ্চল ঘুরে দেখলেন, প্রতিটি এলাকার স্বতন্ত্র উচ্চারণ এবং উপভাষার বৈচিত্র্য তুলে ধরতে।

তাদের যাত্রা শুরু হলো উত্তর কলকাতার শ্যামবাজার থেকে, যেখানে তারা বৈষ্ণব সম্প্রদায়ের একজন প্রাচীন ব্যক্তিত্ব, কেশব ভট্টাচার্যের সাথে সাক্ষাৎ করলেন। তিনি তাদের ‘কৃষ্ণ’ এবং ‘রাধা’ শব্দের সূক্ষ্ম ধ্বনিগত পরিবর্তনগুলি সম্পর্কে জানালেন। এরপর তারা গেলেন সল্টলেকের দিকে, যেখানে মৈত্রী চক্রবর্তী, একজন স্কুলশিক্ষিকা, তাদের ছাত্রছাত্রীদের উচ্চারণের প্রভাবের কথা জানালেন, বিশেষত ‘বই’ এবং ‘গান’ শব্দগুলিতে।

পরবর্তীতে তারা গেলেন দক্ষিণ কলকাতার গড়িয়াহাটে, যেখানে তারা জাদবপুর বিশ্ববিদ্যালয়ের একজন বিশিষ্ট অধ্যাপক, ড. সুকান্ত সেনের লেকচার শুনলেন। তিনি গ্রেট ভাওয়েল শিফট সম্পর্কে আলোকপাত করলেন এবং দেখালেন কিভাবে ‘আম’ এবং ‘আকাশ’ শব্দগুলির ধ্বনিগত বিবর্তন সমাজের পরিবর্তনের সঙ্গে মিলেছে।

দমদমের দিকে গিয়ে, তারা অর্ণব বিশ্বাসের সাথে দেখা করলেন, যিনি একজন কবি এবং তার বাচিক উচ্চারণের রোমান্স ফুটিয়ে তোলেন। অর্ণবের ‘নীল’ এবং ‘ব্রীজ’ শব্দগুলির বিশেষ উচ্চারণ তাদের ভাষার সমৃদ্ধ সাংস্কৃতিক বৈচিত্র্যের প্রতিফলন করে।

'''}

datadic = {
    'clone_EN-NEWEST': ['EN_NEWEST', 'EN-Newest', 0], #language, speaker_id, speaker_value
    'clone_EN-US': ['EN', 'EN-US', 0],
    'clone_EN-BR': ['EN', 'EN-BR', 1],
    'clone_EN-INDIA': ['EN', 'EN_INDIA', 2],
    'clone_EN-AU': ['EN', 'EN-AU', 3],
    'clone_EN-DEFAULT': ['EN', 'EN-Default', 4],
    'clone_ES': ['ES', 'ES', 0],
    'clone_FR': ['FR', 'FR', 0],
    'clone_ZH': ['ZH', 'ZH', 1],
    'clone_JP': ['JP', 'JP', 0],
    'clone_KR': ['KR', 'KR', 0]
}

ckpt_converter = 'checkpoints_v2/converter'
device = "cuda:0" if torch.cuda.is_available() else "cpu"


tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

#transfer folder, transfer need.txt, from awsapi
#transfer results after done, transfer done.txt, delete local, from awsgpu
#refs are in final_cut/speakerid.mp3 --> uuid/speakerid/ref.mp3
#tests are to be written to speakerid/1.txt 2.txt based on final file name w

def convert_color(projectfolder: str) -> list:
 
    ref_audio_path=f"./vocals.mp3"

    target_se, audio_name = se_extractor.get_se(ref_audio_path, tone_color_converter, vad=False)
    source_se, audio_name = se_extractor.get_se(f"./final_audio_nonmixed.mp3", tone_color_converter, vad=False)
    save_path = './tf.mp3'
    #source_se, audio_name = se_extractor.get_se(save_path, tone_color_converter, vad=True)

    # Run the tone color converter
    encode_message = "@VideoDubber.ai"
    tone_color_converter.convert(
            audio_src_path="./final_audio_nonmixed.mp3", 
            src_se=source_se, 
            tgt_se=target_se, 
            output_path=save_path,
            message=encode_message)

convert_color("")


