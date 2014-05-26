from PIL import Image
from PIL.ExifTags import TAGS
import datetime
from os import listdir, rename
from os.path import isdir, isfile, join, split
from pprint import pprint
import string

def get_exif(fn):
    ret = {}
    try:
      i = Image.open(fn)
      info = i._getexif()
    except (IOError, AttributeError):
      # Not an image file. Return an empty dict.
      return ret
    if info is None:
      return ret
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret

def exif_date_to_ts(exif_date):
  # Given a date in exif format, return a unix timestamp
  try:
    dt = datetime.datetime.strptime(exif_date, '%Y:%m:%d %H:%M:%S')
    return int(dt.strftime('%s'))
  except:
    return None

def strip_punctuation(input_str):
  return input_str.translate(string.maketrans("",""), string.punctuation)

def get_oldest_date_in_folder(files):
  # Returns the oldest creation date of all images in the folder as a unix timestamp
  oldest_ts = None
  for f in files:
    fd = open(f)
    exiftags = get_exif(fd)
    creation_ts = None
    if 'DateTimeOriginal' in exiftags:
      creation_ts = exif_date_to_ts(exiftags['DateTimeOriginal'])
    elif 'DateTime' in exiftags:
      creation_ts = exif_date_to_ts(exiftags['DateTime'])
    if creation_ts is not None and (oldest_ts is None or creation_ts < oldest_ts):
      oldest_ts = creation_ts
  return oldest_ts

def rename_directory_with_oldest_photo_date(directory):
  files = [ join(directory,f) for f in listdir(directory) if isfile(join(directory,f)) ]
  prefix_ts = get_oldest_date_in_folder(files)
  if prefix_ts is None:
    print 'No valid photo data in directory', directory
    return
  prefix_formatted = datetime.datetime.fromtimestamp(prefix_ts).strftime('%Y-%m-%d-')
  pathhead, dirname = split(directory)
  new_dirname = prefix_formatted + '-'.join(
    [s.lower() for s in strip_punctuation(dirname).split()])
  new_dirname = join(pathhead, new_dirname)
  print 'Renaming dir %s to %s' % (directory, new_dirname)
  rename(directory, new_dirname)


if __name__ == '__main__':
  import sys
  topdir = sys.argv[1]
  directories = [ join(topdir,d) for d in listdir(topdir) if isdir(join(topdir,d)) ]
  pprint(directories)
  for directory in directories:
    rename_directory_with_oldest_photo_date(directory)

