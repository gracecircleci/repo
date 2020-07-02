import argparse, textwrap
import os.path
import json, time
from urllib.parse import unquote, quote, urlparse
from util.urlutils import EzUtil
from util.logging import EzLogger
from util.datautils import DataUtil
from util.urlutils import EzUtil, EnvironCommon, CatalogEnum
import pandas as pd
from pandas import json_normalize

class Const:
    @property
    def HEADERS(self):
        device_context_json_str = '''{"SYSTEM_INFO":{"SUBSERIES":"M8","SOC":0,"SERIES":"M","MODEL_RESOLUTION":2,"DIID":"9d021e22-c237-4253-asdf-ccbb1234567c","VERSION":"6.0.11.1","DEVICE_TYPE":0,"CHIPSET":2,"MODEL_TYPE":4,"PANEL_TYPE":0,"TVAD_ID":{"LMT":0,"IFA":"aa84c930-asdf-asdf-8cc0-123b55b2ff07","IFA_TYPE":"dpid"},"MODEL_NAME":"M558-G1","SIZE":558},"CAPABILITIES":{"FRC":False,"USB_POWER":True,"ABC":True,"HDR":[0,1,2,3],"MEMC":False,"BATTERY":False,"type":"tvtuner","ACCESSIBILITY":{"TTS":True,"ZOOMMODE":True},"memc":0,"BLE":False,"TUNER":True,"ENERGY_STAR":False,"BACKLIGHT":False},"SC_INFO":"HOME-TEST v53.8","BINARIES":{"CONJURE":"SX7B-3.0.315.0","AIRPLAY":"0.0.4644","COBALT":"0.19.8011"},"MODEL_NAME":"M558-G1","API_VERSION":"1.0.13_1.0.13.29_1949_0001","model":"M558-G1","modelName":"M558-G1","modelResolution":2,"modelSeries":"M","vendor":"Sigma","firmwareVersion":"6.0.11.1","scplVersion":[1949,1],"modelType":4}'''
        epoch_time = int(time.time())

        header_str = '''
        {
            "Content-Type": "application/json",
            "LanguageIso2Code": "EN",
            "CountryIso2Code": "US",
            "ClientDateTimeSeconds": %d,
            "SctvVersion": "5.0.0.0",
            "ModelName": "E50-F2",
            "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxODQzMTYyNCIsInByaW1hcnlQcm9maWxlIjp7InByb2ZpbGVJZCI6IjE3ODQ5NTM0IiwibG9jYXRpb24iOnt9fSwiaWF0IjoxNTkzMjA0ODE1LCJleHAiOjE2NTYyNzY4MTUsImF1ZCI6InNjdHYiLCJpc3MiOiJ2aXppby5jb20iLCJzdWIiOiIxODQzMTYyNCJ9.F3MGlsHoZP5i7ECv-wOtZ5i2eK-qoS3YTrY9FwcC4xcQ620YOGCjDMK_u6qZTsJbP-StHLAVG-oQRsRh0Sz2wA_AtiHscELmUoKpWdrGUTaGoPh9EXHJQ-Df69P2SQ0PmQJ_1a7xzLPxT2jxFGG5J0QuFZ86hpWWrghe3qsoWsHe3uG_QbJR9hbEMYF9OJjlED-tBByoaGWvKdimrCt7qAm9i-eZ1E3dejzP8fuoDkCj6Do-vKUbLkfNcdPGWMB8-1O37uAMQk4f_5zcFlZYFRtRY6n3BKh3hCTY1Il_xEDwLG4eBz0RfAmQNqwiEZ7WYKgCYEvGJQ3hHJDuU3iIcQ",
            "overrides" : "{'BypassFeatureListCache':'true'}" 
        }''' % (epoch_time)

        headersdict = json.loads(header_str)
        return json.dumps(headersdict)


class Catalog(object):
    def __init__(self,proto=None, host=None, uri=None, query_string=None, url=None):
        self.protocol = proto
        self.host = host
        self.uri = uri
        self.qs = query_string

        self.logger = EzLogger.getLogger(__file__)

    def getJsonFromCatalogUrl(self, catalogId=CatalogEnum.HOME.value, url=None):
        # construct and visit home_tab url
        if url is None:
            url = EzUtil.constructUrl(protocol=self.protocol, host=self.host, uri=self.uri, qstring=self.qs)
        assert url
        outfile = 'output/catalog_%s.json' % CatalogEnum(catalogId)
        payload_str = '{ "Catalogs":[{ "Id" : %d }]}' % catalogId
        data = json.loads(payload_str)
        headersdict = json.loads(Const().HEADERS)
        status_code, url, jsonobj = EzUtil.urlToJsonWithPost(url, data_dict=data, hds_dict=headersdict, outfile=outfile)
        assert status_code == 200
        assert jsonobj is not None
        self.logger.info('catalog url=%s. output json file is available %s' % (url, outfile))
        print('catalog url=%s. output json file is available %s' % (url, outfile))
        return url, jsonobj