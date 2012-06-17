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

# idea taken from http://stackoverflow.com/a/1181924
def base62encode(number):
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')
    if number < 0:
        raise ValueError('number must be positive')

    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    base62 = ''
    while number:
        number, i = divmod(number, 62)
        base62 = alphabet[i] + base62

    return base62 or alphabet[0]

def base62decode(number):
    return int(number,62)

class ParseState(object):

    def __init__(self, filter):
        self.filter = filter
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
        self.is_comment = False
        self.to_filter = True
        self.__init_filter_buffer() 

    def __init_filter_buffer(self):
        self.filter_buffer = ''
        for each in self.filter:
            self.filter_buffer += ' '

    def __prevent(self):
        self.accept_sq = False
        self.accept_dq = False

    def toggle_sq(self):
        self.current = "'"
        self.__prevent()
        self.accept_sq = True
        self.sq_started = True

    def toggle_dq(self):
        self.current = '"'
        self.__prevent()
        self.accept_dq = True
        self.dq_started = True


    def is_escaped(self, c):
        if self.current == '':
            return False
        to_ret = False
        if self.current == c:
            if self.previous == '\\':
                to_ret = True
        self.previous = c
        return to_ret


    def should_be_filtered(self):
        return self.to_filter

    def __feed_filter(self, c):
        new_filter_buffer = self.filter_buffer[1:len(self.filter)] # replace first letter
        self.filter_buffer = new_filter_buffer + c
        if self.filter_buffer == self.filter:
            self.to_filter = False
        #print 'buffer %s %s' % (len(self.filter), self.filter_buffer)

    def feed(self, c):
        if self.accept_buffer:
            self.buffer += c
            #print 'added: %s' % c
        else:
            self.__feed_filter(c)

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

    def __init__(self, options):
        self.result_list = []
        
        self.state = ParseState(options.filter)
        self.state.clear()
        
    def parse(self, filename):
        self.result_list = []
        f = open(filename)
        while True:
            c = f.read(1)  #this may have performance implications
            if not c:
                break #eof
            self.__parse(c)

        f.close()
        #print self.state
        self.state.clear()
        return self.result_list

    def __parse(self, c):
        #pdb.set_trace()
        
        # ignore comments

        if self.state.is_comment:
            if c == '\n':
                self.state.clear()
                return None

        if self.state.accept_sq:
            if self.state.accept_dq:
                if c == '#':
                    self.state.is_comment = True
                    return None

        if self.state.accept_sq:
            is_escaped = self.state.is_escaped(c)
            quote_style = "'"
            if c == quote_style and not is_escaped:
                if not self.state.sq_started:
                    self.state.toggle_sq()
                    self.state.accept_buffer = True
                    c = ''
                else:
                    if not self.state.should_be_filtered():
                        self.result_list.append(self.state.buffer)
                    self.state.clear()

        if self.state.accept_dq:
            is_escaped = self.state.is_escaped(c)
            quote_style = '"'
            if c == quote_style and not is_escaped:
                if not self.state.dq_started:
                    self.state.toggle_dq()
                    self.state.accept_buffer = True
                    c = ''
                else:
                    if not self.state.should_be_filtered():
                        self.result_list.append(self.state.buffer)
                    self.state.clear()

        self.state.feed(c)

    def __find_quotes(self, pattern, text):
        pass

def recursive_file_gen(mydir):
   for root, dirs, files in os.walk(mydir):
       for file in files:
           if file.endswith('.py'):
               yield os.path.join(root, file)

def build_index(result_list):
    if_bigger = 4
    index_dict = {}
    i = 0
    for each in result_list:
        if len(each) > if_bigger:
            b62 = base62encode(i)
            index_dict[b62] = each
            i += 1

    print_index(index_dict)
    print "entries indexed: %s" % i
    return index_dict

def print_index(index_dict):
    print "*** Index of log descriptions to minify"
    for key, value in index_dict.items():
        print '\t%s - "%s"' % (key, value)

def analyze_code(options):
    result_list = []
    files = recursive_file_gen(options.codebase)
    codeparser = CodeParser(options)
    for each in files:
        print 'analyzing %s' % each
        result = codeparser.parse(each)
        for text in result:
            if not text == None:
                split_up = text.split('%s')
                print '\t%s' % split_up
                result_list += split_up

    return result_list
def main():

    usage = "usage: %prog -c <code base> <input log files..>\n\n"  
    usage += "example:\n       %prog -c ~/development/project1/ project1.log"
    parser = optparse.OptionParser(usage)
    parser.add_option("-c", "--codebase", dest="codebase",
                      help="project location of the python code to be analyzed")
    parser.add_option ("-f", "--filter", dest="filter",
                      help="filter only string formatting with following filter keyword")
    parser.add_option("-v", "--verbose",
                 action="store_true", dest="verbose")
    parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose")


    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error("incorrect number of arguments")
    if options.verbose:
        print "reading %s..." % options.filename
    
    result = analyze_code(options)

    build_index(result)
if __name__ == '__main__':
    main()
