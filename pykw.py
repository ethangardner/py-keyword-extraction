#!/usr/bin/env python
# encoding: utf-8
import argparse
import csv
import re
import json
import time
import threading
import mechanize
import sys
from bs4 import BeautifulSoup, Comment
from topia.termextract import tag
from topia.termextract import extract

csv.register_dialect('custom', delimiter='\t', doublequote=True, escapechar=None,
                     quotechar='"', quoting=csv.QUOTE_MINIMAL, skipinitialspace=False)

parser = argparse.ArgumentParser()
parser.add_argument('-i, --input', action='store', dest='file', help='Path to the input file containing urls')
parser.add_argument('-c, --content', action='store', dest='content', help='Selector for the main content area')
parser.add_argument('-o, --output', action='store', dest='output', help='Name of the output file')
parser.add_argument('-l, --length', action='store', dest='length', help='Minimum string length of the tags to return')
opts = parser.parse_args()

def getFormat():
    format = opts.output.rsplit('.', 1)
    if(len(format) < 2):
        format.append('csv')
    elif not(format[1] == 'json' or format[1] == 'csv'):
        print "Please enter a valid file type for the format parameter. Acceptable values are 'json' or 'csv'"
        sys.exit()
    return format

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
            soup = BeautifulSoup(response.read())
            
            # Remove inline scripts, styles and comments completely
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
                s = re.sub(r'<[^>]*?>', '', s) #strip remaining tag contents
                text = text + ': ' + s
                text = text.strip()
                scrape.append(text)
            time.sleep(2) # throttles requests to be courteous
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
    keywords = {}
    for i in set(termlist):
        keywords[i] = termlist.count(i)
    return keywords
    
def generateExport():
    keywords = analyzeKeywords()
    format = getFormat()
    if(format[1] == 'json'):
        f = open(format[0] + '.' + format[1], 'w')
        f.write(json.dumps(keywords, sort_keys=True, indent=4))
        f.close()
    elif(format[1] == 'csv'):
        csvfile = open(format[0] + '.' + format[1], 'wb')
        c = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        c.writerow(['Keyword', 'Count'])
        for term in keywords.items():
            try:
                c.writerow(term)
            except Exception:
                continue
        csvfile.close()        
         
    
if __name__ == '__main__':    
    generateExport()
