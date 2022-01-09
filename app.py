
# TEST NEW BRANCH 
# Importing the libraries

from __future__ import print_function
from flask import Flask, jsonify, request
import json
import urllib.request
from urllib.request import Request, urlopen
from numpy.lib.function_base import delete
import requests
import bs4 as bs4
import requests
#import pandas as pd
#import numpy as np
import youtube_dl
from flask import send_file, send_from_directory, safe_join, abort
from pydub import AudioSegment
from pydub.silence import split_on_silence
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, VideoUnavailable, TooManyRequests
from pathlib import Path
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.editor import *
from flask import send_file, send_from_directory, safe_join, abort
import os
from google.cloud import storage
from threading import Thread


# Declearing that the app is using Flask
app = Flask(__name__)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google-credentials.json'
#CHANGED THE VARIABLE

  
@app.route('/')
def home():
    return "We are onlinee"

@app.route('/get_image')
def get_image():
    filename = "martin.jpeg"
    return send_file(filename, mimetype='image/jpeg')



# IMPORTANT This function gets the url of the video from java via a HTTP request with POST method
@app.route('/download', methods=['POST'])  #sending a post request to '/' the function getdata is called
def getdata():
    print("The header is: ")
    print(request.headers)  #this is just to see the details of the request
    print("The json is: ")
    print(request.get_json())  #the request is sent through json format where the link is stored
    url = json.dumps(request.get_json()).split('"')[3]

    video_id = url.split("v=")[1]
    srt = retrieve_transcripts_youtube(video_id)
    print(srt)
    thread_a = VideoMaking(request.__copy__())
    thread_a.start()
    # heavy_process = Process( target=make_the_video(srt), daemon=True)
    # heavy_process.start()

    #transcript_analysis(srt)
    #file_path = "/Users/francescocenciarelli/Desktop/University/Year3/Programming3 /Microservice/finals.mp4"

    #upload_to_bucket('finals.mp4', file_path, "data_bucket_video_swag" )

    # video_downloader("https://www.youtube.com/watch?v=ukNvLsGvdC4")

    #fulltext = transcript_analysis_from_sentence(srt)

    return request.data
    #after the following functions can be used to do everything we need
    # video_downloader("https://www.youtube.com/watch?v=ukNvLsGvdC4")
    # audio_downloader("https://www.youtube.com/watch?v=ukNvLsGvdC4)


def send_done_confirmation(url, videoid):
    headers = {'Content-type': 'text/html; charset=UTF-8'}
    response = requests.post(url, data=videoid, headers=headers)




class VideoMaking(Thread):
    def __init__(self, request):
        Thread.__init__(self)
        self.request = request

    def run(self):
        url = json.dumps(self.request.get_json()).split('"')[3]
        video_id = url.split("v=")[1]
        print(video_id)
        srt = retrieve_transcripts_youtube(video_id)
        print(srt)

        # test temporary.....
        #srt = [{'text': 'this is where you come and punish', 'start': 0.0, 'duration': 3.99}]
        # -------------------

        make_the_video(srt, video_id)
        #url = heroku link to the java app when we will have it
        #send_done_confirmation(url, videoid)


#function to get the transcript from yotube taking in the youtube id (letters and numbers after watch?v= in the youtube link)
def retrieve_transcripts_youtube(video_id):
    # uses youtubetranscriptapi which makes it super easy to do
    # transcript_list = YouTubeTranscriptApi.list_transcripts(
    #     video_id
    # )  #for each video there are many autogenerated transcripts in different languages
    # print(transcript_list)
    # for transcript in transcript_list:

    #     result = transcript.translate('en').fetch()

    #     srt = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    
    ###

    print(video_id)
    try:
        srt = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    except TooManyRequests:
        print("Too many requests \n")
        #srt = [{'text': 'this is where you come and punish', 'start': 0.0, 'duration': 3.99}, {'text': 'yourself for fun a rather for your', 'start': 1.68, 'duration': 4.52}, {'text': 'health', 'start': 3.99, 'duration': 2.21}, {'text': 'here you get rubbed down shaken up', 'start': 7.88, 'duration': 4.27}, {'text': 'crumbled and pushed around for a price', 'start': 10.38, 'duration': 4.049}, {'text': 'and a purpose if you want to turn fat', 'start': 12.15, 'duration': 5.219}, {'text': "and fled into nice hard muscle there's", 'start': 14.429, 'duration': 4.081}, {'text': 'central heating and wall-to-wall', 'start': 17.369, 'duration': 3.481}, {'text': 'carpeting to soften the blows and all', 'start': 18.51, 'duration': 4.679}, {'text': 'kinds of mechanical wonders to waste the', 'start': 20.85, 'duration': 5.089}, {'text': 'way your waste', 'start': 23.189, 'duration': 2.75}, {'text': 'once you join the club you can get down', 'start': 36.5, 'duration': 3.78}, {'text': 'to a workout when you like for as long', 'start': 38.63, 'duration': 3.75}]
        srt = [{'text': 'this is where you come and punish', 'start': 0.0, 'duration': 3.99}]
    except:
        print("some error occurred \n")
        #srt = [{'text': 'this is where you come and punish', 'start': 0.0, 'duration': 3.99}, {'text': 'yourself for fun a rather for your', 'start': 1.68, 'duration': 4.52}, {'text': 'health', 'start': 3.99, 'duration': 2.21}, {'text': 'here you get rubbed down shaken up', 'start': 7.88, 'duration': 4.27}, {'text': 'crumbled and pushed around for a price', 'start': 10.38, 'duration': 4.049}, {'text': 'and a purpose if you want to turn fat', 'start': 12.15, 'duration': 5.219}, {'text': "and fled into nice hard muscle there's", 'start': 14.429, 'duration': 4.081}, {'text': 'central heating and wall-to-wall', 'start': 17.369, 'duration': 3.481}, {'text': 'carpeting to soften the blows and all', 'start': 18.51, 'duration': 4.679}, {'text': 'kinds of mechanical wonders to waste the', 'start': 20.85, 'duration': 5.089}, {'text': 'way your waste', 'start': 23.189, 'duration': 2.75}, {'text': 'once you join the club you can get down', 'start': 36.5, 'duration': 3.78}, {'text': 'to a workout when you like for as long', 'start': 38.63, 'duration': 3.75}]
        srt = [{'text': 'this is where you come and punish', 'start': 0.0, 'duration': 3.99}]

    return srt  #return the transcript


# This function here is to create the clips that are shown when there is not the word we need in the database of words
# takes as args the size (320, 240) and duration of the video and outputs it to color.mp4
def color_clip(size, duration, fps=25, color=(50, 50, 0), output='/tmp/color.mp4'):
    ColorClip(size, color, duration=duration).write_videofile(output, fps=fps)


def make_the_video(srt, video_id):
    #
    # SET UP GOOGLE CLOUD STORAGE FOLDER 
    # 
    bucket_name = "auto-sign-main"
    folder_path = "words_videos/"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    getbucket = storage_client.get_bucket(bucket_name)

    l= 0

    #
    # Create the list of words NOT to translate
    #---------------------------------------------
    words_remove = []
    with open('remove list.txt', 'r') as f:
        for line in f:
            b = line.strip()
            a= b.split('\n')
            words_remove.append(a[0])
    #print(words_remove)
    #---------------------------------------------


    for i in range(len(srt)): 

        #
        # SENTENCE PROCESSING
        # 
        sentence = json.dumps(srt[i]).split('"')[3]  #processing to select sentence from srt #{I, love, gdogs} 3 words
        word_list = sentence.split()  #split sentence in words

        duration = ((json.dumps(srt[i]).split('"')[8]).split(":")[1]).split("}")[0]  #select duration from srt 
        fulltext = sentence + duration
        duration = float(duration)  #make duration become number from string
        duration_per_word = duration / len(word_list)  #divide duration per number of word
        print("DURATION PER WORD: %s", duration_per_word )


        ##video_words = []  #if we have the video of word just put it there
        ##no_video_words = []

        size = (320, 240)  #standard size used in most video
        duration_blank = duration_per_word  #the blank video should last for a word 

        j = 0  #counter to set the first video of the sequence

        # take word list and remov 
        # word_list {parola1, parola 2, parola3}

        # if for parola in word_list == {articolo} {parolo} {avverbi}:
        #     parola = "diocane"

        # word_list{dog diocane diocane}

        #clip = ColorClip(size, (50, 50, 0), duration=duration_blank)
        #translate = False

        # loop going through each word of a sentence
        for word in word_list:

            translate = False
            print(word)
            videoname = word + ".mp4"  #get the filename  "dog.mp4"
            filename = folder_path + videoname #  "video_scarped/dog.mp4"

            # this checks that the file exist, if exist select the sign video otherwise put a blank one
            # Check id word is not in the remove list
            if storage.Blob(bucket=bucket, name=filename).exists(storage_client) and (word not in words_remove):
                print(videoname)

                ##video_words.append(videoname)
                #blob = bucket.blob(filename)
                #blob.download_to_filename(videoname)

                # New code
                word_video = getbucket.get_blob(filename)
                word_video.download_to_filename("/tmp/" + word + ".mp4")
                translate = True

                print("putting it into a videoclipfile")
                try: 
                    # CREATE CLIP (single video)
                    clip = VideoFileClip("/tmp/" + word + ".mp4")
                except:
                    print("For some fucking reason use color clip")
                    translate = False
                    clip = ColorClip(size, (50, 50, 0), duration=duration_blank)


                # TRYING TO RESTART THE DYNOS TO CLEAR MEMORY....
                #os.system("heroku restart --app 'python-microservice'")
                #os.system("heroku ps:restart -a python-microservice")
                    
                #clip = VideoFileClip("'gs://auto-sign-main/words_videos/" + word + ".mp4")
                #clip = VideoFileClip("https://storage.cloud.google.com/auto-sign-main/words_videos/8-8.mp4?authuser=1")  # make the video a VideoFileClip format which moviepy uses
                """
                clip = clip.resize(size)  #check size -> risize clip to fit in the box
                clip_dur = clip.duration  # check duration
                multiplier = clip_dur / duration_blank  #scale it  (5/3) 
                """
                #clip = clip.speedx(multiplier)          # REMOVED THIS FOR DEBUG
                #else make the video blank calling the color_clip function
            else:
                print("NOT FOUND " + videoname)
                ##no_video_words.append(videoname)
                # color_clip(size, duration_blank)
                #clip = ColorClip(size, (50, 50, 0), duration=duration_blank)
            if j == 0 and translate == True:
                final_clip = clip # final clip is for a sentence
                j = j + 1
                close_clip(clip)
            elif translate == True:    
                final_clip = concatenate_videoclips(
                    [final_clip, clip])  #concatenate the clips into a single clip
                close_clip(clip)
                #j = j + 1
            # final_clip is a sentence_video, final_clips_united is the whole video (more sentences together)
        multiplier = final_clip.duration/duration
        if j != 0:
            final_clip = final_clip.fx(vfx.speedx, multiplier)

        # Squeeze final_clip into the duration of the sentence
        if l == 0 and j!= 0:
            final_clips_united = final_clip

        final_clips_united = concatenate_videoclips(
            [final_clips_united, final_clip])
        l = l + 1
        close_clip(final_clip)

    
    #write the final result into a file called finals.mp4
    final_clips_united.write_videofile("/tmp/" + video_id + ".mp4", fps= 24)
    upload_to_bucket(bucket_name, video_id)

    # TRY RESTARTING DYNOS TO CLEAR THE MEMORY
    #os.system("heroku restart --app 'python-microservice'")

    # clip_1 = VideoFileClip("p1b_tetris_1.mp4")
    # clip_2 = VideoFileClip("p1b_tetris_2.mp4")
    # final_clip = concatenate_videoclips([clip_1,clip_2])

    # final_clip.write_videofile("final.mp4")

    #print(video_words)
    #print(no_video_words)
    return fulltext

def upload_to_bucket(bucket_name, video_id):
    try:
        storage_client = storage.Client()
        blob_name = "/tmp/" + video_id + ".mp4"
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(blob_name)
        return True

    except Exception as e:
        print(e)
        return False

def close_clip(clip):
  try:
    clip.reader.close()
    if clip.audio != None:
      clip.audio.reader.close_proc()
      del clip.audio
    del clip
  except Exception as e:
    print("Error in close_clip() ", e)

#main function executed when the program starts
if __name__ == '__main__':
    #you can execute all the functions written here
    #transcript_analysis_from_sentence()
    app.run()



































# Other functions useful 




# same as before but uses a string of text yuo can write
def transcript_analysis_from_sentence():

    fulltext = ""

    l = 0
    for i in range(1):
        sentence = "Hi how are you I will meet you at the restaurant"  # this is the string that will be translated in sign
        word_list = sentence.split()
        duration = 10
        duration_per_word = duration / len(word_list)
        print(duration_per_word)

        video_words = []
        no_video_words = []

        size = (320, 240)
        duration_blank = duration_per_word

        j = 0
        print(word_list)

        for word in word_list:
            print(word)
            videoname = word + ".mp4"
            pathtovideo = Path("/Users/francescocenciarelli/Video_scraped/" +
                               videoname)
            pathtovideo_string = str(pathtovideo)

            if pathtovideo.is_file():
                print(videoname)
                video_words.append(videoname)
                clip = VideoFileClip(pathtovideo_string)
                clip = clip.resize(size)
                clip_dur = clip.duration
                multiplier = clip_dur / duration_blank
                #clip = clip.speedx(multiplier)
            else:
                no_video_words.append(videoname)
                color_clip(size, duration_blank)
                clip = VideoFileClip(
                    "/Users/francescocenciarelli/Desktop/University/Year3/Programming3 /Microservice/color.mp4"
                )

            if j == 0:
                final_clip = clip
            final_clip = concatenate_videoclips([final_clip, clip])
            j = j + 1

        if l == 0:
            final_clips_united = final_clip

        final_clips_united = concatenate_videoclips(
            [final_clips_united, final_clip])
        l = l + 1
        # if l == 5:
        #   cripper = VideoFileClip("/Users/francescocenciarelli/Desktop/University/Year3/Programming3 /Microservice/NLE Choppa throwing up gang signs while buying grills-ukNvLsGvdC4.mp4")
        #   cripper = cripper.resize(size)
        #   final_clips_united = concatenate_videoclips([final_clips_united, cripper])
        #   print(l)

    final_clips_united.write_videofile("videoooo.mp4")

    # clip_1 = VideoFileClip("p1b_tetris_1.mp4")
    # clip_2 = VideoFileClip("p1b_tetris_2.mp4")
    # final_clip = concatenate_videoclips([clip_1,clip_2])
    # final_clip.write_videofile("final.mp4")

    print(video_words)
    print(no_video_words)
    return fulltext




# this is the function to translate the transcript to sign video
def transcript_analysis(srt):

    fulltext = ""

    print("/n")
    print(
        srt[5]
    )  # this is the format of the text outputted by YOutube_transcript_api

    l = 0  #counter to set the first video of the sequence

    # 2 loops: 1 to concat words in a sentence the other to concat sentences into a single video
    for i in range(len(srt)): # "I love dogs" "5"
        sentence = json.dumps(
            srt[i]).split('"')[3]  #processing to select sentence from srt #{I, love, gdogs} 3 words
        word_list = sentence.split()  #split sentence in words
        duration = ((json.dumps(srt[i]).split('"')[8]).split(":")[1]
                    ).split("}")[0]  #select duration from srt 
        fulltext = sentence + duration
        duration = float(duration)  #make duration become number from string
        duration_per_word = duration / len(
            word_list)  #divide duration per number of word
        print(duration_per_word)

        video_words = []  #if we have the video of word just put it there
        no_video_words = []

        size = (320, 240)  #standard size used in most video
        duration_blank = duration_per_word  #the blank video should last for a word 

        j = 0  #counter to set the first video of the sequence
        print(word_list) # I , love , dogs

        #Connect to google cloud storage 

        bucket_name = 'scraped_videos_sign'

        # loop going through each word of a sentence
        for word in word_list:
            print(word)
            videoname = word + ".mp4"  #get the filename 
            pathtovideo = Path("Video_scraped/" +
                               videoname)
            pathtovideo_string = str(pathtovideo)
            # this checks that the file exist, if exist select the sign video otherwise put a blank one
            if pathtovideo.is_file():
                print(videoname)
                video_words.append(videoname)
                clip = VideoFileClip(
                    pathtovideo_string
                )  # make the video a VideoFileClip format which moviepy uses
                clip = clip.resize(size)  #check size
                clip_dur = clip.duration  # check duration
                multiplier = clip_dur / duration_blank  #scale it  (5/3) 
                clip = clip.speedx(multiplier)
                # else make the video blank calling the color_clip function
            else:
                no_video_words.append(videoname)
                color_clip(size, duration_blank)
                clip = VideoFileClip(
                    "color.mp4" # TO CHANGE
                )

            if j == 0:
                final_clip = clip # final clip is for a sentence
            final_clip = concatenate_videoclips(
                [final_clip, clip])  #concatenate the clips into a single clip
            j = j + 1
            # final_clip is a sentence, final_clips_united is the whole video (more sentences together)

        if l == 0:
            final_clips_united = final_clip

        final_clips_united = concatenate_videoclips(
            [final_clips_united, final_clip])
        l = l + 1

    # write the final result into a file called finals.mp4
    final_clips_united.write_videofile("finals.mp4")

    # clip_1 = VideoFileClip("p1b_tetris_1.mp4")
    # clip_2 = VideoFileClip("p1b_tetris_2.mp4")
    # final_clip = concatenate_videoclips([clip_1,clip_2])
    # final_clip.write_videofile("final.mp4")

    print(video_words)
    print(no_video_words)
    return fulltext



#takes in only the video link and uses YOUTUBE_DL to download video
def video_downloader(video_link):

    print(video_link)

    ydl_opts = {}  # no options needed to download the plain video
    # with the options use the YOUTUBE DL download function, the file will be stored in the current folder
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_link])

    return 0


#same as video_downloader but with different options to download audio
def audio_downloader(video_link):
    print(video_link)
    # Setting option for file format and quality
    ydl_opts = {
        'format':
        'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }]
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_link])

    return 0