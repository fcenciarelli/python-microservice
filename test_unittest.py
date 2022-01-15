
import json
import re
import unittest
from xml.etree.ElementTree import tostring
import app
from app import retrieve_transcripts_youtube
from app import upload_to_bucket

# This class contains unit tests for the app.py app
# The tests use the unittesting framework
class TestSum(unittest.TestCase):

    # setup the app as client to carry out get-request tests
    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()
    
    # test the get request to "/" returns a valid status code (200) by asserting the result is equal to 200
    def test_get(self):
        result = self.app.get('/') 
        self.assertEqual(result.status_code, 200, "Test Failed") 

    # test the retrieve_transcripts_youtube function by inputting a wrong videoID and checking whether the output is the proper one 
    # the output is used as an "emergency" srt
    def test_retrieve_transcripts_youtube(self):
        srt = retrieve_transcripts_youtube("fhsjd") # retrieves transcript from the function
        sentence = json.dumps(srt[0]).split('"')[3]
        self.assertEqual(sentence, "this is where you come and punish", "Test Failed") # asserts the first sentence of the transcript is the expected one

if __name__ == '__main__':
    unittest.main()
    


