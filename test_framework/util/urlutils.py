import urllib.request
import urllib.parse
import json, os.path
from urllib.parse import unquote, quote

class EzUtil():

    @staticmethod
    def context_token_str():
        return 'contextToken=-901682349:699519437853925376:0:5234744:5067736:2029148903'

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