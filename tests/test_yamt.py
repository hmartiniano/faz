#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_yamt
----------------------------------

Tests for `yamt` module.
"""

import unittest

from yamt import main

FILE1 = """
# Using bash as the interpreter
# file1, file2 <-
touch file1 file2

# file3, file4 <- file1, file2
echo "Hellow world! 1" > file3
echo "Hellow world! 1" > file4

# file5, file6 <- file3, file4
echo "Hellow world! 2" > file5
echo "Hellow world! 2" > file6

# file7, file8 <- file5, file6
echo "Hellow world! 3" > file7
echo "Hellow world! 3" > file8

# Now using python as the interpreter
# file9, file10, file11 <- file5, file3 [python]
import sys

a = [[range(3)], [range(4, 7)], [range(7, 10)]]
f = open("file11", "w")
for line in a:
    f.write(" ".join([str(i) for i in line]))
f.close()
open("file9", "w").write("Hello from python\\n")
open("file10", "w").write("Hello from python\\n")

# file22, file33 <- file1, file11 [ruby]
File.open("file22", 'w') { |file| file.write("Hi Ruby22!") }
File.open("file33", 'w') { |file| file.write("Hi Ruby33!") }
"""


class TestYamt(unittest.TestCase):

    def setUp(self):
        f = open("yamtfile", "w")
        f.write(FILE1)
        f.close()

    def test_something(self):
        main.yamt(FILE1)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
