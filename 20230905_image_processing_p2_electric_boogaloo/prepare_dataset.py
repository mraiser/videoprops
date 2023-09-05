import sys
import os
import cv2
import face_recognition
import landmark as LM

check_dir = "good"
match_dir = "match"
raw_dir = "raw"
out_face = "lora/Image/face"
out_body = "lora/Image/body"
min_side = 200

body_detector = LM.Body()
min_volume = min_side * min_side
face_padding = [0.1,0.33,0.1,0.1]
body_padding = [0.1,0.1,0.1,0.1]
CACHE = {}

if not os.path.exists(out_face):
    os.makedirs(out_face)

if not os.path.exists(out_body):
    os.makedirs(out_body)

args = sys.argv[1:]
count = 0
n1 = 0
n2 = 1
if len(args) > 0:
    n1 = int(args[0]) - 1
    n2 = int(args[1])

def pad(a, w, h, d):
    foundw = a[2]-a[0] 
    foundh = a[3]-a[1]
    
    a[0] -= int(foundw * d[0])
    a[2] += int(foundw * d[2])
    a[1] -= int(foundh * d[1])
    a[3] += int(foundh * d[3])
    
    if a[0] < 0: 
        a[0] = 0
    if a[1] < 0: 
        a[1] = 0
    if a[2] > w: 
        a[2] = w
    if a[3] > h: 
        a[3] = h
    
    return a

def bounds(points, w, h):
  minx = w + 1
  miny = h + 1
  maxx = -1
  maxy = -1
  
  for point in points:
    if point[1] < minx:
      minx = point[1]
    if point[1] > maxx:
      maxx = point[1]
    if point[2] < miny:
      miny = point[2]
    if point[2] > maxy:
      maxy = point[2]
      
  if maxx < 0:
    return None
  if maxy < 0:
    return None
  if minx > w:
    return None
  if miny > h:
    return None


  if minx < 0:
    minx = 0
  if miny < 0:
    miny = 0
  if maxx > w:
    maxx = w
  if maxy > h:
    maxy = h
    
  if maxx < minx or maxy < miny:
    return None
  
  return [minx, miny, maxx, maxy]

def bod(oimg):
  img1 = cv2.cvtColor(oimg, cv2.COLOR_BGR2RGB)
  
  imgw = img1.shape[1]
  imgh = img1.shape[0]

  allbody = body_detector.Find_Points(oimg, img1)
  if len(allbody) == 0:
    return None
  
  return bounds(allbody, imgw, imgh)

def grab(filename):
    global n1, n2, count
    if filename not in CACHE:
        CACHE[filename] = True
        
        b = False
        i = hash(filename)
        if i % n2 == n1:
            f = os.path.join(raw_dir, filename)
            oimg = cv2.imread(f)
            w = oimg.shape[1]
            h = oimg.shape[0]
            
            face_locations = face_recognition.face_locations(oimg)
            faceclip = face_locations[0]
            faceclip = [faceclip[3],faceclip[0],faceclip[1],faceclip[2]]
            
            foundw = faceclip[2] - faceclip[0] #img2.shape[1] 
            foundh = faceclip[3] - faceclip[1] #img2.shape[0]
            
            founda = foundw * foundh
            if founda >= min_volume:
                xxx = pad(faceclip, w, h, face_padding)
                img2 = oimg[xxx[1]:xxx[3], xxx[0]:xxx[2]]
                f2 = os.path.join(out_face, "FACE_"+str(founda)+"_"+filename)
                cv2.imwrite(f2, img2)
                b = True
            
            check = bod(oimg)
            
            if check != None:
                a = [[-1,faceclip[0],faceclip[1]],[-1,faceclip[2],faceclip[3]],[-1,check[0],check[1]],[-1,check[2],check[3]]]
                a = bounds(a, w, h)
                foundw = a[2]-a[0] 
                foundh = a[3]-a[1]
                founda = foundw * foundh
                if founda >= min_volume:
                    a = pad(a, w, h, body_padding)
                    img2 = oimg[a[1]:a[3], a[0]:a[2]]
                    face_locations = face_recognition.face_locations(img2)
                    if len(face_locations) == 1:
                        f2 = os.path.join(out_body, "BODY_"+str(founda)+"_"+filename)
                        cv2.imwrite(f2, img2)
                        b = True
            if b:
                count += 1

def process(filename):
    i = filename.index("_")
    filename = filename[i+1:]
    grab(filename)
    f = os.path.join(match_dir, filename+".txt")
    file1 = open(f, 'r')
    Lines = file1.readlines()
    for line in Lines:
        nextname = line.strip()
        grab(nextname)    

for filename in os.listdir(check_dir):
    process(filename)

print(count)

