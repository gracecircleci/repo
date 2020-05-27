from pyunitreport import HTMLTestRunner
import unittest
import json, sys
import logging
from components.catalog import CatalogEnum, Const
from components.catalog import Catalog
from components.home_tab import HomeTab
from util.urlutils import EzUtil

class TestEnvDefault:
    CATALOG_ID = CatalogEnum.HOME.value
    CATALOG_HOST = 'catalog-dev.smartcasttv.com'
    VUE_HOST = 'api-stage.vizio.com'
    VUE_QS = 'contextToken=-901682349:629546385057943552:508:5234744:5067736:2029148903&handles=[{"Vibe":{"Sid":3020009,"Iid":%d,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE='

class CatalogCommon(object):
    CATALOG_ID = CatalogEnum.HOME.value
    CATALOG_HOST = TestEnvDefault.CATALOG_HOST
    VUE_HOST = TestEnvDefault.VUE_HOST
    VUE_QS = TestEnvDefault.VUE_QS % CATALOG_ID
    CATALOG_URL = 'http://%s/catalogs?rowsToExpand=100' % CATALOG_HOST
    VUE_SERVICE_URL = 'http://%s/api/1.0.1.0/vibes/getdata.aspx?contextToken=-901682349:629546385057943552:508:5234744:5067736:2029148903&handles=[{"Vibe":{"Sid":3020009,"Iid":%d,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE=' % (VUE_HOST,CatalogEnum.HOME.value)
    VUE_SERVICE_SHOW_URL = 'http://%s/api/1.0.1.0/vibes/getdata.aspx?contextToken=-901682349:629546385057943552:508:5234744:5067736:2029148903&handles=[{"Vibe":{"Sid":3020009,"Iid":%d,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE=' % (VUE_HOST,CatalogEnum.SHOWS.value)
    VUE_SERVICE_MOVIE_URL = 'http://%s/api/1.0.1.0/vibes/getdata.aspx?contextToken=-901682349:629546385057943552:508:5234744:5067736:2029148903&handles=[{"Vibe":{"Sid":3020009,"Iid":%d,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE=' % (VUE_HOST,CatalogEnum.MOVIES.value)


    @staticmethod
    def catalog_rows(host=VUE_HOST,catalogId=CatalogEnum.HOME.value):
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
        catalog_id, catalog_title, catalog_rows = None, None, None
        vue_title, vue_rows = None, None
        catalog_id, catalog_title, catalog_rows = Catalog().run_cat_rows(catalogId=catalogId)
        vue_title, vue_rows = HomeTab().runVueServiceRowsIid(host=host,catalogId=catalogId)
        print('catalog_id=%s, catalog_title=%s, catalog_rows=%s' % (catalog_id, catalog_title, catalog_rows))
        print('vue_title=%s, vue_rows=%s' % (vue_title, vue_rows))
        return catalog_title, catalog_rows, vue_title, vue_rows

    @staticmethod
    def home_row_iids(cat_url=CATALOG_URL, vue_url=VUE_SERVICE_URL,
                    catalogId=CatalogEnum.HOME.value, the_row_index=0, iid=1300, the_vid=92):
        catalog_id, catalog_row_title, catalog_row_iids = None,None,None
        cat = Catalog()
        status, url, jsonobj = cat.getCatalogJsonObjFromUrl(url=cat_url,catalogId=catalogId)
        catalog_id, catalog_row_title, catalog_row_iids = cat.getRowDetailsByIndex(
            jsonobj, row_index=the_row_index)

        # access Vue service
        homeObj = HomeTab()
        vue_url, vueJsonObj = homeObj.getJsonFromHomeUrl(url=vue_url, catalogId=catalogId)
        vue_title, vue_item_title, vue_iid_list = homeObj.getFirstRowFromVueService(
            vueJsonObj, items_pos=the_row_index, item_id=iid, the_vid=the_vid)
        return catalog_row_title, catalog_row_iids, vue_item_title, vue_iid_list

    @staticmethod
    def row_iid_title(cat_url=CATALOG_URL, vue_url=VUE_SERVICE_URL,
                    catalogId=CatalogEnum.HOME.value, iid=1300):
        cat = Catalog()
        status, url, jsonobj = cat.getCatalogJsonObjFromUrl(url=cat_url,catalogId=catalogId)
        catalog_id, catalog_row_title = cat.getRowItemDetailsByIid(
            catJsonObj=jsonobj, iid=iid)
        iid_title_dict, cat_row_count = cat.getCatalogRowsCount(catJsonObj=jsonobj, catalogId=catalogId)

        # access Vue service
        homeObj = HomeTab()
        vue_url, vueJsonObj = homeObj.getJsonFromHomeUrl(url=vue_url, catalogId=catalogId)
        catalog_name, vue_row_title, iid, sid, vue_row_count = homeObj.runVueServiceRowTitleByIid(
            catalogId=catalogId, iid=iid)

        return catalog_row_title, vue_row_title, iid,  cat_row_count, vue_row_count

    @staticmethod
    def common_iids(cat_url=CATALOG_URL, vue_url=VUE_SERVICE_URL,catalogId=CatalogEnum.HOME.value, the_row_index=0, iid=1300, the_vid=92):
        cat = Catalog()
        status, url, catJsonObj = cat.getCatalogJsonObjFromUrl(url=cat_url, catalogId=catalogId)
        homeObj = HomeTab()
        vue_url, vueJsonObj = homeObj.getJsonFromHomeUrl(vue_url=vue_url, catalogId=catalogId)

        catalog_row_title, catalog_row_iids, vue_item_title, vue_iid_list = CatalogCommon.home_row_iids(
            cat_url=cat_url, vue_url=vue_url,
            catalogId=catalogId,
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


    def test_home_title_1300(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_URL,
            catalogId=CatalogEnum.HOME.value, iid=1300)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_home_rowcount(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count  = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_URL,
            catalogId=CatalogEnum.HOME.value, iid=1300)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('%s: catalogService cat_row_count=%s, vue_row_count=%s' % (CatalogEnum(CatalogEnum.HOME.value), cat_row_count, vue_row_count))
        self.assertEqual(cat_row_count, vue_row_count,
                         '\n Diffs ==>> catalog_row_count=%s, vue_row_count=%s' % (cat_row_count, vue_row_count))

    # HERE HERE
    def xtest_shows_row_count(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count  = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1305)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('%s: catalogService cat_row_count=%s, vue_row_count=%s' % (CatalogEnum(CatalogEnum.SHOWS.value), cat_row_count, vue_row_count))
        self.assertEqual(cat_row_count, vue_row_count,
                         '\n Diffs ==>> catalog_row_count=%s, vue_row_count=%s' % (cat_row_count, vue_row_count))

    def xtest_movies_row_count(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count  = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_URL,
            catalogId=CatalogEnum.MOVIES.value, iid=1304)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('%s: catalogService cat_row_count=%s, vue_row_count=%s' % (CatalogEnum(CatalogEnum.MOVIES.value), cat_row_count, vue_row_count))
        self.assertEqual(cat_row_count, vue_row_count,
                         '\n Diffs ==>> catalog_row_count=%s, vue_row_count=%s' % (cat_row_count, vue_row_count))

    def test_home_title_1301(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_URL,
            catalogId=CatalogEnum.HOME.value, iid=1301)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_home_title_9(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_URL,
            catalogId=CatalogEnum.HOME.value, iid=9)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def xtest_home_title_1537(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_URL,
            catalogId=CatalogEnum.HOME.value, iid=1537)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def xtest_home_title_1297(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_URL,
            catalogId=CatalogEnum.HOME.value, iid=1297)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def xtest_home_title_1606(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_URL,
            catalogId=CatalogEnum.HOME.value, iid=1606)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))
    

    def xtest_home_rows(self):
        _, catalog_rows, _, vue_rows = CatalogCommon.catalog_rows(
            host=CatalogCommon.VUE_HOST,catalogId=CatalogEnum.HOME.value)
        self.assertEqual(catalog_rows, vue_rows ,
          '\n catalog_rows=%s. vue_rows=%s' % (catalog_rows, vue_rows ))

    
    def test_catalog_home_row_1300_title(self):
        catalog_row_title, catalog_row_iids, vue_item_title, vue_iid_list = CatalogCommon.home_row_iids(the_row_index=0, iid=1300, the_vid=92)
        # compare catalog and vue service
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_item_title))
        self.assertEqual(catalog_row_title, vue_item_title,
           '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_item_title))


    def test_catalog_home_row_1301_title(self):
        catalog_row_title, catalog_row_iids, vue_item_title, vue_iid_list = CatalogCommon.home_row_iids(the_row_index=1, iid=1301, the_vid=2000013)
        # compare catalog and vue service
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('catalog_title = % s, vue_item_title = % s' % (catalog_row_title, vue_item_title))
        self.assertEqual(catalog_row_title, vue_item_title,
           '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_item_title))

    def test_catalog_home_row_9_title(self):
        catalog_row_title, catalog_row_iids, vue_item_title, vue_iid_list = CatalogCommon.home_row_iids(the_row_index=2, iid=9, the_vid=2000015)
        # compare catalog and vue service
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('catalog_title = % s, vue_item_title = % s' % (catalog_row_title, vue_item_title))
        self.assertEqual(catalog_row_title, vue_item_title,
           '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_item_title))

    def test_catalog_home_row_1537_title(self):
        catalog_row_title, catalog_row_iids, vue_item_title, vue_iid_list = CatalogCommon.home_row_iids(the_row_index=3, iid=1537, the_vid=2000010)
        # compare catalog and vue service
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_item_title))
        self.assertEqual(catalog_row_title, vue_item_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_item_title))

    def test_catalog_home_row_1300_length(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids(
            catalogId=CatalogCommon.CATALOG_ID,the_row_index=0, iid=1300, the_vid=92)
        extra_in_catalog = set(catalog_row_iids)- set(vue_iid_list)
        extra_in_vue = set(vue_iid_list) - set(catalog_row_iids)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue))
        self.assertEqual(len(catalog_row_iids), len(vue_iid_list),
                         'only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue) )

    def test_catalog_home_row_1301_length(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids(
            catalogId=CatalogCommon.CATALOG_ID,the_row_index=1, iid=1301, the_vid=2000013)
        extra_in_catalog = set(catalog_row_iids)- set(vue_iid_list)
        extra_in_vue = set(vue_iid_list) - set(catalog_row_iids)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue))
        self.assertEqual(len(catalog_row_iids), len(vue_iid_list),
                         'only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue) )

    def test_catalog_shows_row_1251_length(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids(
            cat_url=CatalogCommon.CATALOG_URL, vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value,the_row_index=1, iid=1251, the_vid=2000010)
        extra_in_catalog = set(catalog_row_iids)- set(vue_iid_list)
        extra_in_vue = set(vue_iid_list) - set(catalog_row_iids)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('catalog_row_iids=%s\n    vue_iid_list=%s', (catalog_row_iids, vue_iid_list))
        print('only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue))
        self.assertEqual(len(catalog_row_iids), len(vue_iid_list),
                         'only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue) )

    #@unittest.skip('Skip this test')
    def test_catalog_home_row_9_length(self):
        catalog_row_title, catalog_row_iids, vue_item_title, vue_iid_list = CatalogCommon.home_row_iids(
            catalogId=CatalogCommon.CATALOG_ID,the_row_index=2, iid=9, the_vid=2000015)
        extra_in_catalog = set(catalog_row_iids)- set(vue_iid_list)
        extra_in_vue = set(vue_iid_list) - set(catalog_row_iids)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('catalog_row_iids=%s\n    vue_iid_list=%s', (catalog_row_iids, vue_iid_list))
        print('only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue))
        self.assertEqual(len(catalog_row_iids), len(vue_iid_list),
                         'only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s. iids_in_common=%s' % (extra_in_catalog, extra_in_vue, (set(catalog_row_iids) & set(vue_iid_list))) )

    def test_catalog_home_row_1537_length(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids(catalogId=CatalogCommon.CATALOG_ID,the_row_index=3, iid=1537, the_vid=2000010)
        extra_in_catalog = set(catalog_row_iids)- set(vue_iid_list)
        extra_in_vue = set(vue_iid_list) - set(catalog_row_iids)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('catalog_row_iids=%s\n    vue_iid_list=%s', (catalog_row_iids, vue_iid_list))
        print('only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue))
        self.assertEqual(len(catalog_row_iids), len(vue_iid_list),
                         'only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue) )

    def test_catalog_home_row_iids_random_drafting(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids()
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('catalog_row_iids=%s, vue_iid_list=%s' % (catalog_row_iids, vue_iid_list))
        self.assertEqual(len(catalog_row_iids), len(vue_iid_list),
           '\n Diffs ==>> catalog_row_iids=%s, vue_iid_list=%s' % (catalog_row_iids, vue_iid_list))

    def xxtest_catalog_home_row_iids(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids()
        self.assertEqual(catalog_row_iids, vue_iid_list,
           '\n Diffs ==>> catalog_row_iids=%s, vue_iid_list=%s' % (catalog_row_iids, vue_iid_list))

    # Shows
    #
    def test_catalog_shows_title(self):
        catalog_title, vue_title = None, None
        catID = CatalogEnum.SHOWS.value
        catalog_title, catalog_rows, vue_title, vue_rows = CatalogCommon.catalog_rows(
            host=CatalogCommon.VUE_HOST,catalogId=catID)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('%s: catalog_title=%s, vue_title=%s' % (CatalogEnum(catID), catalog_title, vue_title))
        self.assertEqual(catalog_title, vue_title,
                         '\n Diffs ==>> catalog_title=%s, vue_title=%s' % (catalog_title, vue_title))

    def test_catalog_shows_rowcount(self):
        _, catalog_rows, _, vue_rows = CatalogCommon.catalog_rows(host=CatalogCommon.VUE_HOST,catalogId=CatalogEnum.SHOWS.value)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('catalog_rows=%s. vue_rows=%s' % (catalog_rows, vue_rows ))
        self.assertEqual(catalog_rows, vue_rows ,
          '\n Diffs ==>> catalog_rows=%s. vue_rows=%s' % (catalog_rows, vue_rows ))

    def test_shows_row_1305_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1305)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))
    def test_shows_row_1443_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_len,vue_row_len = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1443)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))
    def test_shows_row_1605_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1605)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_shows_row_1296_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1296)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))


    def test_shows_row_1472_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1472)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_shows_row_1201_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1201)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_shows_row_1203_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1203)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_shows_row_1090_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1090)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_shows_row_1126_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1126)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_shows_row_1474_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1474)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_shows_row_1089_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1089)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_shows_row_1545_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1545)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_shows_row_1438_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1438)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_shows_row_1588_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1588)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_shows_row_1448_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1448)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_shows_row_1216_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1216)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_shows_rows_1099_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value, iid=1099)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_catalog_shows_row_length(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids(
            cat_url=CatalogCommon.CATALOG_URL, vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value,the_row_index=0, iid=1305, the_vid=92)
        extra_in_catalog = set(catalog_row_iids)- set(vue_iid_list)
        extra_in_vue = set(vue_iid_list) - set(catalog_row_iids)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('catalog_row_iids=%s, vue_iid_list=%s' % (catalog_row_iids, vue_iid_list))
        print('only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue))
        self.assertEqual(len(catalog_row_iids), len(vue_iid_list),
                         'only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue) )
        self.assertEqual(len(catalog_row_iids), len(vue_iid_list))

    def test_catalog_shows_row_1251_length(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids(
            cat_url=CatalogCommon.CATALOG_URL, vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value,the_row_index=1, iid=1251, the_vid=2000010)
        extra_in_catalog = set(catalog_row_iids)- set(vue_iid_list)
        extra_in_vue = set(vue_iid_list) - set(catalog_row_iids)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('catalog_row_iids=%s, vue_iid_list=%s' % (catalog_row_iids, vue_iid_list))
        print('only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue))
        self.assertEqual(len(catalog_row_iids), len(vue_iid_list),
                         'only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue) )

    def xtest_catalog_shows_row_two_length(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids(
            cat_url=CatalogCommon.CATALOG_URL, vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value,the_row_index=2, iid=1443, the_vid=2000009)
        extra_in_catalog = set(catalog_row_iids)- set(vue_iid_list)
        extra_in_vue = set(vue_iid_list) - set(catalog_row_iids)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('catalog_row_iids=%s, vue_iid_list=%s' % (catalog_row_iids, vue_iid_list))
        print('only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue))
        self.assertEqual(len(catalog_row_iids), len(vue_iid_list),
                         'only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue) )
    def xtest_catalog_shows_row_three_length(self):
        _, catalog_row_iids, _, vue_iid_list = CatalogCommon.home_row_iids(
            cat_url=CatalogCommon.CATALOG_URL, vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
            catalogId=CatalogEnum.SHOWS.value,the_row_index=3, iid=1605, the_vid=2000006)
        extra_in_catalog = set(catalog_row_iids)- set(vue_iid_list)
        extra_in_vue = set(vue_iid_list) - set(catalog_row_iids)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('catalog_row_iids=%s, vue_iid_list=%s' % (catalog_row_iids, vue_iid_list))
        print('only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue))
        self.assertEqual(len(catalog_row_iids), len(vue_iid_list),
                         'only_in_catalog_iid_list=%s, only_in_vue_iid_list=%s' % (extra_in_catalog, extra_in_vue) )

    # Movies
    def test_catalog_movies_title(self):
        catalog_title, vue_title = None, None
        catID = CatalogEnum.MOVIES.value
        catalog_title, catalog_rows, vue_title, vue_rows = CatalogCommon.catalog_rows(
            host=CatalogCommon.VUE_HOST,catalogId=catID)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('catalog_title=%s, vue_title=%s' % (catalog_title, vue_title))
        self.assertEqual(catalog_title, vue_title,
                         '\n Diffs ==>> catalog_title=%s, vue_title=%s' % (catalog_title, vue_title))

    def test_movie_row_1304_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_MOVIE_URL,
            catalogId=CatalogEnum.MOVIES.value, iid=1304)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))

    def test_movie_row_1594_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_MOVIE_URL,
            catalogId=CatalogEnum.MOVIES.value, iid=1594)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))
    def test_movie_row_1098_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_MOVIE_URL,
            catalogId=CatalogEnum.MOVIES.value, iid=1098)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))
    def test_movie_row_1125_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_MOVIE_URL,
            catalogId=CatalogEnum.MOVIES.value, iid=1125)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))
    def xtest_movie_row_1608_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_MOVIE_URL,
            catalogId=CatalogEnum.MOVIES.value, iid=1608)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))
    def test_movie_row_1078_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_MOVIE_URL,
            catalogId=CatalogEnum.MOVIES.value, iid=1078)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))
    def test_movie_row_1085_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_MOVIE_URL,
            catalogId=CatalogEnum.MOVIES.value, iid=1085)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))
    def test_movie_row_1084_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_MOVIE_URL,
            catalogId=CatalogEnum.MOVIES.value, iid=1084)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))
    def test_movie_row_1082_title(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_MOVIE_URL,
            catalogId=CatalogEnum.MOVIES.value, iid=1082)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))
    def xtest_movie_title_1211(self):
        catalog_row_title, vue_row_title, iid, cat_row_count, vue_row_count = CatalogCommon.row_iid_title(
            cat_url=CatalogCommon.CATALOG_URL,
            vue_url=CatalogCommon.VUE_SERVICE_MOVIE_URL,
            catalogId=CatalogEnum.MOVIES.value, iid=1211)
        print('[%s]' % (sys._getframe().f_code.co_name))
        print('iid=%s, catalogService title=%s, VueService title=%s' % (iid, catalog_row_title, vue_row_title))
        self.assertEqual(catalog_row_title, vue_row_title,
                         '\n Diffs ==>> catalog_title=%s, vue_item_title=%s' % (catalog_row_title, vue_row_title))


if __name__ == '__main__':
    # ToRun: python3 test/test_catalog.py <catalog-host> <vue_host>
    # python3 test/test_catalog.py catalog-dev.smartcasttv.com api-stage.vizio.com
    assert (len(sys.argv) >=3)
    CatalogCommon.CATALOG_HOST = sys.argv[1] if sys.argv[1] else TestEnvDefault.CATALOG_HOST
    CatalogCommon.VUE_HOST = sys.argv[2] if sys.argv[2] else TestEnvDefault.VUE_HOST

    # popping the parameters is a must.
    for i in range(len(sys.argv[1:])):
        sys.argv.pop()
    unittest.main(verbosity=2,
        testRunner=HTMLTestRunner(output='./gtest_results'))

