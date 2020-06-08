import urllib.request
import json
from components.catalog import CatalogEnum, Const
from components.home_tab import HomeTab
from test.test_catalog import TestEnvDefault, CatalogCommon




class VueSvcItemDetails(object):
    def __init__(self, itemDetailsJson):
        self.itemDetailsJson = itemDetailsJson

    def getIid(self):
        if 'Iid' in self.itemDetailsJson['Vibe']['Root']:
            return self.itemDetailsJson['Vibe']['Root']['Iid']
        else:
            return None
    def getTitle(self):
        if 'Title' in self.itemDetailsJson['Frame']['Data']:
            return self.itemDetailsJson['Frame']['Data']['Title']
        else:
            return ""

    def getSubTitles(self):
        if 'SubTitles' in self.itemDetailsJson['Frame']['Data']:
          return self.itemDetailsJson['Frame']['Data']['SubTitles'][0]
        else:
            return None

    def getMetadata(self):
        if 'Metadata' in self.itemDetailsJson['Frame']['Data']:
            return self.itemDetailsJson['Frame']['Data']['Metadata']
        else:
            return None

    def getExpires(self):
        exist = True if self.itemDetailsJson['Frame']['Expires'] else False
        return exist

    def getImage(self):
        if 'BigScreenPlayInfo' in self.itemDetailsJson['Frame']['Data'] and \
          'IMAGE_HANDLE' in self.itemDetailsJson['Frame']['Data']['BigScreenPlayInfo'] and \
          'Iid' in self.itemDetailsJson['Frame']['Data']['BigScreenPlayInfo']['IMAGE_HANDLE']['VibeHandle']:
            iid_str = self.itemDetailsJson['Frame']['Data']['BigScreenPlayInfo']['IMAGE_HANDLE']['VibeHandle']['Iid']
            print('type(iid)=', type(iid_str))
            print(iid_str)
            return iid_str

        elif 'ImageId' in self.itemDetailsJson['Frame']['Data']['ImageHandles'][0]:
            return self.itemDetailsJson['Frame']['Data']['ImageHandles'][0]['ImageId']
        else:
            return None

    def __repr__(self):
        str1 = 'Iid=%s, Title:%s, SubTitles:%s, Expires=%s, Image=%s, \nmetadata=%s' % (
            self.getIid(),
            self.getTitle(), self.getSubTitles(), self.getExpires(),
            self.getImage(), self.getMetadata()
        )
        return str1


class VueSvcTestUtil(object):
    @staticmethod
    def startUp(url=CatalogCommon.VUE_SERVICE_URL, catalogId=CatalogEnum.HOME.value):

        response = urllib.request.urlopen(url)
        assert response.status == 200
        json_str = response.read().decode('utf-8')

        vue = HomeTab()
        url, jsonObj = vue.getJsonFromHomeUrl(url=url, catalogId=catalogId)

        return json_str, jsonObj

    @staticmethod
    def getPageRows(jsonObj)->list:
        # example: [1300, 1301, 9, 1517 ]
        page_rows_of_dict = []
        host = jsonObj['Host']
        value0= jsonObj['Value'][0]
        page_rows = value0['Frame']['Data']['Items']
        iids = [ row['Vibe']['Iid'] for row in page_rows]

        return page_rows, iids # iids [1300, 1301, 9, 1537, 1517, 1610]

    @staticmethod
    def getIidsInOneRowByIndex(jsonobj, pos=0) -> list:
        row_items = jsonobj['Value'][0]['Frame']['Data']['Items'][pos]['Frame']['Data']['SummaryItems']
        iids_in_row = []
        for one_item in row_items:
            iids_in_row.append(one_item['Vibe']['Root']['Iid'])
        return iids_in_row  # example: [29730, 29731, 29866]

    @staticmethod
    def getIidsInOneRowByIid(jsonobj, page_iids=None, target_iid=1300) -> list:
        pos = page_iids.index(target_iid)
        row_items = jsonobj['Value'][0]['Frame']['Data']['Items'][pos]['Frame']['Data']['SummaryItems']
        iids_in_row = []
        for one_item in row_items:
            iids_in_row.append(one_item['Vibe']['Root']['Iid'])
        return iids_in_row

    @staticmethod
    def getItemDetailsByIndex(jsonobj, page_rows_iid=None, the_row_iid=None, item_pos=0)-> json:
        assert page_rows_iid is not None
        pos = page_rows_iid.index(the_row_iid)

        item_details = jsonobj['Value'][0]['Frame']['Data']['Items'][pos]['Frame']['Data']['SummaryItems'][item_pos]
        return item_details

    @staticmethod
    def getItemDetalsByIid(jsonobj,  target_row_iid=None, target_item_iid=None)-> json:
        assert target_row_iid is not None
        assert target_item_iid is not None

        page_rows, page_iids = VueSvcTestUtil.getPageRows(jsonobj)
        pos = page_iids.index(target_row_iid)
        iids_in_one_row = VueSvcTestUtil.getIidsInOneRowByIid(jsonobj, page_iids, target_row_iid)
        item_pos = iids_in_one_row.index(target_item_iid)

        item_details = jsonobj['Value'][0]['Frame']['Data']['Items'][pos]['Frame']['Data']['SummaryItems'][item_pos]
        return item_details
