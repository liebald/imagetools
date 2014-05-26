import datetime
from os import listdir, makedirs, rename, walk
from os.path import isdir, isfile, join, split, splitext
from pprint import pprint
from shutil import move

import exiftools
import operator

def segment_images(path, files, dryrun):
  sequences = []
  current_sequence = []
  last_ts = None
  creation_ts_list = []
  for fn in files:
    fullpath = join(path, fn)
    creation_ts = exiftools.get_creation_ts(fullpath)
    if creation_ts is None:
      print 'Unable to determine creation timestamp for', fullpath
      continue
    creation_ts_list.append((creation_ts, fullpath))

  creation_ts_list.sort(key=operator.itemgetter(0))
  for creation_ts, fullpath in creation_ts_list:
    if last_ts is None:
      # Very first image. Create a new sequence
      current_sequence.append(fullpath)
    elif creation_ts - last_ts < 86400:
      # Image within 24 hours of the last one. Assume it's part of the same sequence.
      current_sequence.append(fullpath)
    else:
      # Create a new sequence. Add the old one to the list of sequences
      print "Creating new sequence. Last TS: %s - new TS: %s" % (
        datetime.datetime.fromtimestamp(last_ts).strftime('%Y-%m-%d-%H:%M:%S'),
        datetime.datetime.fromtimestamp(creation_ts).strftime('%Y-%m-%d-%H:%M:%S'))
      sequences.append(current_sequence)
      current_sequence = [fullpath]
    last_ts = creation_ts

  # Add the last sequences to the list
  if len(current_sequence) > 0:
    sequences.append(current_sequence)

  for sequence in sequences:
    creation_ts = exiftools.get_creation_ts(sequence[0])
    dirname = datetime.datetime.fromtimestamp(creation_ts).strftime('%Y-%m-%d')
    dirname = join(path, dirname)
    print 'creating dir', dirname
    if not dryrun:
      makedirs(dirname)
    for fn in sequence:
      print 'Moving file %s to dir %s' % (fn, dirname)
      if not dryrun:
        move(fn, dirname)



if __name__ == '__main__':
  import sys
  topdir = sys.argv[1]
  dryrun = False
  if len(sys.argv) > 2 and sys.argv[2] == '--dryrun':
    dryrun = True
    print "Dry Run"
  for path, dirs, files in walk(topdir):
    segment_images(path, files, dryrun)
