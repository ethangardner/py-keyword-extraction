# Description
Reads a text file with one url on each line to scrape the contents of a web page and extract 
key terms using natural language processing. Built with python.

## Requirements
* [Python 2.7.x](http://python.org/download/)
* [BeautifulSoup 4](http://www.crummy.com/software/BeautifulSoup/)
* [Mechanize](http://pypi.python.org/pypi/mechanize/)
* [Topia Term Extract](http://pypi.python.org/pypi/topia.termextract/)

## Instructions
Run the script from the command line. There are a few required options

### Required Arguments
* `-i`, `--input` the name of the txt file containing the URLS
* `-c`, `--content` the selector for the content region to parse
* `-o`, `--output` the name of the file to be output. Acceptable formats are csv or json.

### Optional Arguments

* `-l`, `--length` the minimum length of each keyword returned by the script
