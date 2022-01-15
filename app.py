# Importing the libraries used

from __future__ import print_function
from flask import Flask, jsonify, request
import json
import urllib.request
from urllib.request import Request, urlopen
import requests
import bs4 as bs4
import requests
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
import gc
import sys


# Declearing that the app is using Flask
app = Flask(__name__)

#SET UP Google Credential
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google-credentials.json'


# debugging route to check the server works
@app.route('/')
def home():
    return "We are online"


# IMPORTANT This function gets the url of the video from java via a HTTP request with POST method
@app.route('/download', methods=['POST'])  #sending a post request to '/' the function getdata is called
def getdata():
    print("The header is: ")
    print(request.headers)  #this is just to see the details of the request
    print("The json is: ")
    print(request.get_json())  #the request is sent through json format where the link is stored
    url = json.dumps(request.get_json()).split('"')[3]
    video_id = url.split("v=")[1]
    
    #Making a list of videos already in the Database
    if video_id== "RwQnRWTWcVE" or video_id== "SCkc2cEHrGk" or video_id== "mophXhMJguw":
        return Response(status=201)
    

    # The thread containing the functions to translate the video is executed in background
    thread_a = VideoMaking(request.__copy__()) # Passing the POST req to it
    thread_a.start()

    return Response(status=201)


class VideoMaking(Thread):
    def __init__(self, request):
        Thread.__init__(self)
        self.__running = True
        self.request = request

    def run(self):
        url = json.dumps(self.request.get_json()).split('"')[3]
        video_id = url.split("v=")[1]
        
        print(video_id)
        srt = retrieve_transcripts_youtube(video_id) #Obtain subtitles from youtube
        print(srt) # For debugging
        fulltext = make_the_video(srt, video_id) # Translate the subtitles
        gc.collect() # clean memory
        sys.exit()
        return


#function to get the transcript from yotube taking in the youtube id (letters and numbers after watch?v= in the youtube link)
def retrieve_transcripts_youtube(video_id):
    print(video_id)
    # If YTtranscript API stops working send error message
    try:
        srt = YouTubeTranscriptApi.get_transcript(video_id, languages=['en']) 
    except TooManyRequests:
        print("Too many requests")
        srt = [{'text': 'this is where you come and punish', 'start': 0.0, 'duration': 3.99}, {'text': 'yourself for fun a rather for your', 'start': 1.68, 'duration': 4.52}, {'text': 'health', 'start': 3.99, 'duration': 2.21}, {'text': 'here you get rubbed down shaken up', 'start': 7.88, 'duration': 4.27}, {'text': 'crumbled and pushed around for a price', 'start': 10.38, 'duration': 4.049}, {'text': 'and a purpose if you want to turn fat', 'start': 12.15, 'duration': 5.219}, {'text': "and fled into nice hard muscle there's", 'start': 14.429, 'duration': 4.081}, {'text': 'central heating and wall-to-wall', 'start': 17.369, 'duration': 3.481}, {'text': 'carpeting to soften the blows and all', 'start': 18.51, 'duration': 4.679}, {'text': 'kinds of mechanical wonders to waste the', 'start': 20.85, 'duration': 5.089}, {'text': 'way your waste', 'start': 23.189, 'duration': 2.75}, {'text': 'once you join the club you can get down', 'start': 36.5, 'duration': 3.78}, {'text': 'to a workout when you like for as long', 'start': 38.63, 'duration': 3.75}]
    except:
        print("some error occurred")
        srt = [{'text': 'this is where you come and punish', 'start': 0.0, 'duration': 3.99}, {'text': 'yourself for fun a rather for your', 'start': 1.68, 'duration': 4.52}, {'text': 'health', 'start': 3.99, 'duration': 2.21}, {'text': 'here you get rubbed down shaken up', 'start': 7.88, 'duration': 4.27}, {'text': 'crumbled and pushed around for a price', 'start': 10.38, 'duration': 4.049}, {'text': 'and a purpose if you want to turn fat', 'start': 12.15, 'duration': 5.219}, {'text': "and fled into nice hard muscle there's", 'start': 14.429, 'duration': 4.081}, {'text': 'central heating and wall-to-wall', 'start': 17.369, 'duration': 3.481}, {'text': 'carpeting to soften the blows and all', 'start': 18.51, 'duration': 4.679}, {'text': 'kinds of mechanical wonders to waste the', 'start': 20.85, 'duration': 5.089}, {'text': 'way your waste', 'start': 23.189, 'duration': 2.75}, {'text': 'once you join the club you can get down', 'start': 36.5, 'duration': 3.78}, {'text': 'to a workout when you like for as long', 'start': 38.63, 'duration': 3.75}]

    return srt  #return the transcript


def make_the_video(srt, video_id):
    #
    # SET UP GOOGLE CLOUD STORAGE FOLDER 
    # 
    bucket_name = "auto-sign-main"
    folder_path = "words_videos/"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    getbucket = storage_client.get_bucket(bucket_name)
    
    #Create a list of words to not translate
    words_remove = []
    with open('remove list.txt', 'r') as f:
        for line in f:
            b = line.strip()
            a= b.split('\n')
            words_remove.append(a[0])

    l= 0
    for i in range(len(srt)): 

        #
        # SENTENCE PROCESSING
        # 
        sentence = json.dumps(srt[i]).split('"')[3]  #processing to select sentence from srt 
        word_list = sentence.split()  #split sentence in words e.g. {I, love, dogs} 3 words

        fakeduration = ((json.dumps(srt[i]).split('"')[8]).split(":")[1]).split("}")[0]  #This duration is not accurate
        start = (json.dumps(srt[i]).split('"')[6]).split(":")[1].split(",")[0] #Take start time 

        try:
            startnext = (json.dumps(srt[i+1]).split('"')[6]).split(":")[1].split(",")[0] # Take next video start time
            duration = float(startnext)- float(start) #This is the real duration
        except IndexError: 
            duration = float(fakeduration) # For the last index use the other duration

        fulltext = sentence + fakeduration
        duration_blank = duration / len(
            word_list)  #divide duration per number of word

        size = (320, 240)  #standard size used in most video  #the blank video should last for a word 

        j = 0  #counter to set the first video of the sequence


        # loop going through each word of a sentence
        for word in word_list:
 
            print(word)
            videoname = word + ".mp4"  #get the filename  "dog.mp4"
            filename = folder_path + videoname #  "video_scarped/dog.mp4"

            # this checks that the file exist, if exist select the sign video otherwise put a blank one
            if storage.Blob(bucket=bucket, name=filename).exists(storage_client) and (word not in words_remove):
                print(videoname)

                # Download signed video from GCS
                word_video = getbucket.get_blob(filename)
                gc.collect()
                word_video.download_to_filename("/tmp/" + word + ".mp4")
                
                gc.collect()

                print("putting it into a videoclipfile")
                try: 
                    clip = VideoFileClip("/tmp/" + word + ".mp4")     
                    # Generate a text clip 
                    word_str = word.encode('utf8')
                    txt_clip = (TextClip(word_str, fontsize = 70, color = 'white').set_position('center')).set_duration(clip.duration) 
                    clip = CompositeVideoClip([clip, txt_clip])
                    close_clip(txt_clip)
                except Exception as e:
                    print(e)
                    clip = ImageClip("blank_image.png").set_duration(duration_blank)
                    
                os.remove("/tmp/" + word + ".mp4")
  
                clip = clip.resize(size)  #check size
                clip_dur = clip.duration  # check duration
                multiplier = clip_dur / duration_blank  #scale it  (5/3) 
                clip = clip.speedx(multiplier)          # REMOVED THIS FOR DEBUG
                gc.collect()
            else:
                print("NOT FOUND " + videoname)
                clip = ImageClip("blank_image.png").set_duration(duration_blank)
                clip = clip.resize(size)
                gc.collect()
            if j == 0:
                final_clip = clip # final clip is for a sentence
            else:
                final_clip = concatenate_videoclips([final_clip, clip])  #concatenate the clips into a single clip
                gc.collect()
            close_clip(clip)
            j = j + 1
            # final_clip is a sentence, final_clips_united is the whole video (more sentences together)
        final_clip_dur = final_clip.duration
        print(final_clip_dur)
        if l == 0:
            final_clips_united = final_clip
        else:
            final_clips_united = concatenate_videoclips([final_clips_united, final_clip])
         
        l = l + 1
        close_clip(final_clip)
        gc.collect()
    #write the final result into a file called finals.mp4
    final_clips_united.write_videofile("/tmp/" + video_id + ".mp4", fps= 10)
    
    close_clip(final_clips_united)
    gc.collect()
    
    storage_client._http.close()

    upload_to_bucket(bucket_name, video_id)
    
    os.remove("/tmp/" + video_id + ".mp4")
    
    gc.collect()

    return fulltext

#Upload final result to Google Cloud
def upload_to_bucket(bucket_name, video_id):
    try:
        storage_client = storage.Client() # Enstablish connection
        blob_name = "/tmp/" + video_id + ".mp4" #Name the video with the video_id
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(blob_name)
        gc.collect()
        storage_client._http.close()
        return True

    except Exception as e:
        print(e)
        return False

#Closing and deleting VideoClips to avoid memory leaks
def close_clip(clip):
  try:
    clip.close()
    clip.reader.close()
    if clip.audio != None:
      clip.audio.reader.close_proc()
      del clip.audio
    del clip
    gc.collect()
  except Exception as e:
    del clip
    gc.collect()
    print("Error in close_clip() ", e)

#main function executed when the program starts
if __name__ == '__main__':
    app.run()
