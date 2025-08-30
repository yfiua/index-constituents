#!/bin/sh

head -n -5 docs/index.html > docs/index.tmp.html
mv docs/index.tmp.html docs/index.html
./gen-footer.py >> docs/index.html
