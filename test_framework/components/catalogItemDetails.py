import json, os.path
from urllib.parse import unquote, quote, urlparse
import pandas as pd
from components.catalog import CatalogEnum, Const
from components.catalog import Catalog
from test.test_catalog import TestEnvDefault, CatalogCommon
from urllib.parse import unquote, quote


class CatSvcItemDetails(object):
    def __init__(self, itemDetailsJson):
        self.itemDetailsJson = itemDetailsJson

    def getIid(self):
        return self.itemDetailsJson['id']

    def getTitle(self):
        return self.itemDetailsJson['title']

    def getSubTitles(self):
        return self.itemDetailsJson['subTitle']

    def getExpires(self):
        return True if "expiresMsSinceEpoch" in self.itemDetailsJson else False

    def getImage(self):
        iid = self.itemDetailsJson['id']
        if self.itemDetailsJson['badgePath'] and len(self.itemDetailsJson['badgePath']) >  5:
            unquoted_badgePathUrl = unquote(self.itemDetailsJson['badgePath'])
            querystr = urlparse(unquoted_badgePathUrl).query
            str1 = querystr.split('=')[1].split('&')[0]  # '{"Sid":1034,"Iid":1000004,"_tid":18}'
            sid_iid_json = json.loads(str1)
            image_iid = sid_iid_json['Iid']
            print(image_iid)
            return image_iid
        elif self.itemDetailsJson['imagePath']:
            imagePathTokens = self.itemDetailsJson['imagePath'].split('/')
            print('imagePathTokens[4]', imagePathTokens[4])
            return imagePathTokens[4]
        else:
            print('We should not get here')
            return None

    def getMetadata(self):
        return self.itemDetailsJson['metadata']


    def __repr__(self):
        str1 = 'Iid=%s, Title:%s, SubTitles:%s, Expires=%s, Image=%s, \nmetadata=%s' % (
            self.getIid(),
            self.getTitle(), self.getSubTitles(), self.getExpires(),
            self.getImage(), self.getMetadata()
        )
        return str1

class CatalogRows(object):
    def __init__(self, theJson):
        self.theJson = theJson

    def getRowsOnPage(self):
        pass

class CatalogSvcTestUtil(object):
    @staticmethod
    def startUp(url=CatalogCommon.CATALOG_URL, catalogId=CatalogEnum.MOVIES.value):
        cat = Catalog()
        cat_url, jsonObj = Catalog().getJsonFromCatalogUrl(catalogId=catalogId, url=url) #catalogId for the http header
        return cat_url, jsonObj

    @staticmethod
    def getPageRows(jsonObj)->list:
        # example: [1300, 1301, 9, 1517 ]
        iids = []
        host = jsonObj['hostName']
        page_rows = jsonObj['rows']
        for i in range(len(page_rows)):
            iids.append(page_rows[i]['id'])

        return page_rows, iids # iids [1300, 1301, 9, 1537, 1517, 1610]

    @staticmethod
    def getIidsInOneRowByIndex(jsonobj, pos=0) -> list:
        row_items = jsonobj['rows']
        row_iids = jsonobj['rows'][pos]['items']
        row_title = jsonobj['rows'][pos]['title']
        expires = jsonobj['rows'][pos]['expiresMsSinceEpoch']
        return row_iids, row_title, expires

    @staticmethod
    def getIidsInOneRowByIid(jsonobj, page_iids=None, target_iid=1300) -> list:
        pos = page_iids.index(target_iid)
        row_iids = jsonobj['rows'][pos]['items']
        row_title = jsonobj['rows'][pos]['title']
        expires = jsonobj['rows'][pos]['expiresMsSinceEpoch']
        return row_iids

    @staticmethod
    def getItemDetailsByIndex(jsonobj, item_pos=0)-> json:
        item_details = jsonobj['items'][item_pos]
        return item_details

    @staticmethod
    def getItemIdsOnPage(jsonobj):
        item_ids_on_page = []
        for item in jsonobj['items']:
            item_ids_on_page.append(item['id'])
        return item_ids_on_page

    @staticmethod
    def getItemDetailsByIid(jsonobj, target_item_iid)-> json:
        assert target_item_iid is not None
        dfColIndex = None #['id', 'title', 'subTitle', 'action']
        df = pd.DataFrame(data=jsonobj['items'], index=None, columns=dfColIndex)
        target_df = df.loc[ df['id'] == target_item_iid]
        target_json_str = target_df.to_json(orient='records')
        target_json = json.loads(target_json_str)
        return target_json[0]
