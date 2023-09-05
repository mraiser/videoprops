import sys
import os
import cv2
import face_recognition

check_dir = "raw"
save_dir = "faces"
min_side = 200

if not os.path.exists(save_dir):
  os.mkdir(save_dir)

def process(filename):
    f = os.path.join(check_dir, filename)
    if os.path.isfile(f) and (filename.endswith(".png") or filename.endswith(".jpg")):
        oimg = cv2.imread(f)
        if oimg is None:
            print("NOT A READABLE IMAGE: "+filename)
        else:
            face_locations = face_recognition.face_locations(oimg)
            if (len(face_locations) > 0):
                faceclip = face_locations[0]
                faceclip = [faceclip[3],faceclip[0],faceclip[1],faceclip[2]]
                img2 = oimg[faceclip[1]:faceclip[3], faceclip[0]:faceclip[2]]
                foundw = img2.shape[1] 
                foundh = img2.shape[0]
                if foundw >= min_side and foundh >= min_side:
                    f2 = os.path.join(save_dir, filename)
                    cv2.imwrite(f2, img2)

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

