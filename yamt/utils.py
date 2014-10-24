# -*- coding: utf-8 -*-
import os
import glob


def expand_filenames(filenames):
    results = []
    for filename in filenames:
        if "*" in filename:
            results.extend(glob.glob(filename))
        else:
            results.append(filename)
    results.sort()
    return results


def files_exist(filenames):
    """ Check if all files in a given list exist. """
    return all([os.path.exists(filename) and os.path.isfile(filename)
                for filename in filenames])


def dependencies_are_newer(files, dependencies):
    """ For two lists of files, check if any file in the
        second list is newer than any file of the first.
    """
    dependency_mtimes = [
        os.path.getmtime(filename) for filename in dependencies]
    file_mtimes = [os.path.getmtime(filename) for filename in files]
    results = []
    for file_mtime in file_mtimes:
        for dependency_mtime in dependency_mtimes:
            if dependency_mtime > file_mtime:
                results.append(True)
            else:
                results.append(False)
    return any(results)
