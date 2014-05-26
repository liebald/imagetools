from os import listdir, rename, walk
from os.path import isdir, isfile, join, split, splitext
from pprint import pprint
import string


if __name__ == '__main__':
  import sys
  masterdir = sys.argv[1]
  otherdirs = sys.argv[2:]
  masterfiles = listdir(masterdir)
  for otherdir in otherdirs:
    renamed = []
    otherfiles = listdir(otherdir)
    for fn in otherfiles:
      fullname = join(otherdir, fn)
      if not isdir(fullname) and fn not in masterfiles:
        rename(fullname, join(otherdir, '__REMOVE__' + fn))
        renamed.append(fullname)
    print 'In Directory %s renamed the following files (%d): %s' % (
      otherdir, len(renamed), str(renamed))
