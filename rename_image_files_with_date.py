from PIL import Image
from PIL.ExifTags import TAGS
import exifread
import datetime
from os import rename, walk
from os.path import join, split, splitext
from pprint import pprint
import string


def get_exif_exifread(fn):
  ret = {}
  try:
    f = open(fn, 'rb')
    tags = exifread.process_file(f, details=False)
    for k, v in tags.iteritems():
      if k.startswith('EXIF '):
        ret[k[5:]] = str(v)
  except (IOError):
    print 'Error getting EXIF for file', fn
  return ret

def get_exif_pil(fn):
    ret = {}
    try:
      i = Image.open(fn)
      info = i._getexif()
    except (IOError, AttributeError):
      # Not an image file. Return an empty dict.
      print 'Error getting EXIF for file', fn
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


def get_creation_ts(fn):
  exiftags = get_exif_exifread(fn)
  creation_ts = None
  if 'DateTimeOriginal' in exiftags:
    creation_ts = exif_date_to_ts(exiftags['DateTimeOriginal'])
  elif 'DateTime' in exiftags:
    creation_ts = exif_date_to_ts(exiftags['DateTime'])
  return creation_ts


def strip_punctuation_except_extension(input_str):
  name, ext = splitext(input_str)
  stripped_name = name.translate(string.maketrans("",""), string.punctuation)
  if ext:
    stripped_name = '%s%s' % (stripped_name, ext)
  return stripped_name


def rename_file_with_photo_date(fn):
  creation_ts = get_creation_ts(fn)
  if creation_ts is None:
    print 'Not renaming file', fn
    return
  prefix_formatted = datetime.datetime.fromtimestamp(creation_ts).strftime(
    '%Y-%m-%d-%H-%M-%S-')
  top, basename = split(fn)
  new_fn = prefix_formatted + '-'.join(
    [s.lower() for s in strip_punctuation_except_extension(basename).split()])
  new_fn = join(top, new_fn)
  print 'Renaming file %s to %s' % (fn, new_fn)
  rename(fn, new_fn)


if __name__ == '__main__':
  import sys
  topdir = sys.argv[1]
  for path, dirs, files in walk(topdir):
    for fn in files:
      fullname = join(path, fn)
      rename_file_with_photo_date(fullname)

