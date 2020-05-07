import unittest
from components.home_tab import HomeTab
from util.datautils import DataUtil

class HomeTest(unittest.TestCase):
    def test_home_tab(self):

        homeObj = HomeTab( 'http', 
                           'api-stage.vizio.com',
                           'api/1.0.1.0/vibes/getdata.aspx',
                           'contextToken=-901682349:629546385057943552:508:5234744:5067736:2029148903&handles=[{"Vibe":{"Sid":3020009,"Iid":1,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE=')
        
        record_path = DataUtil().RECORD_PATH
        required_columns = DataUtil().REQUIRED_COLUMNS
        total_nulls = homeObj.visit_hometab_and_verify_fields(record_path, required_columns)
        self.assertTrue(total_nulls==0)

if __name__ == '__main__':
    unittest.main()
