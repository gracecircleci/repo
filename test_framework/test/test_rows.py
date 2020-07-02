import unittest
import os
from pyunitreport import HTMLTestRunner
from components.catalog import CatalogEnum, Const
from components.catalogItemDetails import CatSvcItemDetails, CatalogSvcTestUtil
from components.VueItemDetails import VueSvcItemDetails, VueSvcTestUtil
from components.VueRows import VueSvcRowUtil, VueSvcRows
from components.catalogRows import CatSvcRows, CatalogSvcRowUtil
from util.urlutils import EzUtil, EnvironCommon


FLAG_COMMON = True

class TestSequense(unittest.TestCase):
    pass

def the_test_generator(testname=None, a=0, b=0, cat_url=None, vue_url=None):
    def test(self):
        print('running test %s acutal=%s expected=%s' % (testname, a, b))
        self.assertEqual(a,b,
            'TestFailed on [%s]: test_name=%s, acutal=%s, expected=%s cat_url=%s,catalog_headers=%s, vue_url=%s' %
                         (EnvironCommon.env, testname, a, b, cat_url, Const().HEADERS, vue_url))
    return test

def create_test_list(testlist=[], cat_url=EnvironCommon.CATALOG_URL,
                     vue_url= EnvironCommon.VUE_SERVICE_URL,
                     catalogId=CatalogEnum.HOME.value):
    # ---- catalog service
    cat_url, vue_url = cat_url, vue_url
    cat_url, cat_jsonObj = CatalogSvcTestUtil.startUp(url=cat_url, catalogId=catalogId)
    page_rows, page_rows_iids = CatalogSvcTestUtil.getPageRows(cat_jsonObj)
    vue_json_str, vue_jsonObj = VueSvcTestUtil.startUp(url=vue_url, catalogId=catalogId)
    vue_page_rows, vue_page_rows_iids = VueSvcTestUtil.getPageRows(vue_jsonObj)
    print('catalog url=%s, ', cat_url)
    #print('=====>>> page_row_iids=%s vue_page_rows_iids=%s' % (page_rows_iids, vue_page_rows_iids))
    if FLAG_COMMON:
        common_iids = list(set(page_rows_iids).intersection(vue_page_rows_iids))
        print('common_iids=%s' % (common_iids))
        test_iids = common_iids
    else:
        test_iids = vue_page_rows_iids
    #assert page_rows_iids == vue_page_rows_iids
    # ---- vue service & catalog service
    for row_iid in test_iids: # example: row_iid=1300
        print('row_iid=', row_iid)

        vjson = VueSvcRowUtil.getRowItemByIid(jsonobj=vue_jsonObj, iid=row_iid)
        cjson = CatalogSvcRowUtil.getRowItemByIid(jsonobj=cat_jsonObj, iid=row_iid)

        for attr in ['getId','getTitle', 'getItemsLength']: # remove 'getItems' due to random drafting
                    print('row_iid=',row_iid)
                    one_test = [] # to store test_name, actual, expected
                    print('catalog name=%s, vue_row_iid=%s' % (CatalogEnum(catalogId), row_iid))

                    test_name  = 'test_{0}_row_{1}_{2}'.format(CatalogEnum(catalogId), row_iid, attr)

                    test_expect = getattr(VueSvcRows(vjson), attr)()
                    test_actual = getattr(CatSvcRows(cjson), attr)()
                    print('===>>> test_name=%s, test_expect=%s, test_actual=%s' % (test_name, test_expect, test_actual))
                    print('cat_url=%s, vue_url=%s' % (cat_url, vue_url))

                    test_actual = test_actual if test_actual is not None else ''
                    test_expect = test_expect if test_expect is not None else ''
                    one_test.append(test_name)
                    one_test.append(test_actual)
                    one_test.append(test_expect)
                    one_test.append(cat_url)
                    one_test.append(vue_url)

                    testlist.append(one_test) # list of [test_name, actual, expected]
    return testlist


def the_test_run():
    testlist1 = []
    testlist = create_test_list(testlist=testlist1, cat_url=EnvironCommon.CATALOG_URL,
                                vue_url=EnvironCommon.VUE_SERVICE_URL,
                                catalogId=CatalogEnum.HOME.value)
    testlist1.extend(testlist)


    testlist = create_test_list(testlist=testlist1, cat_url=EnvironCommon.CATALOG_URL,
                                    vue_url=EnvironCommon.VUE_SERVICE_MOVIE_URL,
                                    catalogId=CatalogEnum.MOVIES.value)
    testlist1.extend(testlist)


    testlist = create_test_list(testlist=testlist1, cat_url=EnvironCommon.CATALOG_URL,
                                    vue_url=EnvironCommon.VUE_SERVICE_SHOW_URL,
                                    catalogId=CatalogEnum.SHOWS.value)
    testlist1.extend(testlist)

    testlist = create_test_list(testlist=testlist1, cat_url=EnvironCommon.CATALOG_URL,
                                    vue_url=EnvironCommon.VUE_SERVICE_SEARCH_URL,
                                    catalogId=CatalogEnum.SEARCH.value)
    testlist1.extend(testlist)
    testlist = create_test_list(testlist=testlist1, cat_url=EnvironCommon.CATALOG_URL,
                                    vue_url=EnvironCommon.VUE_SERVICE_LEARN_URL,
                                    catalogId=CatalogEnum.LEARN.value)
    testlist1.extend(testlist)

    for t in testlist1:
            print('test_name={0}, actual={1}, expected={2}'.format(t[0], t[1], t[2]))
            testname, actual, expect, cat_url, vue_url = t[0], t[1], t[2], t[3], t[4]
            test = the_test_generator(testname, actual, expect, cat_url, vue_url)
            setattr(TestSequense, testname, test)
    print('total testcase count=', len(testlist1))


if __name__ == '__main__':
    the_test_run()
    unittest.main(verbosity=2,
                    testRunner=HTMLTestRunner(output='./reports'))