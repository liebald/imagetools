from PIL import Image
from PIL.ExifTags import TAGS
import datetime
from pprint import pprint
from os import listdir, rename, walk
from os.path import isdir, isfile, join, split, splitext
import json
import urllib2

def get_exif(fn):
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
  exiftags = get_exif(fn)
  creation_ts = None
  if 'DateTimeOriginal' in exiftags:
    creation_ts = exif_date_to_ts(exiftags['DateTimeOriginal'])
  elif 'DateTime' in exiftags:
    creation_ts = exif_date_to_ts(exiftags['DateTime'])
  return creation_ts


def getcoords(d, m, s, ind):
  # Calculate the total number of seconds,
  # 43'41" = (43*60 + 41) = 2621 seconds.

  sec = float((m * 60) + s)
  # The fractional part is total number of
  # seconds divided by 3600. 2621 / 3600 = ~0.728056

  frac = float(sec / 3600)
  # Add fractional degrees to whole degrees
  # to produce the final result: 87 + 0.728056 = 87.728056

  deg = float(d + frac)
  # If it is a West or S longitude coordinate, negate the result.
  if ind == 'W':
    deg = deg * -1

  if ind == 'S':
    deg = deg * -1

  return float(deg)

def getcoords_exif(exif):
  if not 'GPSInfo' in exif:
    return None

  # Latitude
  coords = exif['GPSInfo']

  # Check that all required fields are present.
  has_required_info = all(k in coords for k in [1,2,3,4])
  if not has_required_info:
    return None

  ind = coords[1]
  d = float(coords[2][0][0]) / float(coords[2][0][1])
  m = float(coords[2][1][0]) / float(coords[2][1][1])
  s = float(coords[2][2][0]) / float(coords[2][2][1])
  lat = float(getcoords(d, m ,s, ind))

  #Longitude
  ind = coords[3]
  d = float(coords[4][0][0]) / float(coords[4][0][1])
  m = float(coords[4][1][0]) / float(coords[4][1][1])
  s = float(coords[4][2][0]) / float(coords[4][2][1])

  lon = float(getcoords(d, m ,s, ind))

  return lat, lon

def locations_from_coords(coords):
  url = ('http://maps.googleapis.com/maps/api/geocode/json?latlng=%0.5f,%0.5f&sensor=false' %
         (coords[0], coords[1]))
  data = urllib2.urlopen(url)
  jsondata = json.load(data)
  formmatted_locations = []
  for result in jsondata['results']:
    if 'formatted_address' in result:
      formmatted_locations.append(result['formatted_address'])
  return formmatted_locations

if __name__ == '__main__':
  import sys
  topdir = sys.argv[1]
  for path, dirs, files in walk(topdir):
    for fn in files:
      fullname = join(path, fn)
      coords = getcoords_exif(get_exif(fullname))
      if coords:
        locations = locations_from_coords(coords)
        print fullname, coords, locations
