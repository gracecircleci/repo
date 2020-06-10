import json
import pandas as pd
from components.catalog import CatalogEnum, Const
from test.test_catalog import TestEnvDefault, CatalogCommon
from components.catalogItemDetails import CatalogSvcTestUtil


class CatSvcRows(object):
    def __init__(self, theJson):
        self.theRowJson = theJson

    def getId(self):
        return self.theRowJson['id']

    def getTitle(self): # example: 'New Hero -2019'
        return self.theRowJson['title']

    def getItems(self):
        return self.theRowJson['items']

    def getItemsLength(self):
        return len(self.theRowJson['items'])


    def __repr__(self):
        str1 = 'Iid=%s, Title=%s, Items=%s, ItemLength=%s' % (
            self.getId(),
            self.getTitle(),
            self.getItems(),
            self.getItemsLength()
        )
        return str1



class CatalogSvcRowUtil(object):
    @staticmethod
    def getRowItemByIid(jsonobj, iid):
        assert jsonobj is not None
        dfColIndex = None
        df = pd.DataFrame(data=jsonobj['rows'], index=None, columns=dfColIndex)
        target_df = df.loc[df['id'] == iid]
        target_json_str = target_df.to_json(orient='records')
        target_json = json.loads(target_json_str)
        return target_json[0]


if __name__ == '__main__':
    cat_url = CatalogCommon.CATALOG_URL
    catalogId = CatalogEnum.HOME.value
    cat_url, cat_jsonObj = CatalogSvcTestUtil.startUp(url=cat_url, catalogId=catalogId)
    json = CatalogSvcRowUtil.getRowItemByIid(cat_jsonObj, 1300)
    catrow = CatSvcRows(json)
    print('getTitle:',catrow.getTitle())
    print('catrow=', catrow)