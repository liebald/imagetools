from os import listdir, rename, walk
from os.path import isdir, isfile, join, split

def fix_extension(filename):
  fixed = None
  if filename.endswith('jpg') and not filename.endswith('.jpg'):
    fixed = filename[:-3] + '.jpg'
  if filename.endswith('jpeg') and not filename.endswith('.jpeg'):
    fixed = filename[:-3] + '.jpg'
  elif filename.endswith('jpgjpg'):
    fixed = filename[:-6] + '.jpg'
  elif filename.endswith('png') and not filename.endswith('.png'):
    fixed = filename[:-3] + '.png'


  if fixed is not None:
    print 'Renaming', filename
    rename(filename, fixed)


if __name__ == '__main__':
  import sys
  topdir = sys.argv[1]
  for path, dirs, files in walk(topdir):
    for fn in files:
      fullname = join(path, fn)
      fix_extension(fullname)
