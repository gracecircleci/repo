import unittest
import os
from pyunitreport import HTMLTestRunner
from components.catalog import CatalogEnum
from components.catalogItemDetails import CatSvcItemDetails, CatalogSvcTestUtil
from components.VueItemDetails import VueSvcItemDetails, VueSvcTestUtil
from test.test_catalog import CatalogCommon
from util.urlutils import EzUtil



class TestSequense(unittest.TestCase):
    pass

def test_generator(testname=None, a=0, b=0):
    def test(self):
        self.assertEqual(a,b, 'TestFailed: test_name=%s, acutal=%s, expected=%s' % (testname, a, b))
    return test


def create_test_list(testlist=[], cat_url=CatalogCommon.CATALOG_URL,
                     vue_url= CatalogCommon.VUE_SERVICE_URL,
                     catalogId=CatalogEnum.HOME.value):
    # ---- catalog service
    cat_url, cat_jsonObj = CatalogSvcTestUtil.startUp(url=cat_url, catalogId=catalogId)
    page_rows, page_rows_iids = CatalogSvcTestUtil.getPageRows(cat_jsonObj)
    vue_json_str, vue_jsonObj = VueSvcTestUtil.startUp(url=vue_url, catalogId=catalogId)
    vue_page_rows, vue_page_rows_iids = VueSvcTestUtil.getPageRows(vue_jsonObj)
    print('page_row_iids=%s vue_page_rows_iids=%s' % (page_rows_iids, vue_page_rows_iids))
    assert page_rows_iids == vue_page_rows_iids
    # ---- vue service & catalog service
    cat_iids_in_a_row = []
    for row_iid in page_rows_iids: # example: row_iid=1300

        print('++++++++++ row_iid=', row_iid)
        # Vue Service
        vue_iids_in_a_row = VueSvcTestUtil.getIidsInOneRowByIid(
            vue_jsonObj, page_iids=page_rows_iids, target_iid=row_iid)
        print('vue_iids_in_a_row=%s' % (vue_iids_in_a_row))
        # Cat Service
        cat_iids_in_a_row = CatalogSvcTestUtil.getIidsInOneRowByIid(
            cat_jsonObj, page_iids=page_rows_iids, target_iid=row_iid)
        print('cat_iids_in_a_row=%s' % (cat_iids_in_a_row))

        # ---- gather attr in an array
        for attr in ['getIid','getTitle', 'getSubTitles', 'getExpires']: # ['getImage']:

            common_iids =   list(set(vue_iids_in_a_row).intersection(cat_iids_in_a_row))
            print('common_iids=%s' % (common_iids))

            # adding tests to test_list
            for iid in (common_iids):
                print('iid=',iid)
                one_test = [] # to store test_name, actual, expected
                print('catalog name=%s, vue_target_row_iid=%s, common_iid=%s' % (CatalogEnum(catalogId), row_iid, iid ))

                test_name  = 'test_{0}_row_{1}_item_{2}_{3}'.format(CatalogEnum(catalogId), row_iid, iid, attr)

                vue_itemdetails_json = VueSvcTestUtil.getItemDetalsByIid(jsonobj=vue_jsonObj, target_row_iid=row_iid,
                                                                target_item_iid=iid)
                os.system('rm output/%s' % 'vue_iid_*.json')
                os.system('rm output/%s' % 'cat_iid_*.json')
                EzUtil.pprintJsonobjToFile(vue_itemdetails_json, outfile='output/vue_iid_%s_itemdetails.json' % iid)
                test_expect = getattr(VueSvcItemDetails(vue_itemdetails_json), attr)()
                cat_item_details_json = CatalogSvcTestUtil.getItemDetailsByIid(jsonobj=cat_jsonObj, target_item_iid=iid)
                EzUtil.pprintJsonobjToFile(cat_item_details_json, outfile='output/cat_iid_%s_itemdetails.json' % iid)
                test_actual = getattr(CatSvcItemDetails(cat_item_details_json), attr)()

                test_actual = test_actual if test_actual is not None else ''
                test_expect = test_expect if test_expect is not None else ''
                one_test.append(test_name)
                one_test.append(test_actual)
                one_test.append(test_expect)

                testlist.append(one_test) # list of [test_name, actual, expected]

    return testlist


if __name__ == '__main__':

  testlist1 = []
  testlist = create_test_list(testlist=testlist1, cat_url=CatalogCommon.CATALOG_URL,
                              vue_url=CatalogCommon.VUE_SERVICE_URL,
                              catalogId=CatalogEnum.HOME.value)
  testlist1.extend(testlist)
  #
  # testlist = create_test_list(testlist=testlist1, cat_url=CatalogCommon.CATALOG_URL,
  #                             vue_url=CatalogCommon.VUE_SERVICE_MOVIE_URL,
  #                             catalogId=CatalogEnum.MOVIES.value)
  # testlist1.extend(testlist)
  #
  # testlist = create_test_list(testlist=testlist1, cat_url=CatalogCommon.CATALOG_URL,
  #                             vue_url=CatalogCommon.VUE_SERVICE_SHOW_URL,
  #                             catalogId=CatalogEnum.SHOWS.value)
  # testlist1.extend(testlist)

  for t in testlist1:
        print('test_name={0}, actual={1}, expected={2}'.format(t[0], t[1], t[2]))
        testname, actual, expect = t[0], t[1], t[2]
        test = test_generator(testname, actual, expect)
        setattr(TestSequense, testname, test)

  unittest.main(verbosity=2,
                    testRunner=HTMLTestRunner(output='./reports'))