from PIL import Image
from PIL.ExifTags import TAGS
from os import listdir
from os.path import isdir, isfile, join, split
from pprint import pprint

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

if __name__ == '__main__':
  import sys
  directory = sys.argv[1]
  files = [ join(directory,f) for f in listdir(directory) if isfile(join(directory,f)) ]
  for f in files:
    pprint(get_exif(f))
