#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

import base64
import json
import logging
import os
from optparse import OptionParser
import sys
import subprocess

try:
    # Py3
    from urllib.request import build_opener, urlopen
except ImportError:
    # Py2
    from urllib2 import urlopen

import zlib

# python -m pip install -e git+https://github.com/clach04/w2d.git#egg=w2d
#import w2d

# create logger
log = logging.getLogger("mmic")
log.setLevel(logging.DEBUG)
disable_logging = False
disable_logging = True  # TODO pickup from command line, env, config?
if disable_logging:
    log.setLevel(logging.NOTSET)  # only logs; WARNING, ERROR, CRITICAL
    #log.setLevel(logging.INFO)  # logs; INFO, WARNING, ERROR, CRITICAL

ch = logging.StreamHandler()  # use stdio

if sys.version_info >= (2, 5):
    # 2.5 added function name tracing
    logging_fmt_str = "%(process)d %(thread)d %(asctime)s - %(name)s %(filename)s:%(lineno)d %(funcName)s() - %(levelname)s - %(message)s"
else:
    if JYTHON_RUNTIME_DETECTED:
        # process is None under Jython 2.2
        logging_fmt_str = "%(thread)d %(asctime)s - %(name)s %(filename)s:%(lineno)d - %(levelname)s - %(message)s"
    else:
        logging_fmt_str = "%(process)d %(thread)d %(asctime)s - %(name)s %(filename)s:%(lineno)d - %(levelname)s - %(message)s"

formatter = logging.Formatter(logging_fmt_str)
ch.setFormatter(formatter)
log.addHandler(ch)

CURL_BIN = os.path.expanduser(os.environ.get('CURL_BIN', 'curl'))


def gen_pako_url(in_str, image_type=None):  # TODO enum type for image_type?
    image_type = image_type or 'jpeg'
    if image_type not in ('jpeg', 'svg'):
        raise NotImplementedError('image_type %r not implemented/supported' % (image_type,))

    # https://docs.kroki.io/kroki/setup/encode-diagram/#python
    json_dict = {
        "code": in_str,
        # optional options like theme; "mermaid": {"theme": "default"},
    }
    encoded_str = base64.urlsafe_b64encode(zlib.compress(json.dumps(json_dict).encode('utf-8'), 9))

    #prefix = 'http://mermaid.live/view#pako:'
    if image_type == 'svg':
        prefix = 'https://mermaid.ink/svg/pako:'
    else:
        prefix = 'https://mermaid.ink/img/pako:'  # defaults to jpeg (jpg); options; jpeg (default), png, webp - Use /svg to get an SVG image
    #prefix = 'https://mermaid.ink/img?type=png/pako:'  # this does not work
    #postfix = '?type=png'  # Nor this
    link = prefix + encoded_str.decode('ascii').replace('+', '-').replace('/', '_')  # + postfix
    return link

CURL_HEADERS = {  # Windows 11, Release-Date: 2024-12-11 - curl 8.11.1 (Windows) libcurl/8.11.1 Schannel zlib/1.3 WinIDN
    #HTTP_USER_AGENT: 'curl/7.68.0',  # Ubuntu/Debian Release-Date: 2020-01-08 - curl 7.68.0 (x86_64-pc-linux-gnu) libcurl/7.68.0 OpenSSL/1.1.1f zlib/1.2.11 brotli/1.0.7 libidn2/2.2.0 libpsl/0.21.0 (+libidn2/2.2.0) libssh/0.9.3/openssl/zlib nghttp2/1.40.0 librtmp/2.3
    'HTTP_USER_AGENT': 'curl/8.11.1',
    'HTTP_ACCEPT': '*/*',
}
MOZILLA_FIREFOX_HEADERS = {
    #'HTTP_HOST': 'localhost:8000',
    'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'HTTP_ACCEPT': '*/*',
    'HTTP_ACCEPT_LANGUAGE': 'en-US,en;q=0.5',
    'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br',
    'HTTP_SERVICE_WORKER': 'script',
    'HTTP_CONNECTION': 'keep-alive',
    'HTTP_COOKIE': 'js=y',  # could be problematic...
    'HTTP_SEC_FETCH_DEST': 'serviceworker',
    'HTTP_SEC_FETCH_MODE': 'same-origin',
    'HTTP_SEC_FETCH_SITE': 'same-origin',
    'HTTP_PRAGMA': 'no-cache',
    'HTTP_CACHE_CONTROL': 'no-cache'
}
def main(argv=None):
    if argv is None:
        argv = sys.argv

    DEBUG = False

    usage = "usage: %prog [options] in_filename"
    parser = OptionParser(usage=usage, version="%%prog %s" % '0.0.1')
    parser.add_option("-i", "--input", help="Input mermaid file")
    parser.add_option("-o", "--output", help="Output mermaid file. Filename extension should be one of; svg or jpeg (jpg)")  # TODO Imlplement; svg, png, jpeg (jpg), webp")
    parser.add_option("-v", "--verbose", action="store_true")

    #parser.add_option("-f", "--pdfFit", action="store_true")  # DEBUG this will be ignored, for use with https://github.com/pandoc-ext/diagram

    (options, args) = parser.parse_args(argv[1:])
    verbose = options.verbose
    if DEBUG:
        verbose = True

    if verbose:
        print('Python %s on %s' % (sys.version.replace('\n', ' - '), sys.platform))

    if not options.input:
        parser.error("-i/--input is required")
    if not options.output:
        parser.error("-o/--output is required")

    in_filename = options.input
    out_filename = options.output

    if verbose:
        print('in_filename: %s' % (in_filename,))
        log.info('in_filename %s', in_filename)
        print('out_filename: %s' % (out_filename,))
        log.info('out_filename %s', out_filename)

    f = open(in_filename)  # assume correct encoding...
    data = f.read()
    f.close()
    if out_filename.lower().endswith('svg'):
        image_type = 'svg'
    else:
        # FIXME split file extension...
        image_type = None  # 'jpeg'  # jpg

    url = gen_pako_url(data, image_type=image_type)
    if verbose:
        print('%s' % (url,) )
        log.info('url: %s', url)

    """
    f = urlopen(url)
    fout = open(out_filename, "wb")
    fout.write(f.read())
    fout.close()
    f.close()
    """
    #image_data = w2d.easy_get_url(url, headers=MOZILLA_FIREFOX_HEADERS)
    """
    image_data = w2d.easy_get_url(url, headers=CURL_HEADERS)
    fout = open(out_filename, "wb")
    fout.write(image_data)
    fout.close()
    f.close()
    """
    cmd = [CURL_BIN, url, '--output', out_filename]  # NOTE likely to be png filename BUT jpg contents
    subprocess.check_call(cmd)

    return 0


if __name__ == "__main__":
    sys.exit(main())

