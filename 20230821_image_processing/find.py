import sys
import os
import cv2
import face_recognition
import landmark as LM

check_dir = "raw"
save_dir = "found"
target_size = 1024
min_size = 768
SIMILAR = 0.6
FACE = True
BODY = True
RESIZE = False

good_images = [
    "good/a0_b121333869.png",
    "good/a0_b-963490375.png",
    "good/a0_b-1128207254.png",
    "good/a58250102_b73213112.png"
]

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

min_volume = min_size * min_size
good_encodings = []
for img in good_images:
    known_image = cv2.imread(img)
    known_encoding = face_recognition.face_encodings(known_image)[0]
    good_encodings.append(known_encoding)
    
body_detector = LM.Body()

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
  
  return [minx, miny, maxx, maxy]

def bod(oimg):
  img1 = cv2.cvtColor(oimg, cv2.COLOR_BGR2RGB)
  
  imgw = img1.shape[1]
  imgh = img1.shape[0]
  #res = [imgw, imgh]

  #allface = face_detector.Find_Points(oimg, img1)
  #print(allface)
  #head = None
  #if len(allface) > 0:
  #  head = bounds([allface[103],allface[298],allface[338],allface[336]], imgw, imgh)

  allbody = body_detector.Find_Points(oimg, img1)
  if len(allbody) == 0:
    return [None, None]
    
  chest = bounds([allbody[11], allbody[12], allbody[23], allbody[24]], imgw, imgh)
  legs = bounds([allbody[23], allbody[27], allbody[24], allbody[28]], imgw, imgh)
  #return [res, head, chest, legs]
  return [chest, legs]
  
def numfaces(img):
  try:
    locs = face_recognition.face_locations(img)
    return len(locs)
  except:
    print("ERROR")
    return 0

def bestfit(img1, nextloc, padpercent):
  left = nextloc[0]
  top = nextloc[1]
  right = nextloc[2]
  bottom = nextloc[3]
  h = bottom - top
  w = right - left
  
  padw = w + (w * padpercent)
  padh = h + (h * padpercent)
  
  nmax = min(img1.shape[0], img1.shape[1], max(padw, padh, target_size))
  
  dw = (nmax - w) / 2
  dh = (nmax - h) / 2
  
  left = max(left - dw, 0)
  right = min(right + dw, img1.shape[1])
  w = right - left
  
  if w < nmax:
    if left == 0:
      right = nmax
      w = nmax
    else:
      left = max(right - nmax, 0)
      right = left + nmax
      w = nmax
      
  top = max(top - max(dh,0), 0)
  bottom = min(bottom + dh, img1.shape[0])
  h = bottom - top
  
  if h < nmax:
    if top == 0:
      bottom = nmax
      h = nmax
    else:
      top = max(bottom - nmax, 0)
      bottom = top + nmax
      h = nmax
  
  if w > h:
    right -= w - h
    w = right - left
  elif w < h:
    bottom -= h - w
    h = bottom - top
  
  nextloc = (int(left), int(top), int(right), int(bottom))
  return nextloc
  
def process(filename):
    f = os.path.join(check_dir, filename)
    if os.path.isfile(f) and (filename.endswith(".png") or filename.endswith(".jpg")):
        oimg = cv2.imread(f)
        if oimg is None:
            print("NOT A READABLE IMAGE: "+filename)
        else:
            unknown_encodings = face_recognition.face_encodings(oimg)
            b = False
            i = 0
            for unknown_encoding in unknown_encodings:
                results = face_recognition.compare_faces(good_encodings, unknown_encoding, tolerance=SIMILAR)
                for result in results:
                    if result:
                        b = True
                        
                        face_locations = face_recognition.face_locations(oimg)
                        faceclip = face_locations[i]
                        faceclip = [faceclip[3],faceclip[0],faceclip[1],faceclip[2]]
                        
                        img2 = oimg[faceclip[1]:faceclip[3], faceclip[0]:faceclip[2]]
                        foundw = img2.shape[1] 
                        foundh = img2.shape[0]
                        if FACE and foundw * foundh >= min_volume:
                            xxx = bestfit(oimg, faceclip, 0)
                            img2 = oimg[xxx[1]:xxx[3], xxx[0]:xxx[2]]
                            if RESIZE:
                                img2 = cv2.resize(img2, (target_size,target_size))
                            if numfaces(img2) == 1:
                                f2 = os.path.join(save_dir, "FACE_"+filename)
                                cv2.imwrite(f2, img2)
                        
                        if i == 0:
                            [chest, legs] = bod(oimg)
                            
                            check = legs
                            if check is None:
                                check = chest
                            
                            if check != None:
                                xxx = bestfit(oimg, faceclip, 0.5)
                                a = [[-1,xxx[0],xxx[1]],[-1,xxx[2],xxx[3]],[-1,check[0],check[1]],[-1,check[2],check[3]]]
                                w = oimg.shape[1]
                                h = oimg.shape[0]
                                a = bounds(a, w, h)
                                foundw = a[2]-a[0] 
                                foundh = a[3]-a[1]
                                if BODY and foundw * foundh >= min_volume:
                                    #r = int(2.5*foundh/foundw)
                                    xxx = bestfit(oimg, a, 0)
                                    img2 = oimg[xxx[1]:xxx[3], xxx[0]:xxx[2]]
                                    if RESIZE:
                                        img2 = cv2.resize(img2, (target_size,target_size))
                                    if numfaces(img2) == 1:
                                        f2 = os.path.join(save_dir, "BODY_"+filename)
                                        cv2.imwrite(f2, img2)
                        
                        break
                if b:
                    break
                i += 1

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

