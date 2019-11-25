#!/usr/bin/python
import PIL
from PIL import Image
from PIL.ExifTags import TAGS
import re
import os
import sys

# import the debug module
sys.path.append(os.path.abspath('../'))
import debug as dbg

# set debug constants
CRITICAL = dbg.CRITICAL
INFO = dbg.INFO
VERBOSE = dbg.VERBOSE
ALL = dbg.ALL

###################
# Resize
###################
# pixel value for the fixed short edge
fixed_edge_p = 1080
# 0 - 100
quality_level = 50

###################
# RET VAL
###################
# general success
SUCCESS = 0
# general error
ERROR = 1
# err no file
ERROR_NO_FILE = 2
# err no image
ERROR_NO_IMAGE = 3
# STRING output for the above
RET_STRING = ["SUCCESS", "ERROR", "ERROR_NO_FILE", "ERROR_NO_IMAGE"]

# returns ret_string based on given index ret_val
# Input:
#   ret_val: (INT) index to ret_string
# Output:
#   STRING
def getRetString(ret_val):
  if ret_val >= 0 and ret_val < len(RET_STRING):
    return RET_STRING[ret_val]
  else:
    return "UNDEFINED_RET_VAL"

###################
# PUBLIC FUNCTIONS
###################
# checks if file exists
def imageExists(image_path):
  if os.path.exists(image_path):
    return SUCCESS
  else:
    dbg.dprintln(1, "\tFILE DOES NOT EXIST: " + str(filename))
    return ERROR_NO_FILE

# check if jpg
def isJpg(filename):
  if imageExists(filename) == SUCCESS:
    if re.search('.jpg', filename, re.IGNORECASE):
      return SUCCESS
    else:
      dbg.dprintln(3, "\tNON-JPG IMAGE: " + str(filename))
      return ERROR_NO_IMAGE
  else:
    return ERROR_NO_FILE

# https://gist.github.com/tomvon/ae288482869b495201a0
def resizeImg(filename):
  if isJpg(filename) == SUCCESS:
    img = Image.open(filename)
    exif = img._getexif()
    dbg.dprintln(5, "WIDTH, HEIGHT: " + str(img.size[0]) + ", " + str(img.size[1]))
    # save short edge
    IS_WIDTH = True
    short_edge = img.size[0]
    # calculate percentages
    if img.size[0] > img.size[1]:
      short_edge = img.size[1]
      IS_WIDTH = False
    # check if short edge is already scaled, skip if so
    if short_edge <= fixed_edge_p:
      dbg.dprintln(4, "Resizing: SKIP")
      return
    else:
      dbg.dprintln(4, "Resizing: VALID")
    # calculate percentage
    wpercent = (fixed_edge_p/float(short_edge))
    # resize by short edge width
    if IS_WIDTH:
      long_edge = int((float(img.size[1])*float(wpercent)))
      img = img.resize((fixed_edge_p,long_edge), PIL.Image.ANTIALIAS)
    # resize by short edge height
    else:
      long_edge = int((float(img.size[0])*float(wpercent)))
      img = img.resize((long_edge,fixed_edge_p), PIL.Image.ANTIALIAS)
    # save exif data
    if exif is not None:
      for tag, value in exif.items():
        decoded = TAGS.get(tag, tag)
        if decoded == 'Orientation':
          if value == 3:
            img = img.rotate(180, expand=True)
          if value == 6:
            img = img.rotate(270, expand=True)
          if value == 8:
            img = img.rotate(90, expand=True)
    # save image
    try:
      img.save(filename, 'JPEG', quality=quality_level)
    except IOError as e:
      dbg.dprintln(1, "\tERROR SAVING FILE: " + str(filename))
  else:
    dbg.dprintln(1, "\tFILE DOES NOT EXIST: " + str(filename))


###################
# MAIN
###################
walk_dir = sys.argv[1]

dbg.dprintln(1, 'walk_dir = ' + walk_dir)

# If your current working directory may change during script execution, it's recommended to
# immediately convert program arguments to an absolute path. Then the variable root below will
# be an absolute path as well. Example:
# walk_dir = os.path.abspath(walk_dir)
dbg.dprintln(1, 'walk_dir (absolute) = ' + os.path.abspath(walk_dir))

for root, subdirs, files in os.walk(walk_dir):
    dbg.dprintln(1, '--\nroot = ' + root)
    for subdir in subdirs:
        dbg.dprintln(1, '\t- subdirectory ' + subdir)
    for filename in files:
        file_path = os.path.join(root, filename)
        resizeImg(file_path)
        dbg.dprintln(3, '\t- file %s (full path: %s)' % (filename, file_path))