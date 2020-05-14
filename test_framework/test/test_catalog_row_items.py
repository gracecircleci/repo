import unittest
import json, sys
import logging
from components.catalog import CatalogEnum, Const
from components.catalog import Catalog
from components.home_tab import HomeTab
from components.vue_row_item_details import VueRowItemDetails
from util.urlutils import EzUtil
from test.test_catalog import CatalogCommon

CATALOG_URL = 'http://catalog-dev.smartcasttv.com/catalogs?rowsToExpand=100'
VUE_SERVICE_URL = 'http://api-stage.vizio.com/api/1.0.1.0/vibes/getdata.aspx?contextToken=-901682349:629546385057943552:508:5234744:5067736:2029148903&handles=[{"Vibe":{"Sid":3020009,"Iid":1,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE='

class CatalogRowItemTest(unittest.TestCase):
    def getJsonObjs(self):
        vueObj = VueRowItemDetails()
        catObj = Catalog()
        _, vueJsonObj = vueObj.getJsonFromUrl(url=VUE_SERVICE_URL)
        _, _, catJsonObj = catObj.getCatalogJsonObjFromUrl(url=CATALOG_URL)
        return vueObj, vueJsonObj, catObj, catJsonObj

    def getCommonIids(self, catObj, vueObj, catJsonObj, vueJsonObj):
        the_row_index = 0
        catalog_id, catalog_row_title, catalog_row_iids = catObj.getRowDetailsByIndex(
            catJsonObj, row_index=the_row_index)
        _,_, vue_iid_list = vueObj.getFirstRowFromVueService(vueJsonObj, items_pos= 0, item_id=1300, the_vid=92)
        the_common_iids = (set(catalog_row_iids) & set(vue_iid_list))
        print('===>>> catalog_row_iids=%s, vue_iids=%s the_common_iids=%s' %
              (catalog_row_iids, vue_iid_list, the_common_iids))
        return catalog_row_iids, vue_iid_list, the_common_iids

    def getCommondIidPosition(self, catalog_row_iids, vue_iid_list, the_common_iids, the_index):
        self.assertTrue( (the_index >= 0) and (the_index < len(the_common_iids)), 'Error: the_index is out of range' )
        commonIid = list(the_common_iids)[the_index]
        vuePos = vue_iid_list.index(commonIid)
        catPos = catalog_row_iids.index(commonIid)
        return commonIid, vuePos, catPos

    def getComparisonStuff(self, vueObj, catObj, vueJsonObj, catJsonObj, commonIid, vuePos, catPos):
        # get Vue stuff
        vdict = vueObj.gather_item_details(
            vueJsonObj,the_vid=92, items_pos=0, iids_index=vuePos)

        # get Catalog Stuff
        cdict = catObj.getRowItemDetails(catJsonObj, row_index=0, iid_idx=catPos)

        print('vueSubTitle=%s, catSubTitle=%s' % (vdict['subtitle'], cdict['subtitle']))
        return commonIid, vdict, cdict

    def getBothDetailsbyIndex(self, index=0):
        vueObj, vueJsonObj, catObj, catJsonObj = self.getJsonObjs()
        catalog_row_iids, vue_iid_list, the_common_iids = self.getCommonIids(catObj, vueObj, catJsonObj, vueJsonObj)
        print('the_common_iids=', the_common_iids)

        commonIid, vuePos, catPos = self.getCommondIidPosition(catalog_row_iids, vue_iid_list, the_common_iids, the_index=index)
        commonIid, vdict, cdict = self.getComparisonStuff(vueObj, catObj, vueJsonObj, catJsonObj, commonIid, vuePos, catPos)
        return commonIid, vdict, cdict, the_common_iids

    def test_common_item_details_subtitle_item(self, index=0):
        commonIid, vdict, cdict, common_iids = self.getBothDetailsbyIndex(index=0)
        self.assertTrue(commonIid is not None, 'There is NO commonIid from VueService and CatalogService ')
        vsubtitle =  vdict['subtitle']
        csubtitle = ''.join(x for x in cdict['subtitle'].values())
        self.assertEqual(vsubtitle, csubtitle, \
                 'SubTitles not match: iid=%s, vueSubTitle=%s, catSubTitle=%s' % (commonIid, vsubtitle, csubtitle))

    def test_common_item_details_subtitle_item1(self, index=1):
        commonIid, vdict, cdict, common_iids = self.getBothDetailsbyIndex(index=1)
        self.assertFalse(len(common_iids)<=1, 'Error: len(common_iids)<=1')
        vsubtitle =  vdict['subtitle']
        csubtitle = ''.join(x for x in cdict['subtitle'].values())
        self.assertEqual(vsubtitle, csubtitle, \
                 'SubTitles not match: iid=%s, vueSubTitle=%s, catSubTitle=%s' % (commonIid, vsubtitle, csubtitle))


if __name__ == '__main__':
    unittest.main()
