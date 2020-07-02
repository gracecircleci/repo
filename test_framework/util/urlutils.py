import urllib.request
import urllib.parse
import json, os.path
from enum import Enum
from urllib.parse import unquote, quote

class CatalogEnum(Enum):
    HOME = 1
    SHOWS = 2
    MOVIES = 3
    LEARN = 20
    SEARCH = 5
    def __str__(self):
        return '%s' % self.name

class EnvironCommon():
    CATALOG_HOST_DEV = 'catalog-dev.smartcasttv.com'
    CATALOG_HOST_PROD = 'catalog-prod.smartcasttv.com'
    VUE_HOST_DEV = 'api-stage.vizio.com'
    VUE_HOST_PROD = 'api.vizio.com'
    CONTEXT_TOKEN_DEV = 'contextToken=-901682349:629546385057943552:508:5234744:5067736:2029148903'
    CONTEXT_TOKEN_PROD = 'contextToken=-27856087:638773072417591296:0:5234744:5067736:-1926405309'

    # if no environment variable set use PROD as default
    env = os.environ['VIZIO_TEST_ENV'].lower() if (os.environ['VIZIO_TEST_ENV'] and os.environ['VIZIO_TEST_ENV']!='') else 'prod'.lower()
    print('environment var VIZIO_TEST_ENV not set. Use PROD as the environment')
    CATALOG_HOST = CATALOG_HOST_PROD if env == 'prod' else CATALOG_HOST_DEV
    VUE_HOST = VUE_HOST_PROD if env == 'prod' else VUE_HOST_DEV
    VUE_CONTEXT_TOKEN = CONTEXT_TOKEN_PROD if env == 'prod' else CONTEXT_TOKEN_DEV

    CATALOG_URL = 'http://%s/catalogs?rowsToExpand=100' % CATALOG_HOST
    VUE_SERVICE_URL = 'http://%s/api/1.0.1.0/vibes/getdata.aspx?%s&handles=[{"Vibe":{"Sid":3020009,"Iid":%d,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE=' % (
    VUE_HOST, VUE_CONTEXT_TOKEN, CatalogEnum.HOME.value)
    VUE_SERVICE_SHOW_URL = 'http://%s/api/1.0.1.0/vibes/getdata.aspx?%s&handles=[{"Vibe":{"Sid":3020009,"Iid":%d,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE=' % (
    VUE_HOST, VUE_CONTEXT_TOKEN, CatalogEnum.SHOWS.value)
    VUE_SERVICE_MOVIE_URL = 'http://%s/api/1.0.1.0/vibes/getdata.aspx?%s&handles=[{"Vibe":{"Sid":3020009,"Iid":%d,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE=' % (
    VUE_HOST, VUE_CONTEXT_TOKEN, CatalogEnum.MOVIES.value)
    VUE_SERVICE_SEARCH_URL = 'http://%s/api/1.0.1.0/vibes/getdata.aspx?%s&handles=[{"Vibe":{"Sid":3020009,"Iid":%d,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE=' % (
    VUE_HOST, VUE_CONTEXT_TOKEN, CatalogEnum.SEARCH.value)
    VUE_SERVICE_LEARN_URL = 'http://%s/api/1.0.1.0/vibes/getdata.aspx?%s&handles=[{"Vibe":{"Sid":3020009,"Iid":%d,"_tid":18},"Vid":2000002,"Expand":2,"_tid":14}]&access_key=D/0FFxEJr5gXiH4qpf0k48V9Agw=&access_sig=COr+y/+4I9W64iYci+uJt9QCouE=' % (
    VUE_HOST, VUE_CONTEXT_TOKEN, CatalogEnum.LEARN.value)
    print('=== env===', env)
    print('HOME: catalog_url=%s, \n vue_url=%s' % (CATALOG_URL, VUE_SERVICE_URL))
    print('SHOWS:', VUE_SERVICE_SHOW_URL)
    print('MOVIE:', VUE_SERVICE_MOVIE_URL)
    print('SEARCH:', VUE_SERVICE_SEARCH_URL)
    print('SEARCH:', VUE_SERVICE_LEARN_URL)

class EzUtil():

    @staticmethod
    def constructUrlFromDict(dict):
        return EzUtil().constructUrl(dict['protocol'], dict['host'], dict['uri'], dict['qs'])

    @staticmethod
    def constructUrl(protocol='http', host=None, uri=None, qstring=None):
        '''
        contructUrl: construct an URL from protocol, hostname, uri and query_string
        parameters: 
            protocol: str - http or https
            host: str - hostname eg: api-stage.vizio.com or api.vizio.com
            uri: str - eg. 'api/1.0.1.0/auth/authserversigninwithdetails.aspx',
            qstring: str - query_string like "clientTypeId=2000001&appTypeId=2000001&_url=1"
        return: an URL str
        '''
        if (protocol==None) or (host==None) or (uri==None) or (qstring == None):
            raise ValueError('Error: protocol, host, uri and qstring can NOT be None.')
        url = '%s://%s/%s?%s' % (protocol, host, uri,qstring)
        return url

    @staticmethod
    def urlToJson(url, outfile):
        ''' Create a json object from the url
            parameter: url - url
            parameter: outfile - name of the output file. it can be <dir>/<dir>/filename
            Return: response.status and json object
        '''
        response = urllib.request.urlopen(url)
        assert response.status == 200

        data = response.read().decode('utf-8')
        jsonobj = json.loads(data)
        #outfile filepath - create dir if not exists
        fpath, fname = os.path.split(outfile)
        fpath = fpath if fpath else 'output'
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        # write the http response json to a file for debugging
        with open(outfile, 'w+') as fo:
            json.dump(jsonobj, fo, separators=(',',':'), sort_keys=True, indent=4)
        return response.status, jsonobj

    @staticmethod
    def urlToJsonPostVue(url, data_dict, hds_dict,outfile):

        response = urllib.request.urlopen(url)
        assert response.status == 200

        data = response.read().decode('utf-8')
        jsonobj = json.loads(data)
        #outfile filepath - create dir if not exists
        fpath, fname = os.path.split(outfile)
        fpath = fpath if fpath else 'output'
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        # write the http response json to a file for debugging
        with open(outfile, 'w+') as fo:
            json.dump(jsonobj, fo, separators=(',',':'), sort_keys=True, indent=4)
        return response.status, url, jsonobj

    @staticmethod
    def pprintJsonobjToFile(jsonobj, outfile='output/jsonToFile.json'):
        assert jsonobj is not None

        fpath, fname = os.path.split(outfile)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        # write the http response json to a file for debugging
        with open(outfile, 'w+') as fo:
            json.dump(jsonobj, fo, separators=(',',':'), sort_keys=True, indent=4)

    @staticmethod
    def urlToJsonWithPost(url, data_dict, hds_dict, outfile='output/post_url_result.json'):
        assert url is not None
        assert data_dict is not None
        assert hds_dict is not None
        # byte-type string
        data = json.dumps(data_dict)
        data = str.encode(data)

        req = urllib.request.Request(url, headers=hds_dict)

        response = urllib.request.urlopen(req, data)
        assert response.status == 200
        data = response.read().decode('utf-8')
        jsonobj = json.loads(data)
        #outfile filepath - create dir if not exists
        fpath, fname = os.path.split(outfile)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        # write the http response json to a file for debugging
        with open(outfile, 'w+') as fo:
            json.dump(jsonobj, fo, separators=(',',':'), sort_keys=True, indent=4)
        return response.status, url, jsonobj