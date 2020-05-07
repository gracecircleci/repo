# catalog.py
import os.path
import json, time
from urllib.parse import unquote, quote, urlparse
from enum import Enum
from util.urlutils import EzUtil
from util.logging import EzLogger
from util.datautils import DataUtil
import pandas as pd
from pandas import json_normalize

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

class Catalog(object):    
    def __init__(self):
        self.logger = EzLogger.getLogger(__file__)

    def getCatalogRowIdList(self, url, catalogId=CatalogEnum.HOME.value, outfile='output/catalog.json'):
        assert url is not None
        headers = json.loads(Const().HEADERS)
        payload_str = '{ "Catalogs":[{ "Id" : %d }]}' % catalogId
        data = json.loads(payload_str)
    
        status, url, jsonobj = EzUtil().urlToJsonWithPost(url=url, data_dict=data, hds_dict=headers, outfile=outfile)
        self.logger.info('making http POST request. url=%s' % unquote(url))
        self.logger.info('http HEADERS %s. http payload %s' % (headers, payload_str ))
        self.logger.info('response status_code=%s. Json file is available at %s' % (status, outfile ))

        catalog_id = self.getCatalogId(jsonobj)
        catalog_title = self.getCatalogTitle(jsonobj)
        rows = self.getCatalogRows(jsonobj)
        self.logger.info('catalog[id=%s, title=%s] rows=%s' % 
            (catalog_id, catalog_title, rows))
        return catalog_id, catalog_title, rows


    def getCatalogById(self, catJsonObj, catalog_id):
        assert (catalog_id > 0 )
        catalogJsonObj = catJsonObj['catalogs'][catalog_id]
        return catJsonObj['catalogs'][catalog_id]['id']  

    def getCatalogId(self,catJsonObj):
        return catJsonObj['catalogs'][0]['id'] 

    def getCatalogTitle(self,catJsonObj):
        return catJsonObj['catalogs'][0]['title']
    
    def getCatalogRows(self, catJsonObj):
        self.logger.info('catalog_rows=%s' % catJsonObj['catalogs'][0]['rows'])
        return catJsonObj['catalogs'][0]['rows']
   
    def getItems(self,catJsonObj):
        return catJsonObj['catalogs'][0]['items']

    def getCatalogJsonObjFromUrl(self, url, catalogId=CatalogEnum.HOME.value, outfile='output/catalog.json'):
        assert url is not None
        headers = json.loads(Const().HEADERS)
        payload_str = '{ "Catalogs":[{ "Id" : %d }]}' % catalogId
        data = json.loads(payload_str)
    
        status, url, jsonobj = EzUtil().urlToJsonWithPost(url=url, data_dict=data, hds_dict=headers, outfile=outfile)
        self.logger.info('making http POST request. url=%s' % unquote(url))
        self.logger.info('http HEADERS %s. http payload %s' % (headers, payload_str ))
        self.logger.info('response status_code=%s. Json file is available at %s' % (status, outfile ))
        
        return status, url, jsonobj

    def getRowDetailsByIndex(self,catJsonObj, row_index=0, cols=['id', 'title', 'subTitle', 'action']):
        assert isinstance(row_index, int) and row_index >=0
        assert catJsonObj is not None

        catalogTitle = self.getCatalogTitle(catJsonObj) # cat title
        catalogId = self.getCatalogId(catJsonObj)

        self.logger.info('%s INFO: catalogId=%d' % (__file__, catalogId))
        row = catJsonObj['rows'][row_index]
        self.logger.info('%s INFO: row=%s' % (__file__, row))

        dfRowIndex = None
        # ['id', 'title', 'subTitle', 'action', 'metadata', 'imagePath']
        dfColIndex = ['id', 'title', 'subTitle', 'action']
        df = pd.DataFrame(data=catJsonObj['items'], index=dfRowIndex, columns=dfColIndex)
        df = df.loc[ df['id'].isin(row['items'])] # row['items'] example:[28269,28117,28119,28268,28124]

        return row['id'], row['title'], row['items']

    def print_catalog_rows(self, catJsonObj):
        rows = self.getCatalogRows(catJsonObj)
        for pos in range(len(rows)):
            print('\n\n ==== Row %d ====' % pos)
            print('\n -- row', rows[pos])
            row_id, row_title, row_items, df = self.getRowDetailsByIndex(
                catJsonObj,
                row_index=pos, 
                cols=['id', 'title', 'subTitle', 'action','imagePath'])
            print('row_id=%s, row_title=%s \n\n rows=%s' % (row_id, row_title, row_items))
            print(df)

    @staticmethod
    def run_cat_rows():
        #curl -i -X POST -H 'Content-Type: application/json' -H 'LanguageIso2Code: EN' -H 'CountryIso2Code: US' -H 'ClientDateTimeSeconds: 1588700639' -H 'SctvVersion: 5.0.0.0' -H 'ModelName: E50-F2' -d '{ "Catalogs":[{ "Id" : 1 }]}' http://catalog-dev.smartcasttv.com/catalogs?rowsToExpand=3
        url = 'http://catalog-dev.smartcasttv.com/catalogs?rowsToExpand=3' 
        catalog_id, catalog_title, row_list = Catalog().getCatalogRowIdList(url)
        return catalog_id, catalog_title, row_list

    @staticmethod
    def run_cat_home_iids():
        url = 'http://catalog-dev.smartcasttv.com/catalogs?rowsToExpand=100' 
        status, url, jsonobj = Catalog().getCatalogJsonObjFromUrl(url)
        catalog_id, catalog_title, rows = Catalog().getRowDetailsByIndex(jsonobj)
        return catalog_id, catalog_title, rows

if __name__ == '__main__':
    catalog_id, catalog_title, row_list = Catalog().run_cat_rows()
    catalog_id, catalog_title, rows = Catalog().run_cat_home_iids()



