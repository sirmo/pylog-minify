pylog-minify
============

Minifying Python Logs


This was a Proof of Concept to see what sort of gain can be expected when compressing application logs, if we staticly analyze the source code for common blocks of text.

Starting with a 414M raw file, we were able to shrink it to 271M. However since the log files tend to compress well. It was interesting to see what sort of difference we got once the files were gziped.

Gzip results:

- original gzip: 31M (32,066,354)
- minified gzip: 28M (29,141,218)

This was just a POC and further improvements can be made to the algorithm, sorting the keyword index by length to ensure largest entries are matched first for instance, as well as timestamp compression.

Also the performance is an issue, no optimizations were used.

If you would like to experiment with the script I suggest you use pypy for some modest performance gains if you are working with large files.

`pypy pylog-minify-static.py -c <your_project_location> tmp/sample.log -f 'log.'`

The example above has the `-f 'log.'`. This optmizes the text block search to python source code which contains log. text only. If you want all the static text to be included in your lookup index you can leave -f as '' empty.


Further Work:

I think it would be more interesting to implement this dynamicaly, by writting a replacement for the python's loggin module. Far bigger gains in terms of space requirements could be accomplished in this fashion. 