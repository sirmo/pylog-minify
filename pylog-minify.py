"""
py log minify - This is a proof of concept. The simple idea is to statically code analyze python source code
                and use the string formatting found in the code to 
                compress logs beyond what's possible with conventional compression utilities. 
                Goal being a dramatically reduced space requirement for long term log retention.

Author: Mirsad Dedovic 
"""

import optparse




def main():

    usage = "usage: %prog -c <code base> -i <input log file>\n\n"  
    usage += "example:\n       %prog -c ~/development/project1/ project1.log"
    parser = optparse.OptionParser(usage)
    parser.add_option("-c", "--codebase", dest="codebase",
                      help="project location of the python code to be analyzed")
    parser.add_option("-i", "--inputlog", dest="inputlog",
                      help="input log to be compressed") 
    parser.add_option("-v", "--verbose",
                 action="store_true", dest="verbose")
    parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose")


    (options, args) = parser.parse_args()
    print options
    if len(args) != 2:
        parser.error("incorrect number of arguments")
    if options.verbose:
        print "reading %s..." % options.filename


if __name__ == '__main__':
    main()
