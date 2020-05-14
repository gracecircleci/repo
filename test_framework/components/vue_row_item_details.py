import argparse, textwrap

import urllib.request
import json, os.path
from urllib.parse import unquote, quote, urlparse
import pandas as pd
from pandas import json_normalize
from util.urlutils import EzUtil
from util.logging import EzLogger
from util.datautils import DataUtil
from components.home_tab import HomeTab

class VueRowItemDetails(HomeTab):
    def __init__(self, proto=None, host=None, uri=None, query_string=None, url=None):
        self.protocol = proto
        self.host = host
        self.uri = uri
        self.qs = query_string
        self.url = url
        self.logger = EzLogger.getLogger(__file__)

    def getJsonFromUrl(self, url=None):
        # construct and visit home_tab url
        if url is None:
            url = EzUtil.constructUrl(protocol=self.protocol, host=self.host, uri=self.uri, qstring=self.qs)
        assert url

        outfile = 'output/vue_row_item_details.json'
        status_code, jsonobj = EzUtil.urlToJson(url, outfile=outfile)
        assert status_code == 200
        assert jsonobj is not None
        self.logger.info('vue url=%s. output json file is available %s' % (url, outfile))
        return url, jsonobj

    def getRowTabTitle(self, jsonobj, items_pos=0):
        assert jsonobj is not None
        # get HomeTab Title and  row_item_title. eg: title= 'Home', row_item_title='New Hero - 2019'
        title = jsonobj['Value'][0]['Frame']['Data']['Title']['Text']
        row_item_title = jsonobj['Value'][0]['Frame']['Data']['Items'][items_pos]['Frame']['Data']['Title']
        return title, row_item_title

    def getRowItemDetails(self, jsonobj, the_vid=92, items_pos=0):  # items_pos is used for getting the row_item_title
        iid_list = None
        assert jsonobj is not None

        the_record_path = ['Frame', 'Data', 'Items', 'Frame', 'Data', 'SummaryItems']
        df = json_normalize(data=jsonobj['Value'][0], record_path=the_record_path, max_level=4)
        df = df[df['Vid'] == the_vid]  # select the rows
        df2 = df.reindex(
            columns=['Vid', 'Vibe.Root.Iid', 'Frame.Data.Title', 'Frame.Data.SubTitles', 'Frame.Data.ImageHandles',
                     'Frame.Data.Metadata'])

        return df2

    @staticmethod
    def unpack(df):
        assert df is not None
        val = [x for b in df.values for x in b][0]
        ret_val = val[0] if isinstance(val, list) else val
        return ret_val

    @staticmethod
    def getIidList(df):
        assert df is not None
        df_iids = df.reindex(columns=['Vibe.Root.Iid'])
        iid_list = [x for b in df_iids.values for x in b]
        return iid_list

    def getRowItemDetailByColumn(self, df, iids_index=0,
                                 columns=['Vid', 'Vibe.Root.Iid', 'Frame.Data.Title', 'Frame.Data.SubTitles',
                                          'Frame.Data.ImageHandles', 'Frame.Data.Metadata']):
        assert df is not None

        df2 = df.reindex(columns=columns)
        iid_list = VueRowItemDetails.getIidList(df2)

        df_one_iid = df2[df2['Vibe.Root.Iid'] == iid_list[iids_index]]
        df_iid = df_one_iid.reindex(columns=['Vibe.Root.Iid'])
        iid_str = VueRowItemDetails.unpack(df_iid)

        df_title = df_one_iid.reindex(columns=['Frame.Data.Title'])
        title_str = VueRowItemDetails.unpack(df_title)
        df_subtitle = df_one_iid.reindex(columns=['Frame.Data.SubTitles'])
        subtitle_str = VueRowItemDetails.unpack(df_subtitle)
        df_imageHandles = df_one_iid.reindex(columns=['Frame.Data.ImageHandles'])
        imageHandles_dict = VueRowItemDetails.unpack(df_imageHandles)
        df_metadata = df_one_iid.reindex(columns=['Frame.Data.Metadata'])
        metadata_jsonstr = df_metadata.to_json()
        ret_dict = {'title': title_str,
                    'subtitle': subtitle_str,
                    'iid': iid_str,
                    'imageHandles': imageHandles_dict,
                    'metadata': metadata_jsonstr
                    }
        return ret_dict

    def gather_item_details(self, jsonobj, the_vid=92, items_pos=0, iids_index=0):
        title, row_item_title = self.getRowTabTitle(jsonobj)
        df = self.getRowItemDetails(jsonobj, the_vid=the_vid, items_pos=items_pos)
        dict1 = self.getRowItemDetailByColumn(df, iids_index=iids_index)
        return dict1

    @staticmethod
    def run_home_item_details_locally(the_vid=92, items_pos=0, iids_index=0):
        proto, host, uri, qstr, url = get_command_line_args()
        itemDetailsObj = VueRowItemDetails(proto,host,uri,qstr)
        url, jsonobj = itemDetailsObj.getJsonFromUrl()

        title, row_item_title = itemDetailsObj.getRowTabTitle(jsonobj)
        df = itemDetailsObj.getRowItemDetails(jsonobj, the_vid=the_vid, items_pos=items_pos)
        dict1 = itemDetailsObj.getRowItemDetailByColumn(
            df, iids_index=iids_index)

        return dict1


example_text = '''example:
  python3 components/vue_row_item_details.py --protocol 'http' --host 'api-stage.vizio.com' --uri '/api/1.0.1.0/vibes/getdata.aspx' --qs 'contextToken=-901682349:629546385057943552:508:5234744:5067736:2029148903&handles=%5b%7b%22Vibe%22:%7b%22Sid%22:3020009,%22Iid%22:1,%22_tid%22:18%7d,%22Vid%22:2000002,%22Expand%22:2,%22_tid%22:14%7d%5d&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE='
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

    parser.add_argument('--url', default=None, help='url')

    args = parser.parse_args()
    return args.protocol, args.host, args.uri, args.qs, args.url


if __name__ == '__main__':

    dict1 = VueRowItemDetails.run_home_item_details_locally(the_vid=92, items_pos=0, iids_index=0)
    print('iid_str=', dict1['iid'])
    print('title_str=%s, subtitle_str=%s' % (dict1['title'], dict1['subtitle']))
    print('imageHandles_dict=%s, metadata_jsonstr=%s' % (dict1['imageHandles'], dict1['metadata']))
    print('-----------------------------------------------')

    dict1 = VueRowItemDetails.run_home_item_details_locally(the_vid=92, items_pos=0, iids_index=1)
    print('iid_str=', dict1['iid'])
    print('title_str=%s, subtitle_str=%s' % (dict1['title'], dict1['subtitle']))
    print('imageHandles_dict=%s, metadata_jsonstr=%s' % (dict1['imageHandles'], dict1['metadata']))
    print('-----------------------------------------------')

    dict1 = VueRowItemDetails.run_home_item_details_locally(the_vid=92, items_pos=0, iids_index=2)
    print('iid_str=', dict1['iid'])
    print('title_str=%s, subtitle_str=%s' % (dict1['title'], dict1['subtitle']))
    print('imageHandles_dict=%s, metadata_jsonstr=%s' % (dict1['imageHandles'], dict1['metadata']))
    print('-----------------------------------------------')

    dict1 = VueRowItemDetails.run_home_item_details_locally(the_vid=92, items_pos=0, iids_index=3)
    print('iid_str=', dict1['iid'])
    print('title_str=%s, subtitle_str=%s' % (dict1['title'], dict1['subtitle']))
    print('imageHandles_dict=%s, metadata_jsonstr=%s' % (dict1['imageHandles'], dict1['metadata']))
    print('-----------------------------------------------')

    dict1 = VueRowItemDetails.run_home_item_details_locally(the_vid=92, items_pos=0, iids_index=4)
    print('iid_str=', dict1['iid'])
    print('title_str=%s, subtitle_str=%s' % (dict1['title'], dict1['subtitle']))
    print('imageHandles_dict=%s, metadata_jsonstr=%s' % (dict1['imageHandles'], dict1['metadata']))
    print('-----------------------------------------------')









