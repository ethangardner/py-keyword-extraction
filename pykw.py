#!/usr/bin/env python
# encoding: utf-8
import sys
import argparse
import csv
import os
import re
import mechanize
from bs4 import BeautifulSoup

csv.register_dialect('custom', delimiter='\t', doublequote=True, escapechar=None,
                     quotechar='"', quoting=csv.QUOTE_MINIMAL, skipinitialspace=False)

parser = argparse.ArgumentParser()
parser.add_argument('-f', action='store', dest='file', help='Path to the file containing urls')
parser.add_argument('-c', action='store', dest='content', help='Selector for the main content area')
opts = parser.parse_args()

def getContent():
    with open(opts.file) as urls:
        data = csv.reader(urls, dialect='custom')
        br = mechanize.Browser()
        br.set_handle_robots(False)
        for record in data:
            response = br.open(record[0])
            assert br.viewing_html()
            soup = BeautifulSoup(response.read())
            if(opts.content):
                content = soup.select(opts.content)
            else:
                raise Exception('A required argument is missing. The content area must be specified.')
            pagetitle = soup.title.string
            print pagetitle.encode('utf-8').strip()
            for s in content:
                s = str(s)
                s = ''.join(BeautifulSoup(s).findAll(text=True))
                s = s.encode('utf-8')
                pat = re.compile(r'\s+')
                s = pat.sub(' ', s).strip()
                print s


if __name__ == '__main__':    
    getContent()