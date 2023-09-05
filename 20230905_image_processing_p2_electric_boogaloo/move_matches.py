import sys
import os
from pathlib import Path
import shutil
import cv2
import face_recognition

match_dir = "match"
src_dir = "faces"
dest_dir = "good"

CACHE = {}

all_files = ( os.path.join(basedir, filename) for basedir, dirs, files in os.walk(match_dir) for filename in files   )
sorted_files = sorted(all_files, key = os.path.getsize)
sorted_files.reverse()

count = 0

for f in sorted_files:
    filename = os.path.basename(f)
    if (filename not in CACHE):
        CACHE[filename] = True
        count += 1
        size_of_file  = os.stat(f).st_size
        basename = Path(f).stem
        
        print("SCANNING "+basename+" / "+str(size_of_file))
        
        src = os.path.join(src_dir, basename)
        dst = os.path.join(dest_dir, str(size_of_file)+"_"+basename)
        shutil.copyfile(src, dst)

        file1 = open(f, 'r')
        Lines = file1.readlines()
        for line in Lines:
            nextname = line.strip()+".txt"
            CACHE[nextname] = True

print(count)
