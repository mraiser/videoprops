import sys
import os
import cv2
import face_recognition

check_dir = "faces"
save_dir = "match"
SIMILAR = 0.4

CACHE = {}

def getEncodings(filename):
    if (filename in CACHE):
        return CACHE[filename]
    f = os.path.join(check_dir, filename)
    if os.path.isfile(f) and (filename.endswith(".png") or filename.endswith(".jpg")):
        oimg = cv2.imread(f)
        base_encodings = face_recognition.face_encodings(oimg)
        if (len(base_encodings) > 0):
            base_encodings = [ base_encodings[0] ]
            CACHE[filename] = base_encodings
            return base_encodings
    CACHE[filename] = []
    return []

def process(base_filename):
    #print("SCANNING "+base_filename)
    base_encodings = getEncodings(base_filename)
    if (len(base_encodings) > 0):
        base_encodings = [ base_encodings[0] ]
        base_i = hash(filename)
        for sample_filename in os.listdir(check_dir):
            sample_i = hash(sample_filename)
            if sample_i > base_i:
                sample_encodings = getEncodings(sample_filename)
                if (len(sample_encodings) > 0):
                    results = face_recognition.compare_faces(base_encodings, sample_encodings[0], tolerance=SIMILAR)
                    if (results[0]):
                        f3 = os.path.join(save_dir, base_filename+".txt")
                        f3 = open(f3, "a")  # append mode
                        f3.write(sample_filename+"\n")
                        f3.close()
                        f3 = os.path.join(save_dir, sample_filename+".txt")
                        f3 = open(f3, "a")  # append mode
                        f3.write(base_filename+"\n")
                        f3.close()
                        #print("yay")

args = sys.argv[1:]
count = 0
if len(args) > 0:
    n1 = int(args[0]) - 1
    n2 = int(args[1])
    for filename in os.listdir(check_dir):
        i = hash(filename)
        if i % n2 == n1:
            process(filename)
            count += 1
else:
    for filename in os.listdir(check_dir):
        process(filename)
        count += 1
  
print(count)

