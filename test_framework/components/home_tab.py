import argparse, textwrap

import urllib.request
import json, os.path
from urllib.parse import unquote, quote, urlparse
import pandas as pd
from pandas import json_normalize
from util.urlutils import EzUtil
from util.logging import EzLogger
from util.datautils import DataUtil

class HomeTab(object):

    def __init__(self, proto=None, host=None, uri=None, query_string=None):
        self.protocol = proto
        self.host = host
        self.uri = uri
        self.qs = query_string
        self.logger = EzLogger.getLogger(__file__)

        self.dataframe = None

    def getJsonFromHomeUrl(self, url=None):
        # construct and visit home_tab url
        if url is None:
            url = EzUtil.constructUrl(protocol=self.protocol, host=self.host, uri=self.uri, qstring=self.qs)
        assert url

        outfile = 'output/home.json'
        status_code, jsonobj = EzUtil.urlToJson(url, outfile=outfile)
        assert status_code == 200
        assert jsonobj is not None
        self.logger.info('vue url=%s. output json file is available %s' % (url, outfile))
        return url, jsonobj

    def getRowsIid(self, jsonobj):
        assert jsonobj is not None
        title = jsonobj['Value'][0]['Frame']['Data']['Title']['Text']
        df = json_normalize(data=jsonobj['Value'][0], record_path=['Frame', 'Data', 'Items'])
        df1 = df[['Vibe.Iid']]
        iid_list = [x for b in df1.values for x in b]
        self.logger.info('VueService title=[%s], rows_iids=%s' % (title, iid_list))
        return title, iid_list

    def getJsonFromFile(self, jsonfile):
        with open(jsonfile, 'r+') as f:
            json_str = f.read()
            jsonobj = json.loads(json_str)
            assert jsonobj is not None
            return jsonobj
    
    def getDataFromJson(self, jsonobj, rd_path=[], maxlevel=8):
        assert rd_path != []
        self.dataframe = json_normalize(data=jsonobj['Value'][0], 
            record_path=rd_path, max_level=maxlevel)
        assert self.dataframe is not None
        assert self.dataframe.columns is not None
        #  write df columns to a file for debugging purpose
        DataUtil().writeDataColumnNamesToFile(self.dataframe, outfile='output/home_columns.txt')
        return self.dataframe 

    def getFirstRowFromVueService(self, jsonobj, items_pos= 0, item_id=1300):
        '''
        From the jsonobj that we get from the http GET response
        :param jsonobj: the jsonobj that we get from the http GET response
        :param items_pos: position of the rows.  For example: pos 0 is item_id 1300, pos 1 is item_id 1301
        :param item_id: example: 1300 or 1301
        :return: title, row_item_title, iid_list.
               eg: title=Home, row_item_title=New Hero - 2019, iid_list=[28700, 28538, 28544, 28549, 28550]
        '''
        assert jsonobj is not None
        self.logger.info('Getting items_pos=%s, item_id=%s' % (items_pos, item_id))

        # get HomeTab Title and  row_item_title. eg: title= 'Home', row_item_title='New Hero - 2019'
        title = jsonobj['Value'][0]['Frame']['Data']['Title']['Text']
        row_item_title = jsonobj['Value'][0]['Frame']['Data']['Items'][items_pos]['Frame']['Data']['Title']

        the_record_path = ['Frame', 'Data', 'Items', 'Frame','Data','SummaryItems']
        dflevel2 = json_normalize(data=jsonobj['Value'][0], record_path=the_record_path, max_level=8)
        print('dfelevel2 columns=', dflevel2.columns)

        # only interested in the column 'Vibe.Root.Iid' where 'Vid'==92
        dflevel3 = dflevel2.reindex(columns=['Vid', 'Vibe.Root.Iid'])
        dflevel3 = dflevel3.loc[dflevel3['Vid']==92]
        dflevel3 = dflevel3.reindex(columns=['Vibe.Root.Iid'])
        iid_list = iid_list = [x for b in dflevel3.values for x in b ]

        # pprint for debugging
        self.pprintDataFrame(data=jsonobj['Value'][0],
                             record_path=['Frame', 'Data', 'Items', 'Frame','Data','SummaryItems'],
                             columns=['Vid','Vibe.Root.Iid','Frame.Data.Pivot.Vid','Frame.Data.Title','Frame.Data.SubTitles','Href'])

        self.logger.info('title=%s, row_item_title=%s, iid_list=%s' % (title, row_item_title, iid_list))
        return title, row_item_title, iid_list

    def pprintDataFrame(self, data, record_path, columns):
        top_df = json_normalize(
                    data=data,
                    record_path=record_path,
                    max_level=4
                    )
        df2 = top_df.reindex(columns=columns )
        print(df2)

    def visit_hometab_and_verify_fields(self, record_path=[], wanted_columns=[]):
        # check input param columns is not empty
        assert record_path != [] and wanted_columns != []

        # create json obj from the HomeTab url
        url, jsonObj = self.getJsonFromHomeUrl()
        assert jsonObj is not None

        # get data from json obj with specified record_path
        df = self.getDataFromJson(jsonObj,record_path)
        exist = DataUtil().allColumnsExist(df, wanted_columns)
        assert exist is True

        # check the required fields or columns are not null
        total_nulls = DataUtil().checkRequiredFieldsNotNull(df)
        print('total_nulls=', total_nulls)
        print('type(total_nulls)=', total_nulls)
        # the required fields value cannot be null, so total_nulls should be 0
        assert (total_nulls == 0) 
        return total_nulls

    @staticmethod
    def runVueServiceRowsIid():
        url = 'http://api-stage.vizio.com/api/1.0.1.0/vibes/getdata.aspx?contextToken=-901682349:629546385057943552:508:5234744:5067736:2029148903&handles=[{"Vibe":{"Sid":3020009,"Iid":1,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE='
        vue_url, vueJsonObj = HomeTab().getJsonFromHomeUrl(url)
        vue_title, vue_rows = HomeTab().getRowsIid(vueJsonObj)
        return vue_title, vue_rows

    @staticmethod
    def runVueServiceFirstRow():
        proto, host, uri, qstr = get_command_line_args()
        homeObj = HomeTab(proto, host, uri, qstr)
        url, jsonObj = homeObj.getJsonFromHomeUrl()  # construct url from proto,host, uri,qstr
        title, row_item_title, iid_list = homeObj.getFirstRowFromVueService(jsonObj, items_pos=0, item_id=1300)
        return title, row_item_title, iid_list

example_text='''example:
  python3 components/home_tab.py --protocol 'http' --host 'api-stage.vizio.com' --uri '/api/1.0.1.0/vibes/getdata.aspx' --qs 'contextToken=-901682349:629546385057943552:508:5234744:5067736:2029148903&handles=%5b%7b%22Vibe%22:%7b%22Sid%22:3020009,%22Iid%22:1,%22_tid%22:18%7d,%22Vid%22:2000002,%22Expand%22:2,%22_tid%22:14%7d%5d&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE='
'''
def get_command_line_args():
    parser = argparse.ArgumentParser(epilog=example_text, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--protocol', default='http', help='protocol eg: http or https')
    parser.add_argument('--host', default='api-stage.vizio.com', help='host eg: api-stage.vizio.com')
    parser.add_argument('--uri', default='api/1.0.1.0/vibes/getdata.aspx', 
            help='api/1.0.1.0/vibes/getdata.aspx')
    parser.add_argument('--qs', 
        default='contextToken=-901682349:629546385057943552:508:5234744:5067736:2029148903&handles=%5b%7b%22Vibe%22:%7b%22Sid%22:3020009,%22Iid%22:1,%22_tid%22:18%7d,%22Vid%22:2000002,%22Expand%22:2,%22_tid%22:14%7d%5d&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE=', 
        help='query_sting eg: clientTypeId=2000001&appTypeId=2000001&_url=')

    args = parser.parse_args()
    return args.protocol, args.host, args.uri, args.qs


if __name__ == '__main__':
    title, row_item_title, iid_list = HomeTab().runVueServiceFirstRow()

    






