import os, re, os.path, sys, shutil
for root, dirs, files in os.walk(sys.argv[1]):
  for name in files:
    if name.startswith('PANO'):
      newname = 'IMG' + name[4:]
      src = os.path.join(root, name)
      dst = os.path.join(root, newname)
      print "%s -> %s" % (src, dst)
      shutil.move(src, dst)
