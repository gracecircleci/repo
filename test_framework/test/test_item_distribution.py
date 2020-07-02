import unittest
import os
from pyunitreport import HTMLTestRunner
from components.catalog import CatalogEnum, Const
from components.catalogItemDetails import CatalogSvcTestUtil
from components.catalogRows import CatSvcRows, CatalogSvcRowUtil
from components.VueRows import VueSvcRowUtil, VueSvcRows
from components.VueItemDetails import VueSvcTestUtil
from util.urlutils import EzUtil, EnvironCommon
from collections import Counter

ITERATIONS = 1000

class TestSequense(unittest.TestCase):
    pass

def the_test_generator(testname=None, a=0, b=0, cat_url=None, vue_url=None):
    def test(self):
        print('-->> running test %s acutal=%s expected=%s' % (testname, a, b))
        self.assertEqual(str(a),str(b),
            'TestFailed: test_name=%s, acutal(catalog)=%s, expected(vue)=%s cat_url=%s cat_header=%s, vue_url=%s' %
                         (testname, a, b, cat_url, Const().HEADERS,vue_url))
    return test

def startUp(cat_url=EnvironCommon.CATALOG_URL,
                     vue_url= EnvironCommon.VUE_SERVICE_URL,
                     catalogId=CatalogEnum.HOME.value):

    cat_url, vue_url = cat_url, vue_url
    cat_url, cat_jsonObj = CatalogSvcTestUtil.startUp(url=cat_url, catalogId=catalogId)
    page_rows, page_rows_iids = CatalogSvcTestUtil.getPageRows(cat_jsonObj)
    #vue_json_str, vue_jsonObj = VueSvcTestUtil.startUp(url=vue_url, catalogId=catalogId)
    vue_json_str, vue_jsonObj = VueSvcTestUtil.startUpCache(url=vue_url, catalogId=catalogId)
    vue_page_rows, vue_page_rows_iids = VueSvcTestUtil.getPageRows(vue_jsonObj)
    print('page_rows=%s, page_rows_iid=%s' % (page_rows, page_rows_iids))
    return page_rows, page_rows_iids, cat_jsonObj, vue_jsonObj

def distribution_one_row(cat_appearance_dict={}, vue_appearance_dict={}, cat_jsonObj=None, vue_jsonObj=None, row_iid=None):

    # ---- catalog service
    cjson = CatalogSvcRowUtil.getRowItemByIid(jsonobj=cat_jsonObj, iid=row_iid)
    vjson = VueSvcRowUtil.getRowItemByIid(jsonobj=vue_jsonObj,iid=row_iid)

    cat_item_ids = getattr(CatSvcRows(cjson), 'getItems')() # example: [30617, 30616, 30666, ...]
    vue_item_ids = getattr(VueSvcRows(vjson), 'getItems')()
    print('cat_item_ids=%s, vue_item_ids=%s' % (cat_item_ids, vue_item_ids))
    for i in range(len(cat_item_ids)):
        cat_appearance_dict.setdefault(i, []).append(cat_item_ids[i])  # d= {0:[iid, iid, ...], 1:[iid,iid,...], ...}
    for i in range(len(vue_item_ids)):
        vue_appearance_dict.setdefault(i, []).append(vue_item_ids[i])
    print('done distribution_one_row')
    return cat_item_ids, vue_item_ids

def calculate(cat_appearance_dict, vue_appearance_dict, slot=0): #cat_appearance_dict, vue_appearance_dict
    # catalog
    list_of_iids = cat_appearance_dict.get(slot) # example: list_of_iids on slot 0
    cat_counter = Counter(list_of_iids) # create a counter from a list of iids appeared on slot 0-5
    # vue service
    list_of_iids = vue_appearance_dict.get(slot) # slot = 0, 1, 2,...
    vue_counter = Counter(list_of_iids) # create a counter from a list of iids appeared on slot 0-5
    return cat_counter, vue_counter

def process_one_row(cat_url=EnvironCommon.CATALOG_URL,vue_url=EnvironCommon.VUE_SERVICE_URL,catalogId=CatalogEnum.HOME.value,row_pos=0):
    print('process page row:', row_pos)
    # collect data
    cat_appearance_dict, vue_appearance_dict = {}, {}
    cat_item_ids, vue_item_ids = None, None
    for itr in range(ITERATIONS):

        print('----- itr=', itr)
        os.system('rm output/%s' % '*.json')
        page_rows, page_rows_iids, cat_jsonObj, vue_jsonObj = startUp(cat_url=cat_url, vue_url=vue_url, catalogId=catalogId
            )
        row_iid = page_rows_iids[row_pos] # example: row_iid = 1300

        cat_item_ids, vue_item_ids = distribution_one_row(cat_appearance_dict=cat_appearance_dict, vue_appearance_dict=vue_appearance_dict,
                         cat_jsonObj=cat_jsonObj, vue_jsonObj=vue_jsonObj, row_iid=row_iid)

    # calculate distribution on one row
    # each cat_counter, vue_counter is for one slot on that row
    actual_results, expected_results = [], []
    print('========== Counting item appearance ============')
    for slot in range(len(cat_item_ids)):
        print('++++ slot: ', slot)
        cat_counter, vue_counter = calculate(cat_appearance_dict, vue_appearance_dict, slot=slot)

        # --- printing info for easy reading ---
        cat_total = sum(cat_counter.values())
        for cat_slot_item in cat_counter.most_common():
            cat_item_distribution = cat_slot_item[1]/cat_total
            print('cat_slot_item=%s, distribution=%.2f' % (cat_slot_item, cat_item_distribution))
        print('\t ---')
        vue_total = sum(vue_counter.values())
        for vue_slot_item in vue_counter.most_common():
            vue_item_distribution = vue_slot_item[1]/vue_total
            print('vue_slot_item=%s, distribution=%.2f' % (vue_slot_item, vue_item_distribution))
        print('\t ---')
        print('cat_counter.most_common()=', cat_counter.most_common())
        print('vue_counter.most_common()=', vue_counter.most_common())
        assert id(cat_counter) != id(vue_counter) # assert cat_counter != vue_counter
        actual_results.append(cat_counter.most_common())
        expected_results.append(vue_counter.most_common())

    return actual_results, expected_results

def create_test_list(testlist=[], cat_url=EnvironCommon.CATALOG_URL,
                     vue_url=EnvironCommon.VUE_SERVICE_URL,
                     catalogId=CatalogEnum.HOME.value,row_pos=0):

    test_name = 'test_item_distribution_row_%d' % row_pos

    actual_results, expected_results = process_one_row(cat_url=EnvironCommon.CATALOG_URL,
                                                         vue_url=EnvironCommon.VUE_SERVICE_URL,
                                                         catalogId=CatalogEnum.HOME.value,row_pos=row_pos)
    one_test = [] # one test is a list of test_name, test_actual, test_expected, cat_url, vue_url
    test_actual = str(actual_results)
    test_expected = str(expected_results)
    one_test.append(test_name)
    one_test.append(test_actual)
    one_test.append(test_expected)
    one_test.append(cat_url)
    one_test.append(vue_url)
    testlist.append(one_test)
    return testlist


def the_test_run():
    testlist1 = []
    row_pos = 0
    testlist = create_test_list(testlist=[], cat_url=EnvironCommon.CATALOG_URL,
                     vue_url=EnvironCommon.VUE_SERVICE_URL,
                     catalogId=CatalogEnum.HOME.value, row_pos=row_pos)

    for t in testlist:
        testname, actual, expect, cat_url, vue_url = t[0], t[1], t[2], t[3], t[4]
        test = the_test_generator(testname, actual, expect, cat_url, vue_url)
        setattr(TestSequense, testname, test)

if __name__ == '__main__':

    the_test_run()
    unittest.main(verbosity=2,
                    testRunner=HTMLTestRunner(output='./reports'))