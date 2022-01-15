
import json
import re
import unittest
from xml.etree.ElementTree import tostring
import app
from app import retrieve_transcripts_youtube
from app import upload_to_bucket

class TestSum(unittest.TestCase):

    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()
    
    def test_get(self):
        result = self.app.get('/') 
        self.assertEqual(result.status_code, 200, "Test Failed") 

    def test_retrieve_transcripts_youtube(self):
        #random video id --> expect usual str
        #print(retrieve_transcripts_youtube("hjjkak"))
        #print("\n\n\n")
        srt = [{'text': 'this is where you come and punish', 'start': 0.0, 'duration': 3.99}, {'text': 'yourself for fun a rather for your', 'start': 1.68, 'duration': 4.52}, {'text': 'health', 'start': 3.99, 'duration': 2.21}, {'text': 'here you get rubbed down shaken up', 'start': 7.88, 'duration': 4.27}, {'text': 'crumbled and pushed around for a price', 'start': 10.38, 'duration': 4.049}, {'text': 'and a purpose if you want to turn fat', 'start': 12.15, 'duration': 5.219}, {'text': "and fled into nice hard muscle there's", 'start': 14.429, 'duration': 4.081}, {'text': 'central heating and wall-to-wall', 'start': 17.369, 'duration': 3.481}, {'text': 'carpeting to soften the blows and all', 'start': 18.51, 'duration': 4.679}, {'text': 'kinds of mechanical wonders to waste the', 'start': 20.85, 'duration': 5.089}, {'text': 'way your waste', 'start': 23.189, 'duration': 2.75}, {'text': 'once you join the club you can get down', 'start': 36.5, 'duration': 3.78}, {'text': 'to a workout when you like for as long', 'start': 38.63, 'duration': 3.75}]
        sentence = json.dumps(srt[0]).split('"')[3]
        print(sentence)
        self.assertEqual(sentence, "this is where you come and punish", "Test Failed")

if __name__ == '__main__':
    unittest.main()
    


