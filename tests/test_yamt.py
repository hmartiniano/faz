#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_yamt
----------------------------------

Tests for `yamt` module.
"""
import os
import glob

import unittest

from yamt import main, parser

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


FILE2 = """
# Using bash as the interpreter
# file1, file2 <-
touch file3 file4
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
"""

FILE3 = """
# Using bash as the interpreter
# file1, file2 <-
touch file3 file4
"""

FILE4 = """
# Using bash as the interpreter
# file3, file4 <- file1, file2
touch file3 file4
"""


FILE5 = """
# Using bash as the interpreter
# file1, file2 <-
touch file5
touch file1 file2

# file3, file4 <- file1, file2
touch file3, file4

# file5 <- file3, file4
touch file5
"""


FILE6 = """
# Using bash as the interpreter
# file21, file22 <-
touch file21 file22

# file3, file4 <- file2*
touch file3, file4
"""


class TestYamt(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        main.yamt(FILE1)

    def tearDown(self):
        for fname in glob.glob("file*"):
            os.unlink(fname)


class TestMain(unittest.TestCase):

    def setUp(self):
        f = open("yamtfile", "w")
        f.write(FILE1)
        f.close()

    def test_something(self):
        main.main(arguments=[])

    def tearDown(self):
        for fname in glob.glob("file*"):
            os.unlink(fname)
        os.unlink("yamtfile")


class TestMainDebug(unittest.TestCase):

    def setUp(self):
        f = open("yamtfile", "w")
        f.write(FILE1)
        f.close()

    def test_something(self):
        main.main(arguments=["-v"])

    def tearDown(self):
        for fname in glob.glob("file*"):
            os.unlink(fname)
        os.unlink("yamtfile")


class TestMissingInput(unittest.TestCase):

    def setUp(self):
        pass

    @unittest.expectedFailure
    def test_something(self):
        main.yamt()

    def tearDown(self):
        pass


class TestMissingInputs(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        main.yamt(FILE2)

    def tearDown(self):
        for fname in glob.glob("file*"):
            os.unlink(fname)


class TestYAMTFileInDir(unittest.TestCase):

    def setUp(self):
        for fname in glob.glob(".yamt/tmp*"):
            os.remove(fname)
        os.rmdir(".yamt")
        f = open(".yamt", "w")
        f.close()

    @unittest.expectedFailure
    def test_something(self):
        main.yamt(FILE1)

    def tearDown(self):
        os.unlink(".yamt")


class TestOuputsNotCreated(unittest.TestCase):

    def setUp(self):
        pass

    @unittest.expectedFailure
    def test_something(self):
        main.yamt(FILE3)

    def tearDown(self):
        pass


class TestInputsDoNotExist(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        main.yamt(FILE4)

    def tearDown(self):
        pass


class TestOutputsAreOlderThanInputs(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        main.yamt(FILE5)

    def tearDown(self):
        pass


class TestWildcardInName(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        main.yamt(FILE6)

    def tearDown(self):
        pass


class TestOldParser(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        tasks = parser.old_parser(FILE1)
        self.failUnlessEqual(6, len(tasks))

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main(verbosity=3)
