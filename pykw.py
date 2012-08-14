#!/usr/bin/env python
# encoding: utf-8
import argparse
import csv
import re
import mechanize
from bs4 import BeautifulSoup
from topia.termextract import tag
from topia.termextract import extract

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
        scrape = []
        for url in data:
            response = br.open(url[0])
            assert br.viewing_html()
            soup = BeautifulSoup(response.read())
            if(opts.content):
                content = soup.select(opts.content)
            else:
                raise Exception('A required argument is missing. The content area must be specified.')
            # scrape.append(soup.title.string)
            text = soup.title.string
            for s in content:
                s = str(s).decode('ascii', 'ignore')
                s = ''.join(BeautifulSoup(s).findAll(text=True))
                pat = re.compile(r'\s+')
                s = pat.sub(' ', s).strip()          
                text = text + ': ' + s
                text = text.strip()
                scrape.append(text) 
        return scrape

def analyzeKeywords():
    content = getContent()
    tagger = tag.Tagger()
    tagger.initialize()
    extractor = extract.TermExtractor(tagger)
    for s in content:
        terms = sorted(extractor(s), key=lambda strength: strength[2])
        print terms
    
    
if __name__ == '__main__':    
    analyzeKeywords()