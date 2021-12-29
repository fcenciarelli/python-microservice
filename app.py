
# Importing the libraries

from __future__ import print_function
from flask import Flask, jsonify, request
import json
import urllib.request
from urllib.request import Request, urlopen
import requests
import bs4 as bs4
import requests
#import pandas as pd
#import numpy as np
import youtube_dl
from flask import send_file, send_from_directory, safe_join, abort
from pydub import AudioSegment
from pydub.silence import split_on_silence
from youtube_transcript_api import YouTubeTranscriptApi
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
        srt = retrieve_transcripts_youtube(video_id)
        print(srt)
        make_the_video(srt, video_id)
        #url = heroku link to the java app when we will have it
        #send_done_confirmation(url, videoid)


#function to get the transcript from yotube taking in the youtube id (letters and numbers after watch?v= in the youtube link)
def retrieve_transcripts_youtube(video_id):
    # uses youtubetranscriptapi which makes it super easy to do
    transcript_list = YouTubeTranscriptApi.list_transcripts(
        video_id
    )  #for each video there are many autogenerated transcripts in different languages

    for transcript in transcript_list:
        # print(
        #     transcript.video_id,
        #     transcript.language,
        #     transcript.language_code,

        #     # whether it has been manually created or
        #     # generated by YouTube
        #     transcript.is_generated,
        # )

        result = transcript.translate('en').fetch()

        # translating the transcript will return another
        # transcript object
        #print(transcript.translate('en').fetch())

        #select the transcript and put it into a variable called srt

        srt = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])

        #this thing is if you want to save the transcript into a file

        #filename = "subtitles_" + video_id

        # LOOP TO DOWNLOAD TRANCRIPTI TO FILE

        # with open(filename, "w") as f:
        #       # iterating through each element of list srt
        #   for i in srt:
        #       # writing each element of srt on a new line
        #       f.write("{}\n".format(i))

    return srt  #return the transcript


# This function here is to create the clips that are shown when there is not the word we need in the database of words
# takes as args the size (320, 240) and duration of the video and outputs it to color.mp4
def color_clip(size, duration, fps=25, color=(50, 50, 0), output='color.mp4'):
    ColorClip(size, color, duration=duration).write_videofile(output, fps=fps)


def make_the_video(srt, video_id):
    #
    # SET UP GOOGLE CLOUD STORAGE FOLDER 
    # 
    bucket_name = "auto-sign-main"
    folder_path = "words_videos/"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)


    for i in range(len(srt)): 

        #
        # SENTENCE PROCESSING
        # 
        sentence = json.dumps(srt[i]).split('"')[3]  #processing to select sentence from srt #{I, love, gdogs} 3 words
        word_list = sentence.split()  #split sentence in words

        duration = ((json.dumps(srt[i]).split('"')[8]).split(":")[1]).split("}")[0]  #select duration from srt 
        fulltext = sentence + duration
        duration = float(duration)  #make duration become number from string
        duration_per_word = duration / len(
            word_list)  #divide duration per number of word

        video_words = []  #if we have the video of word just put it there
        no_video_words = []

        size = (320, 240)  #standard size used in most video
        duration_blank = duration_per_word  #the blank video should last for a word 

        j = 0  #counter to set the first video of the sequence

        # loop going through each word of a sentence
        for word in word_list:
 
            print(word)
            videoname = word + ".mp4"  #get the filename  "dog.mp4"
            filename = folder_path + videoname #  "video_scarped/dog.mp4"

            video_path = 'file:gs://' + bucket_name + '/' + filename

            # this checks that the file exist, if exist select the sign video otherwise put a blank one
            if storage.Blob(bucket=bucket, name=filename).exists(storage_client):
                print(videoname)

                video_words.append(videoname)

                clip = VideoFileClip(video_path)  # make the video a VideoFileClip format which moviepy uses
                clip = clip.resize(size)  #check size
                clip_dur = clip.duration  # check duration
                multiplier = clip_dur / duration_blank  #scale it  (5/3) 
                clip = clip.speedx(multiplier)
                #else make the video blank calling the color_clip function
            else:
                print("NOT FOUND " + videoname)
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

    #write the final result into a file called finals.mp4
    final_clips_united.write_videofile(video_id + ".mp4")
    #upload_to_bucket('finals.mp4', file_path, "data_bucket_video_swag" )

    upload_to_bucket(bucket_name, video_id)

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
        blob_name = video_id + ".mp4"
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(blob_name)
        return True

    except Exception as e:
        print(e)
        return False




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