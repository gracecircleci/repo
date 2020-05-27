import unittest
from components.home_tab import HomeTab
from util.datautils import DataUtil
from components.catalog import CatalogEnum, Const

class HomeTest(unittest.TestCase):
    def test_home_tab(self):

        homeObj = HomeTab( 'http', 
                           'api-stage.vizio.com',
                           'api/1.0.1.0/vibes/getdata.aspx',
                           'contextToken=-901682349:629546385057943552:508:5234744:5067736:2029148903&handles=[{"Vibe":{"Sid":3020009,"Iid":1,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE=')

        dict1 = homeObj.runVueServiceRowTitles(catalogId=CatalogEnum.HOME.value, item_pos=0, item_id=1300)
        home_rows_count = len(dict1)
        self.assertTrue(home_rows_count==6)

if __name__ == '__main__':
    unittest.main()
