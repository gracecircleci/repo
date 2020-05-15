import unittest
import xmlrunner
import json, sys
import logging
from components.catalog import CatalogEnum, Const
from components.catalog import Catalog
from components.home_tab import HomeTab
from util.urlutils import EzUtil

xml_str = '''
<?xml version="1.0" encoding="UTF-8"?>
<test_result>
    <test_runs>
        <test_run started="STARTED_TS" status="Skipped" duration="14" name="bandTestA" class="BandTest" package="com.mycomp.devops.demoapp" module="webapp"/>
        <test_run started="STARTED_TS" status="Passed" duration="0" name="bandTestB" class="BandTest" package="com.mycomp.devops.demoapp" module="webapp"/>
        <test_run started="STARTED_TS" status="Passed" duration="1" name="always_true_A" class="CalcsTest" package="com.mycomp.devops.demoapp" module="webapp"/>
        <test_run started="STARTED_TS" status="Passed" duration="1" name="always_true_B" class="CalcsTest" package="com.mycomp.devops.demoapp" module="webapp"/>
        <test_run started="STARTED_TS" status="Passed" duration="1" name="always_true_C" class="CalcsTest" package="com.mycomp.devops.demoapp" module="webapp"/>
    </test_runs>
</test_result>
'''
CATALOG_URL = 'http://catalog-dev.smartcasttv.com/catalogs?rowsToExpand=100'
VUE_SERVICE_URL = 'http://api-stage.vizio.com/api/1.0.1.0/vibes/getdata.aspx?contextToken=-901682349:629546385057943552:508:5234744:5067736:2029148903&handles=[{"Vibe":{"Sid":3020009,"Iid":1,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE='

class CatalogCommon(object):
    @staticmethod
    def catalog_rows():
        '''
        1) http POST request to CatalogService:
         http://catalog-dev.smartcasttv.com/catalogs?rowsToExpand=3
         headersdict = {
            'Content-Type': 'application/json',
            'LanguageIso2Code': 'EN',
            'CountryIso2Code': 'US',
            'ClientDateTimeSeconds': '1588700639',
            'SctvVersion': '5.0.0.0',
            'ModelName': 'E50-F2'
         }
         { "Catalogs":[{ "Id" : <catalogId> }]} # catalogId is passed in. eg. 1


        2) http GET request to VueService:
          url = 'http://api-stage.vizio.com/api/1.0.1.0/vibes/getdata.aspx?
          contextToken=-901682349:629546385057943552:508:5234744:5067736:2029148903&
          handles=[{"Vibe":{"Sid":3020009,"Iid":1,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&
          access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE='

        3) get catalog_title, catalog_rows step 1; get vue_item_title, vue_iid_list.
           call assertEqual to compare the catalog_title and vue_item_title.
           example: 'New Hero - 2019' vs 'New Hero - 2019'
           call assertEqual to compare the catalog_rows and vue_iid_list.
           example: [1300, 1301, 9, 1537] vs [1300, 1301, 9, 1537, 1517]

        '''

        catalog_id, catalog_title, catalog_rows = Catalog().run_cat_rows()
        vue_title, vue_rows = HomeTab().runVueServiceRowsIid()
        return catalog_title, catalog_rows, vue_title, vue_rows

    @staticmethod
    def home_row_iids(the_row_index=0, iid=1300, the_vid=92):
        catalog_id, catalog_row_title, catalog_row_iids = None,None,None
        cat = Catalog()
        status, url, jsonobj = cat.getCatalogJsonObjFromUrl(url=CATALOG_URL)
        catalog_id, catalog_row_title, catalog_row_iids = cat.getRowDetailsByIndex(
            jsonobj, row_index=the_row_index)

        # access Vue service
        homeObj = HomeTab()
        vue_url, vueJsonObj = homeObj.getJsonFromHomeUrl(url=VUE_SERVICE_URL)
        vue_title, vue_item_title, vue_iid_list = homeObj.getFirstRowFromVueService(
            vueJsonObj, items_pos=the_row_index, item_id=iid, the_vid=the_vid)
        return catalog_row_title, catalog_row_iids, vue_item_title, vue_iid_list

    @staticmethod
    def common_iids(the_row_index=0, iid=1300, the_vid=92):
        cat = Catalog()
        status, url, catJsonObj = cat.getCatalogJsonObjFromUrl(url=CATALOG_URL)
        homeObj = HomeTab()
        vue_url, vueJsonObj = homeObj.getJsonFromHomeUrl(url=VUE_SERVICE_URL)

        catalog_row_title, catalog_row_iids, vue_item_title, vue_iid_list = CatalogCommon.home_row_iids(
            the_row_index=0, iid=1300, the_vid=92)
        the_common_iids = (set(catalog_row_iids) & set(vue_iid_list) )
        return catJsonObj, vueJsonObj, the_common_iids

class CatalogTest(unittest.TestCase):
    '''
        1) http POST request to CatalogService:
         http://catalog-dev.smartcasttv.com/catalogs?rowsToExpand=3
         headersdict = {
            'Content-Type': 'application/json',
            'LanguageIso2Code': 'EN',
            'CountryIso2Code': 'US',
            'ClientDateTimeSeconds': '1588700639',
            'SctvVersion': '5.0.0.0',
            'ModelName': 'E50-F2'
         }
         { "Catalogs":[{ "Id" : <catalogId> }]} # catalogId is passed in. eg. 1


        2) http GET request to VueService:
          url = 'http://api-stage.vizio.com/api/1.0.1.0/vibes/getdata.aspx?
          contextToken=-901682349:629546385057943552:508:5234744:5067736:2029148903&
          handles=[{"Vibe":{"Sid":3020009,"Iid":1,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&
          access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE='

        3) get catalog_title, catalog_rows step 1; get vue_item_title, vue_iid_list.
           call assertEqual to compare the catalog_title and vue_item_title.
           example: 'New Hero - 2019' vs 'New Hero - 2019'
           call assertEqual to compare the catalog_rows and vue_iid_list.
           example: [1300, 1301, 9, 1537] vs [1300, 1301, 9, 1537, 1517]

    '''
        
    def test_catalog_row_title(self):
        catalog_title, catalog_rows, vue_title, vue_rows = CatalogCommon.catalog_rows()
        self.assertEquals(catalog_title, vue_title,
          '\n Diffs ==>> catalog_title=%s, vue_title=%s' % (catalog_title, vue_title))
    
    def test_catalog_rows(self):
        _, catalog_rows, _, vue_rows = CatalogCommon.catalog_rows()
        self.assertEqual(catalog_rows, vue_rows ,
          '\n Diffs ==>> catalog_rows=%s. vue_rows=%s' % (catalog_rows, vue_rows ))

    def test_catalog_home_row_title(self):
        catalog_row_title, catalog_row_iids, vue_item_title, vue_iid_list = CatalogCommon.home_row_iids(the_row_index=0, iid=1300, the_vid=92)
        # compare catalog and vue service
        print('Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_item_title))
        self.assertEqual(catalog_row_title, vue_item_title,
           '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_item_title))

    def test_catalog_home_row_one_title(self):
        catalog_row_title, catalog_row_iids, vue_item_title, vue_iid_list = CatalogCommon.home_row_iids(the_row_index=1, iid=1301, the_vid=2000013)
        # compare catalog and vue service
        print('Diffs == >> catalog_title = % s, vue_item_title = % s' % (catalog_row_title, vue_item_title))
        self.assertEqual(catalog_row_title, vue_item_title,
           '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_item_title))

    def test_catalog_home_row_two_title(self):
        catalog_row_title, catalog_row_iids, vue_item_title, vue_iid_list = CatalogCommon.home_row_iids(the_row_index=2, iid=9, the_vid=2000015)
        # compare catalog and vue service
        print('Diffs == >> catalog_title = % s, vue_item_title = % s' % (catalog_row_title, vue_item_title))
        self.assertEqual(catalog_row_title, vue_item_title,
           '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_item_title))

    def test_catalog_home_row_three_title(self):
        catalog_row_title, catalog_row_iids, vue_item_title, vue_iid_list = CatalogCommon.home_row_iids(the_row_index=3, iid=1537, the_vid=2000010)
        # compare catalog and vue service
        print('test_catalog_home_row_three_title')
        print('Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_item_title))
        self.assertEqual(catalog_row_title, vue_item_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_item_title))

    def test_catalog_home_row_four_title(self):
        catalog_row_title, catalog_row_iids, vue_item_title, vue_iid_list = CatalogCommon.home_row_iids(the_row_index=4, iid=1517, the_vid=2000009)
        # compare catalog and vue service
        print('Diffs == >> catalog_title = % s, vue_item_title = % s' % (catalog_row_title, vue_item_title))
        self.assertEqual(catalog_row_title, vue_item_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_item_title))

    def test_catalog_home_row_five_title(self):
        catalog_row_title, catalog_row_iids, vue_item_title, vue_iid_list = CatalogCommon.home_row_iids(the_row_index=5, iid=1142)
        print('Diffs == >> catalog_title = % s, vue_item_title = % s' % (catalog_row_title, vue_item_title))
        # compare catalog and vue service
        self.assertEqual(catalog_row_title, vue_item_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_item_title))

    def test_catalog_home_row_length(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids(the_row_index=0, iid=1300, the_vid=92)
        self.assertEqual(len(catalog_row_iids), len(vue_iid_list))

    def test_catalog_home_row_one_length(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids(the_row_index=1, iid=1301, the_vid=2000013)
        self.assertEqual(len(catalog_row_iids), len(vue_iid_list))

    def xtest_catalog_home_row_two_length(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids(the_row_index=2, iid=9, the_vid=2000015)
        self.assertEqual(len(catalog_row_iids), len(vue_iid_list))

    def test_catalog_home_row_three_length(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids(the_row_index=3, iid=1537, the_vid=2000010)
        self.assertEqual(len(catalog_row_iids), len(vue_iid_list))

    def test_catalog_home_row_iids_random_drafting(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids()
        self.assertNotEqual(catalog_row_iids, vue_iid_list, 
           '\n Diffs ==>> catalog_row_iids=%s, vue_iid_list=%s' % (catalog_row_iids, vue_iid_list))

    def xtest_catalog_home_row_iids(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids()
        self.assertEqual(catalog_row_iids, vue_iid_list, 
           '\n Diffs ==>> catalog_row_iids=%s, vue_iid_list=%s' % (catalog_row_iids, vue_iid_list))

if __name__ == '__main__':
  with open('../catalog-results.xml', 'w+') as output:
    unittest.main(
        testRunner = xmlrunner.XMLTestRunner(output=output.decode('utf-8')),
	failfast=False, buffer=False, catchbreak=False)
	
