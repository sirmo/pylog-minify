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
import pdb

class ParseState(object):

    def __init__(self):
        self.clear()

    def clear(self):
        self.accept_sq = True
        self.sq_started = False
        self.accept_dq = True
        self.dq_started = False
        self.current = ''
        self.previous = ''
        self.accept_buffer = False
        self.buffer = ''

    def __prevent(self):
        self.accept_sq = False
        self.accept_dq = False

    def toggle_sq(self):
        self.current = "'"
        self.__prevent()
        self.accept_sq = True

    def toggle_dq(self):
        self.current = '"'
        self.__prevent()
        self.accept_dq = True


    def is_escaped(self, c):
        if self.current == '':
            return False
        to_ret = False
        if self.current == c:
            if self.previous == '\\':
                to_ret = True
        self.previous = c
        return to_ret

    def feed(self, c):
        if self.accept_buffer:
            self.buffer += c
            #print 'added: %s' % c

    def __repr__(self):
        to_ret = """ accept_sq: %s,
                     sq_started: %s,
                     current: %s,
                     previous: %s, 
                     accept_buffer: %s,
                     buffer_len: %s """ % (self.accept_sq,
                                          self.sq_started,
                                          self.current,
                                          self.previous,
                                          self.accept_buffer,
                                          len(self.buffer))
        return to_ret

class CodeParser (object):

    def __init__(self):
        self.result_list = []
        self.state = ParseState()
        
    def parse(self, filename):
        self.buffer = ''
        f = open(filename)
        while True:
            c = f.read(1)  #this may have performance implications
            if not c:
                break #eof
            self.__parse(c)

        f.close()
        print self.state
        return self.result_list

    def __parse(self, c):
        #pdb.set_trace()
        if self.state.accept_sq:
            is_escaped = self.state.is_escaped(c)
            quote_style = "'"
            if c == quote_style and not is_escaped:
                if not self.state.sq_started:
                    self.state.sq_started = True
                    self.state.current = quote_style
                    self.state.accept_buffer = True
                    c = ''
                else:
                    self.result_list.append(self.state.buffer)
                    self.state.clear()

        if self.state.accept_dq:
            is_escaped = self.state.is_escaped(c)
            quote_style = '"'
            if c == quote_style and not is_escaped:
                if not self.state.dq_started:
                    self.state.dq_started = True
                    self.state.current = quote_style
                    self.state.accept_buffer = True
                    c = ''
                else:
                    self.result_list.append(self.state.buffer)
                    self.state.clear()

        self.state.feed(c)

    def __find_quotes(self, pattern, text):
        pass
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
                pass
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
