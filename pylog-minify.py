"""
py log minify - This is a proof of concept. The simple idea is to statically code analyze python source code
                and use the string formatting found in the code to 
                compress logs beyond what's possible with conventional compression utilities. 
                Goal being a dramatically reduced space requirement for long term log retention.

Author: Mirsad Dedovic 
"""

import optparse
import os
import re

class CodeParser (object):

    def __init__(self):
        self.result_list = []

    def parse(self, filename):
        self.result_list = []
        patterns = []
        patterns.append( r"'([^'\\]*(?:\\.[^'\\]*)*)'")
        #patterns.append( r'"([^"\\]*(?:\\.[^"\\]*)*)"')
        #patterns.append(r'"""([^"\\]*(?:\\.[^"\\]*)*)"""')
        #patterns.append(r"'([^\"]*)'")
        #patterns.append(r'"""(.*)"""')

        f = open(filename)
        text = f.read()
        for pattern in patterns:
            self.__find_quotes(pattern, text)
        f.close()
        return self.result_list

    def __find_quotes(self, pattern, text):
        pattern = pattern
        m = re.findall(pattern, text, re.DOTALL | re.VERBOSE)
        for match in m:
            if not match == '':
                self.result_list.append(match)    

codeparser = CodeParser()

def recursive_file_gen(mydir):
   for root, dirs, files in os.walk(mydir):
       for file in files:
           if file.endswith('.py'):
               yield os.path.join(root, file)

def analyze_code(base_path):
    files = recursive_file_gen(base_path)
    for each in files:
        result = codeparser.parse(each)
        for text in result:
            if not text == None:
                print text
def main():

    usage = "usage: %prog -c <code base> <input log files..>\n\n"  
    usage += "example:\n       %prog -c ~/development/project1/ project1.log"
    parser = optparse.OptionParser(usage)
    parser.add_option("-c", "--codebase", dest="codebase",
                      help="project location of the python code to be analyzed")
    parser.add_option("-v", "--verbose",
                 action="store_true", dest="verbose")
    parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose")


    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error("incorrect number of arguments")
    if options.verbose:
        print "reading %s..." % options.filename
    
    analyze_code(options.codebase)

if __name__ == '__main__':
    main()
