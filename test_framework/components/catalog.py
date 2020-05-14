import argparse, textwrap
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

        outfile = 'output/catqlog.json'
        payload_str = '{ "Catalogs":[{ "Id" : %d }]}' % catalogId
        data = json.loads(payload_str)
        headersdict = json.loads(Const().HEADERS)
        status_code, url, jsonobj = EzUtil.urlToJsonWithPost(url, data_dict=data, hds_dict=headersdict, outfile=outfile)
        assert status_code == 200
        assert jsonobj is not None
        self.logger.info('catalog url=%s. output json file is available %s' % (url, outfile))
        return url, jsonobj

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
        #print('df=', df)
        df = df.loc[ df['id'].isin(row['items'])] # row['items'] example:[28269,28117,28119,28268,28124]
        #print('df=', df)

        return row['id'], row['title'], row['items']

    def getRowItemDetails(self, catJsonObj, row_index=0, cols=['id', 'title', 'subTitle', 'action'], iid_idx=0):
        assert catJsonObj is not None
        assert isinstance(row_index, int) and row_index >=0
        assert iid_idx is not None

        catalogTitle = self.getCatalogTitle(catJsonObj) # cat title
        catalogId = self.getCatalogId(catJsonObj)

        row = catJsonObj['rows'][row_index]

        dfRowIndex = None
        dfColIndex = ['id', 'title', 'subTitle', 'action', 'metadata', 'imagePath']
        df = pd.DataFrame(data=catJsonObj['items'], index=dfRowIndex, columns=dfColIndex)
        df = df.loc[df['id'].isin(row['items'])]  # row['items'] example:[28269,28117,28119,28268,28124]
        #print('df=', df)
        # item_details for item of iid_idx
        print('row=', row['items'][iid_idx])
        series1 = df[df['id'] == row['items'][iid_idx]]  # get item details of iid (example: 28117)
        # series1 is like a dictionary
        the_json = series1.to_json(orient='columns')
        item_detail_jsonobj = json.loads(the_json)
        dict1 = {}
        dict1['title'] = item_detail_jsonobj['title']
        dict1['id'] = item_detail_jsonobj['id']
        dict1['subtitle'] = item_detail_jsonobj['subTitle']
        dict1['imagePath'] = item_detail_jsonobj['imagePath']
        dict1['action'] = item_detail_jsonobj['action']
        dict1['metadata'] = item_detail_jsonobj['metadata']
        return dict1




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
        cat = Catalog()
        cat_url, catJsonObj = cat.getJsonFromCatalogUrl(catalogId=CatalogEnum.HOME.value, url=url)
        catalog_id, catalog_title, row_list = Catalog().getCatalogRowIdList(cat_url)
        return catalog_id, catalog_title, row_list

    @staticmethod
    def run_cat_home_iids(row_index=0):
        proto, host, uri, qs, url = get_command_line_args()
        cat = Catalog(proto, host, uri, qs)
        url, jsonobj  = cat.getJsonFromCatalogUrl(url=None)

        catalog_id, catalog_title, rows = cat.getRowDetailsByIndex(jsonobj, row_index=row_index)
        return catalog_id, catalog_title, rows

    @staticmethod
    def run_cat_home_row_item(row_index=0, item_index=0):
        proto, host, uri, qs, url = get_command_line_args()
        cat = Catalog(proto, host, uri, qs)
        url, jsonobj  = cat.getJsonFromCatalogUrl(url=None)
        dict1 = cat.getRowItemDetails(jsonobj, row_index=0, iid_idx=item_index)
        print('title=%s, id=%s, subTitle=%s, imagePath=%s, \n\n action=%s, metadata=%s' %
              (dict1['title'], dict1['id'], dict1['subtitle'], dict1['imagePath'], dict1['action'], dict1['metadata']))

        return dict1


example_text = '''example:
  python3 components/catalog.py --protocol 'http' --host 'catalog-dev.smartcasttv.com' --uri 'catalogs' --qs 'rowsToExpand=100'
  or 
  python3 components/catalog.py --url 'http://catalog-dev.smartcasttv.com/catalogs?rowsToExpand=100'
 '''

def get_command_line_args():
    parser = argparse.ArgumentParser(epilog=example_text, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--protocol', default='http', help='protocol eg: http or https')
    parser.add_argument('--host', default='catalog-dev.smartcasttv.com', help='host eg: catalog-dev.smartcasttv.com')
    parser.add_argument('--uri', default='catalogs',help='catalogs')
    parser.add_argument('--qs', default='rowsToExpand=100',help='query_sting eg: rowsToExpand=100')
    parser.add_argument('--url', default='http://catalog-dev.smartcasttv.com/catalogs?rowsToExpand=100',
                        help='http://catalog-dev.smartcasttv.com/catalogs?rowsToExpand=100')

    args = parser.parse_args()
    return args.protocol, args.host, args.uri, args.qs, args.url
if __name__ == '__main__':
    catalog_id, catalog_title, row_list = Catalog().run_cat_rows()
    catalog_id, catalog_title, rows = Catalog().run_cat_home_iids(row_index=0)
    catalog_id, catalog_title, rows = Catalog().run_cat_home_iids(row_index=1)
    dict1 = Catalog().run_cat_home_row_item(row_index=0, item_index=0) # item_index = 0 not found?
