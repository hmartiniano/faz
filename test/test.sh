#!/bin/bash
export PYTHONPATH=/home/hugo/devel/MakeTools/yamt:$PYTHONPATH
rm file*
#touch file1 file2
python ../yamt/main.py -v
