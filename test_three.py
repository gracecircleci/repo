# catalog.py
import os.path
import json, time
import urllib.request
from urllib.parse import unquote, quote, urlparse
from enum import Enum
import pandas as pd
from pandas import json_normalize
import unittest

class SimpleTest(unittest.TestCase):
  def test(self):
    self.assertTrue(True)

class CatalogEnum(Enum):
    HOME = 1
    SHOWS =2
    MOVIES = 3
    def __str__(self):
        return '%s' % self.name

class Const:
    @property
    def HEADERS(self):
        epoch_time = int(time.time())

        header_str = '''
        {
            "Content-Type": "application/json",
            "LanguageIso2Code": "EN",
            "CountryIso2Code": "US",
            "ClientDateTimeSeconds": %d,
            "SctvVersion": "5.0.0.0",
            "ModelName": "E50-F2"  
        }''' % epoch_time
        #ToDo: "ModelName": "E50-F2" # is this needed
        headersdict = json.loads(header_str)
        return json.dumps(headersdict)

if __name__ == '__main__':
  url = 'http://catalog-dev.smartcasttv.com/catalogs?rowsToExpand=3' 
  headers = json.loads(Const().HEADERS)
  payload_str = '{ "Catalogs":[{ "Id" : 1 }]}'
  data = json.loads(payload_str)
  data = json.dumps(data)
  data = str.encode(data)
  req = urllib.request.Request(url, headers=headers)
  response = urllib.request.urlopen(req, data)
  print('response status=', response.status)
  assert response.status==200

  print('calling unittest.main')
  unittest.main()
  print('calling done unittest.main')
