
import argparse, textwrap

import urllib.request
import json, os.path
from urllib.parse import unquote, quote
from util.urlutils import EzUtil

'''
SignOn class has member variables: protocol, hostname, uri and query_string.
  1. Call EzUtil.constructUrl from protocol, hostname, uri and query_string.
  2. Issue http request to the url, write the JSON response to output file, 
        return the JSON object for later use.
  3. Get rootNavDataHandle from step2 response JSON, construct a new URL
     'api/1.0.1.0/vibes/getdata.aspx?contextToken=<blah>&handles=<put rootNavDataHandle here>
  4. Get rootNavUrl from step3 and visit the rootNavUrl. Verify status_code is 200

'''
class SignOn(object):
    def __init__(self, proto, host, uri, query_string):
        self.protocol = proto
        self.host = host
        self.uri = uri
        self.qs = query_string

    def sign_in(self):
        url = EzUtil.constructUrl(protocol=self.protocol, host=self.host,
                                  uri=self.uri, qstring=self.qs)
        status_code, jsonobj = EzUtil.urlToJson(url, outfile='output/sign_in_a.json')
        return status_code, jsonobj

    def get_data(self, jsonobj):
        rootNavDataHandle = jsonobj['Value']["RootNavDataHandle"]
        uri = 'api/1.0.1.0/vibes/getdata.aspx'
        qstr = 'contextToken=778712964:609818312649940992:0:5234744:5067736:-1926405309&handles=%s' % str(rootNavDataHandle)
        url = EzUtil.constructUrl(protocol=self.protocol, host=self.host, uri=self.uri, qstring=self.qs)
        status_code, jsonobj = EzUtil.urlToJson(url, outfile='output/getdata_1.json')
        return status_code, jsonobj

    def get_root_nav(self, jsonobj):
        rootNavUrl = jsonobj['Value']['RootNavUrl']
        status_code, jsonobj = EzUtil.urlToJson(rootNavUrl, outfile='output/rootNav.json')
        return status_code, jsonobj


    def signon_and_verify(self):
        jsonobj, jsonobj2, jsonobj3 = None, None, None
        status_code, jsonobj = self.sign_in()
        assert(status_code == 200)
        assert(jsonobj != None)
        
        status_code, jsonobj2 = self.get_data(jsonobj)
        assert(status_code == 200)
        assert(jsonobj2 != None)

        status_code, jsonobj3 = self.get_root_nav(jsonobj2)
        assert(status_code == 200)
        assert(jsonobj3 != None)     


example_text='''example:
  > python3 components/sign_on.py

  or
  > python3 components/sign_on.py --protocol 'http' --host 'api-stage.vizio.com' --uri 'api/1.0.1.0/auth/authserversigninwithdetails.aspx' --qs 'clientTypeId=2000001&appTypeId=2000001&_url=1'
   

'''
def get_command_line_args():
    parser = argparse.ArgumentParser(epilog=example_text, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--protocol', default='http', help='protocol eg: http or https')
    parser.add_argument('--host', default='api-stage.vizio.com', help='host eg: api-stage.vizio.com')
    parser.add_argument('--uri', default='api/1.0.1.0/auth/authserversigninwithdetails.aspx', 
            help='api/1.0.1.0/auth/authserversigninwithdetails.aspx')
    parser.add_argument('--qs', default='clientTypeId=2000001&appTypeId=2000001&_url=', 
            help='query_sting eg: clientTypeId=2000001&appTypeId=2000001&_url=')
    parser.add_argument('--url', default=None, help='url')


    args = parser.parse_args()
    return args.protocol, args.host, args.uri, args.qs, args.url

if __name__ == '__main__':
    '''
    Here is example of the parameters:
    proto= 'http'
    host = 'api-stage.vizio.com'
    uri = 'api/1.0.1.0/auth/authserversigninwithdetails.aspx'
    qstr = 'clientTypeId=2000001&appTypeId=2000001&_url=1'
    '''
    proto, host, uri, qstr, url = get_command_line_args()
    signOnObj = SignOn(proto,host,uri, qstr)
    signOnObj.signon_and_verify()
