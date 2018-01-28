s#!/usr/bin/env python

tablename="pdfextract"

for filename in *.pdf
do
 echo "converting file ${filename}"
 echo "pdf2txt.py -o ${filename}.html ${filename}.pdf"
 pdf2txt.py -o ${filename}.html ${filename}
done

for filename in *.html
do
 echo "reading file ${filename}"
 python htmlparser.py ${filename} ${tablename}

done