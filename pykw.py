#!/usr/bin/env python
# encoding: utf-8
import argparse
import csv
import re
import json
import time
import threading
import mechanize
from bs4 import BeautifulSoup, Comment
from topia.termextract import tag
from topia.termextract import extract

csv.register_dialect('custom', delimiter='\t', doublequote=True, escapechar=None,
                     quotechar='"', quoting=csv.QUOTE_MINIMAL, skipinitialspace=False)

parser = argparse.ArgumentParser()
parser.add_argument('-f', action='store', dest='file', help='Path to the file containing urls')
parser.add_argument('-c', action='store', dest='content', help='Selector for the main content area')
parser.add_argument('-o', action='store', dest='output', help='Name of the output file')
parser.add_argument('-l', action='store', dest='length', help='Minimum string length of the tags to return')
opts = parser.parse_args()

def getContent():
    with open(opts.file) as urls:
        data = csv.reader(urls, dialect='custom')
        br = mechanize.Browser()
        br.set_handle_robots(False)
        scrape = []
        print "=== Sit tight - Fetching content"
        for url in data:
            print "     - Fetching " + url[0]
            response = br.open(url[0])
            assert br.viewing_html()
            soup = BeautifulSoup(response.read())
            
            # Remove inline scripts, styles and comments
            for script in soup("script"):
                soup.script.extract()
            
            for style in soup("style"):
                soup.style.extract()
                
            comments = soup.findAll(text=lambda text:isinstance(text, Comment))
            [comment.extract() for comment in comments]
            
            if(opts.content):
                content = soup.select(opts.content)
            else:
                raise Exception('A required argument is missing. The content area must be specified.')
            text = soup.title.string
            for s in content:
                s = str(s).decode('ascii', 'ignore')
                s = ''.join(BeautifulSoup(s).findAll(text=True))
                pat = re.compile(r'\s+')
                s = pat.sub(' ', s).strip()          
                text = text + ': ' + s
                text = text.strip()
                scrape.append(text)
            time.sleep(2)
        return scrape

def analyzeKeywords():
    content = getContent()
    tagger = tag.Tagger()
    tagger.initialize()
    extractor = extract.TermExtractor(tagger)
    allterms = []
    print "=== Analyzing keywords"
    for s in content:
        try:
            terms = sorted(extractor(s), key=lambda strength: strength[2])
            allterms.extend(terms)
        except Exception:
            continue
    termlist = []
    for term in allterms:
        if(opts.length):
            if(len(term[0]) >= int(opts.length)):
                termlist.append(term[0].lower())
        else:
            termlist.append(term[0].lower())
    d = {}
    for i in set(termlist):
        d[i] = termlist.count(i)
    if(opts.output):
        f = open(opts.output, 'w')
        f.write(json.dumps(d, sort_keys=True, indent=4))
        f.close()
    else:
        csvfile = open('data.csv', 'wb')
        c = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        c.writerow(['Keyword', 'Count'])
        for term in d.items():
            try:
                c.writerow(term)
            except Exception:
                continue
        csvfile.close()
         
    
if __name__ == '__main__':    
    analyzeKeywords()