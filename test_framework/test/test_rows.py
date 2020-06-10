import unittest
import os
from pyunitreport import HTMLTestRunner
from components.catalog import CatalogEnum
from components.catalogItemDetails import CatSvcItemDetails, CatalogSvcTestUtil
from components.VueItemDetails import VueSvcItemDetails, VueSvcTestUtil
from components.VueRows import VueSvcRowUtil, VueSvcRows
from components.catalogRows import CatSvcRows, CatalogSvcRowUtil
from test.test_catalog import CatalogCommon
from util.urlutils import EzUtil




class TestSequense(unittest.TestCase):
    pass

def the_test_generator(testname=None, a=0, b=0):
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
    print('=====>>> page_row_iids=%s vue_page_rows_iids=%s' % (page_rows_iids, vue_page_rows_iids))
    assert page_rows_iids == vue_page_rows_iids
    # ---- vue service & catalog service
    for row_iid in page_rows_iids: # example: row_iid=1300
        print('row_iid=', row_iid)

        vjson = VueSvcRowUtil.getRowItemByIid(jsonobj=vue_jsonObj, iid=row_iid)
        cjson = CatalogSvcRowUtil.getRowItemByIid(jsonobj=cat_jsonObj, iid=row_iid)

        for attr in ['getId','getTitle', 'getItems', 'getItemsLength']: # ['getImage']:
                    print('row_iid=',row_iid)
                    one_test = [] # to store test_name, actual, expected
                    print('catalog name=%s, vue_row_iid=%s' % (CatalogEnum(catalogId), row_iid))

                    test_name  = 'test_{0}_row_{1}_{2}'.format(CatalogEnum(catalogId), row_iid, attr)

                    test_expect = getattr(VueSvcRows(vjson), attr)()
                    test_actual = getattr(CatSvcRows(cjson), attr)()
                    print('===>>> test_name=%s, test_expect=%s, test_actual=%s' % (test_name, test_expect, test_actual))

                    test_actual = test_actual if test_actual is not None else ''
                    test_expect = test_expect if test_expect is not None else ''
                    one_test.append(test_name)
                    one_test.append(test_actual)
                    one_test.append(test_expect)

                    testlist.append(one_test) # list of [test_name, actual, expected]
    return testlist


class TestRows(unittest.TestCase):
  def test_rows(self):
    testlist1 = []
    testlist = create_test_list(testlist=testlist1, cat_url=CatalogCommon.CATALOG_URL,
                                vue_url=CatalogCommon.VUE_SERVICE_URL,
                                catalogId=CatalogEnum.HOME.value)
    testlist1.extend(testlist)

    for t in testlist1:
        print('test_name={0}, actual={1}, expected={2}'.format(t[0], t[1], t[2]))
        testname, actual, expect = t[0], t[1], t[2]
        test = the_test_generator(testname, actual, expect)
        setattr(TestSequense, testname, test)
    print('total testcase count=', len(testlist1))
if __name__ == '__main__':
  unittest.main(verbosity=2,
                    testRunner=HTMLTestRunner(output='./reports'))