#!/usr/bin/python

import sys
import getopt
from httplib import *
from urllib import *
import base64
import re
import json
import codecs
import time
import hashlib

from multiprocessing import Process, Manager


def varnish_get_data(host='localhost', port='6085', tag='RxHeader',
                     tag_val='Referer', username=None, password=None):

    if username is None:
        params = {}
        headers = {}
    else:
        auth = 'Basic ' + base64.encodestring(username + ':' + password)
        headers = {'Authorization': auth}

    url = '/log/1/' + tag + '/' + tag_val

    conn = HTTPConnection(host=host, port=port)
    conn.request(method="GET", url=url, headers=headers)

    response = conn.getresponse()
    data = response.read()
    conn.close

    return data


def varnish_parse_json(data=None):

    if data is None:
        return None

    varnish_decoded = json.loads(data)

    return varnish_decoded


def varnish_parse_log(ncsa_log='varnishncsa', urls_dict=None):

    if urls_dict is None:
        return None

    log = open('varnishncsa.log', 'r')
    p = re.compile('(.*) (.*) (.*) (\[.*\]) (".*") (\d+) (.*) (".*") (".*")')

    while True:
        try:
            s = log.readline()
        except:
            log = open('varnishncsa.log', 'r')
 #           break

        try:
            m = p.search(s)
            host = m.groups()[0]
            code = m.groups()[5].replace("'", "")
            url = m.groups()[4]

            url = url.replace('"', '')
            url = url.replace("GET ", "")
            url = url.replace(" HTTP/1.1", "")
            url = url.replace(" HTTP/1.0", "")

            if (code in ['404', '301', '304', '206', '500', '302', '403']):
                continue

            h = hashlib.sha1()
            h.update(url)
            hd = h.hexdigest()

            if h.hexdigest() in urls_dict:
                urls_dict[hd]['count'] += 1
                urls_dict[hd]['oldnew'] = urls_dict[h.hexdigest()]['newset']
                urls_dict[hd]['newset'] = time.time()
            else:
                urls_dict[hd] = {'url': url, 'count': 1,
                                 'born': time.time(), 'oldnew': 0,
                                 'newset': time.time()}
        except:
            time.sleep(1)
            continue

    log.close


def varnish_watch(d):
    varnish_parse_log(urls_dict=d)


def monitor(d):

    urls_dict = d

    if urls_dict is None:
        return None

    while True:
        print len(d.keys())

        now = time.time()
        for url in urls_dict.keys():
            url_d = urls_dict[url]

            if url_d['count'] > 1:
                del urls_dict[url]

            if  now - url_d['newset'] > 60:
                del urls_dict[url]

        time.sleep(1)

if __name__ == '__main__':
    manager = Manager()

    d = manager.dict()

    p_varnish = Process(target=varnish_watch, args=(d,))
    p_monitor = Process(target=monitor, args=(d,))

    p_varnish.start()
    p_monitor.start()

    p_varnish.join()
    p_monitor.join()
