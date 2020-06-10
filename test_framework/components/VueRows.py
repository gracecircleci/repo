from components.catalog import CatalogEnum, Const
from test.test_catalog import TestEnvDefault, CatalogCommon
from components.VueItemDetails import VueSvcTestUtil



class VueSvcRows(object):
    def __init__(self, theJson):
        self.theRowJson = theJson

    def getId(self):
        return self.theRowJson['Vibe']['Iid']

    def getTitle(self):
        return self.theRowJson['Frame']['Data']['Title']

    def getItems(self):
        iid_list = []
        items =  self.theRowJson['Frame']['Data']['SummaryItems']
        for one in items:
            item_id = one['Vibe']['Root']['Iid']
            iid_list.append(item_id)
        return iid_list

    def getItemsLength(self):
        length = len(self.getItems())
        return length

    def __repr__(self):
        str1 = 'id=%s, Title=%s, Items=%s, ItemLength=%s' % (
            self.getId(),
            self.getTitle(),
            self.getItems(),
            self.getItemsLength()
        )
        return str1

class VueSvcRowUtil(object):
    @staticmethod
    def getRowItemByIndex(jsonobj_list, pos=0):
        json1 = jsonobj_list[pos]
        iid = json1['Vibe']['Iid']
        return json1, iid

    @staticmethod
    def getRowItemByIid(jsonobj, iid=1300):
        assert jsonobj is not None
        json_list = jsonobj['Value'][0]['Frame']['Data']['Items']
        for pos in range(len(json_list)):
            json, the_iid = VueSvcRowUtil.getRowItemByIndex(json_list, pos)
            if the_iid == iid:
                return json
        return None



if __name__ == '__main__':
    vue_url = CatalogCommon.VUE_SERVICE_URL
    catalogId = CatalogEnum.HOME.value
    jsonstr, vue_jsonObj = VueSvcTestUtil.startUp(url=vue_url, catalogId=catalogId)
    for theiid in [1300, 1301]:
        json = VueSvcRowUtil.getRowItemByIid(vue_jsonObj, iid=theiid)
        vue_row = VueSvcRows(json)
        print('getTitle:',vue_row.getTitle(), ' Id=', vue_row.getId())
        print('getItemsLength=', vue_row.getItemsLength())
        print('items=', vue_row.getItems())
        print('catrow=', str(vue_row))