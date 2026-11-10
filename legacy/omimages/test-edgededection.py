import os
import numpy as np
import cv2
import math
from matplotlib import pyplot as plt

filename = "../test-data/youtubeTEST.mp4"


abspath  = os.path.abspath(filename)
basename = os.path.basename(abspath)
dirname  = os.path.dirname(abspath)   
omimagedir = os.path.join (dirname, basename.rsplit('.', 1)[0] + ".omimagedata")

print (abspath)
print (basename)
print (dirname)
print (omimagedir)


fn = os.path.join(omimagedir, "ist_%05d.jpg" % 5)


img = cv2.imread(fn,3)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 0, 100)

cv2.imshow('image',img)

height, width = img.shape[:2]

verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(height / 4)))
kernel = np.array([[2,  -2],
                   [2,  -2],
                   [2,  -2]])
kernel2 = np.array([[-2,  2],
                   [-2,  2],
                   [-2,  2]])

lines = cv2.HoughLinesP(
    edges,
    rho=1,
    theta=np.pi/180,
    lines=np.array([]),
    threshold=5,
    minLineLength=30,
    maxLineGap=1  )

filteredStripe = cv2.filter2D(edges, -1, kernel)
filteredStripe2 = cv2.filter2D(edges, -1, kernel2)
dst1 = cv2.reduce(filteredStripe, 0,  cv2.REDUCE_SUM, dtype=cv2.CV_32S)
dst2 = cv2.reduce(filteredStripe2, 0, cv2.REDUCE_SUM, dtype=cv2.CV_32S)

dst3 = cv2.add(dst1, dst2)

print (dst3)
edgeRGB = cv2.cvtColor(edges,cv2.COLOR_GRAY2RGB)

for line in lines:
    print (line)
    x1, y1, x2, y2 = line[0]
    cv2.line(edgeRGB, (x1, y1), (x2, y2), (0, 255, 0), 1)
    if (x2==x1):
        cv2.line(edgeRGB, (x1, y1), (x2, y2), (0, 0, 255), 1)
    #slope = (y2 - y1) / (x2 - x1)  # <-- Calculating the slope.
    #if math.fabs(slope) > 3.05:  # <-- Only consider extreme slope
    #    cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 1)


cv2.imshow("Filetered Stripe", filteredStripe)
#cv2.imshow("Image", img)

cv2.imshow("Edges", edgeRGB)

cv2.waitKey(0)
cv2.destroyAllWindows()
    