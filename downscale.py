from wand.image import Image
import os
import os.path
# from os import listdir, rename, walk
# from os.path import abspath, commonprefix, isdir, isfile, join, split, splitext
import errno

# Copied verbatim from http://goo.gl/6J4uX
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

class DownscaleException(Exception):
  def __init__(self, arg):
      self.arg = arg


def downscale(img, pixels=3000000, width=None, height=None, compression_quality=92):
  if width is None or height is None:
    # compute width and height from input width and height and desired image size.
    ratio = float(img.height) / float(img.width)
    width = int((pixels / ratio)**(0.5))
    height = int((pixels * ratio)**(0.5))
  img.format = 'jpeg'
  img.compression_quality = compression_quality
  img.resize(width, height)
  return img


def clone_downscale_save(input_file, output_file, pixels=3000000,
                         width=None, height=None, compression_quality=92):
  orig = Image(filename=input_file)
  img = orig.clone()
  img = downscale(img, pixels, width, height, compression_quality)

  # Make sure output directory exists
  dirname, _basename = os.path.split(output_file)
  mkdir_p(dirname) # Noop if dir already exists
  img.save(filename=output_def)


def downscale_directory_tree(root, out_fmt, skip_non_jpeg=True, pixels=3000000,
                             width=None, height=None, compression_quality=92):
  root = os.path.abspath(root)
  for path, dirs, files in os.walk(root):
    for fn in files:
      fullname = os.path.join(path, fn)
      basename, ext = os.path.splitext(fn)
      # Example format string: "{orig_dir}/web_hq/{orig_base}_web_hq.{orig_ext}"
      outname = out_fmt.format(orig_dir=path, orig_base=basename, orig_ext=ext)
      outname = os.path.abspath(outname)
      # For security, make sure that outname is somewhere under the root
      # directory, otherwise bail.
      if os.path.commonprefix([outname, root]) != root:
        raise DownscaleException('Invalid output directory: %s is not under root %s' %
                                 (outname, root))

      # Make sure output filename has correct extension ('JPEG', 'JPG', 'jpg',
      # or 'jpeg').
      outbase, outext = os.path.splitext(outname)
      if outext.lower() != '.jpg' and outext.lower() != '.jpeg':
        if not skip_non_jpeg:
          raise DownscaleException('Invalid file extension %s for file %s' %
                                   (outext, outname))
        else:
          print 'Skipping non-jpeg file %s' % outname
          continue

      if os.path.exists(outname) and os.path.isfile(outname):
        print 'skipping existing file %s' % outname
        continue

      print "Converting %s to %s" % (fullname, outname)
      clone_downscale_save(fullname, outname, pixels, width, height, compression_quality)

if __name__ == '__main__':
  import sys
  try:
    downscale_directory_tree(sys.argv[1],
                             '{orig_dir}/web_hq/{orig_base}_web_hq{orig_ext}')
  except DownscaleException, e:
    print e.arg

