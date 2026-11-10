pimport os
import cv2
import numpy as np
import shutil
import requests
import csv

os.environ["FFMPEG_BINARY"] = "/usr/local/Cellar/ffmpeg/4.1_1/bin/ffmpeg"
from moviepy.editor import *
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader

filename = "../test-data/2017-11-23 08-24-16.mp4"
filename = "../test-data/v.avi"
filename = "../test-data/BERGWEIHNACHT.mp4"

def generateOMimage (filename, nr, inPointOMimage, outPointOMimage):
    print("generateOMimage ", inPointOMimage, outPointOMimage, outPointOMimage-inPointOMimage,  "====================================================")

    abspath = os.path.abspath(filename)
    basename = os.path.basename(abspath)
    dirname = os.path.dirname(abspath)
    omimagedir = os.path.join(dirname, basename.rsplit('.', 1)[0] + ".omimagedata")

    oMimageDuration = outPointOMimage - inPointOMimage

    cap = cv2.VideoCapture(filename)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH ))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)
    #print( length, width, height, fps )

    STRIPEPARTWIDTH = 1500
    stripeToRead = oMimageDuration
    stripeToReadRemaining = stripeToRead;

    firstStripeImage = int ( inPointOMimage / STRIPEPARTWIDTH )
    lastStripeImage  = int ( (outPointOMimage-1) / STRIPEPARTWIDTH )

    startInFirstStripeImage = inPointOMimage - firstStripeImage * STRIPEPARTWIDTH
    endInLastStripeImage    = outPointOMimage - lastStripeImage * STRIPEPARTWIDTH

    print ("firstStripeImage = ", firstStripeImage, "startInFirstStripeImage = ", startInFirstStripeImage  )
    print ("lastStripeImage = ",  lastStripeImage,  "endInLastStripeImage = ",     endInLastStripeImage )

    SMALLIMAGEWITH = 100
    BIGIMAGEWITH   = SMALLIMAGEWITH * 5
    SMALLIMAGEHEIGHT = int (SMALLIMAGEWITH * float(height) / float (width) + 0.5)
    BIGIMAGEHEIGTH   = int (BIGIMAGEWITH * float(height) / float (width) + 0.5)
    STRIPEHEIGHT     = int (BIGIMAGEHEIGTH)


    numberofbigimages = int ((oMimageDuration) / (5 * fps) + 0.5)

    if (numberofbigimages==0):
        numberofbigimages = 1

    numberofsmallimages = int (numberofbigimages * 5)
    print(numberofbigimages, numberofsmallimages)

    fdeltasmall = oMimageDuration / numberofsmallimages
    fdeltabig   = oMimageDuration / numberofbigimages

    omimageheight = BIGIMAGEHEIGTH + SMALLIMAGEHEIGHT + STRIPEHEIGHT
    omimagewidth  = numberofsmallimages * SMALLIMAGEWITH

    print(omimagewidth, omimageheight)

    omimage = np.zeros((omimageheight,omimagewidth,3), np.uint8)
    scale = omimagewidth / oMimageDuration
    print ("oMimageDuration = ", oMimageDuration, "omimagewidth", omimagewidth, "scale" , scale )

    xstripeimagesin = 0
    xstripeimagesout = 0
    for i in range(firstStripeImage, lastStripeImage+1):
        startx = 0
        endx   = STRIPEPARTWIDTH
        if (i == firstStripeImage):
            startx = startInFirstStripeImage
        if (i == lastStripeImage):
             endx = endInLastStripeImage

        xstripeimagesout = xstripeimagesin + (endx - startx)

        xstripeimagesinScaled   = int (xstripeimagesin * scale + 0.5)
        xstripeimagesoutScaled  = int (xstripeimagesout * scale + 0.5)

        print("copy to (scaled) ", xstripeimagesinScaled, xstripeimagesoutScaled)

        stripeCacheImageFileName = os.path.join(omimagedir, "ist_%05d.jpg" % i)
        print("READ stripe cache nr ", i, "look for data in ", startx, endx, endx-startx)


        stripecCacheImage = cv2.imread(stripeCacheImageFileName, 3)
        sheight, swidth, schannels = stripecCacheImage.shape
        stripecCacheImageSelected = stripecCacheImage [0:sheight, startx:endx]

        striptImageWidthScaled    = xstripeimagesoutScaled - xstripeimagesinScaled
        print ("final size = ", striptImageWidthScaled, STRIPEHEIGHT)

        stripecCacheImageScaled  = cv2.resize( stripecCacheImageSelected, (striptImageWidthScaled , STRIPEHEIGHT))


        ystart = SMALLIMAGEHEIGHT + BIGIMAGEHEIGTH
        yend = ystart + STRIPEHEIGHT
        omimage[ystart:yend, xstripeimagesinScaled:xstripeimagesoutScaled] = stripecCacheImageScaled
        xstripeimagesin = xstripeimagesout


    # get the small images
    for i in range(0, numberofsmallimages):
    #    print (i, i%5)
        fn = int (inPointOMimage + i * fdeltasmall + 0.5)
        cap.set(cv2.CAP_PROP_POS_FRAMES, fn)
        sucess, capturedimage = cap.read()
        imgsmall = cv2.resize(capturedimage, (SMALLIMAGEWITH, SMALLIMAGEHEIGHT))

        ystart = BIGIMAGEHEIGTH+1
        yend   = ystart + SMALLIMAGEHEIGHT
        xstart = i * SMALLIMAGEWITH
        xend   = (i+1) * SMALLIMAGEWITH

        omimage[ystart:yend, xstart:xend] = imgsmall

        if (i%5==0):
            ib = i / 5
            fn = int(inPointOMimage + fdeltabig/2 + ib * fdeltabig+ 0.5)
            cap.set(cv2.CAP_PROP_POS_FRAMES, fn)
            sucess, capturedimage = cap.read()
            imgbig = cv2.resize(capturedimage, (BIGIMAGEWITH, BIGIMAGEHEIGTH))
            ystart = 0
            yend   = BIGIMAGEHEIGTH
            xstart = i * SMALLIMAGEWITH
            xend   = xstart +  BIGIMAGEWITH
    #        print(BIGIMAGEWITH, BIGIMAGEHEIGTH, xstart, xend)
            omimage[ystart:yend, xstart:xend] = imgbig


    seconds = (inPointOMimage / fps ) % 60
    minutes = (inPointOMimage / fps / 60) % 60
    hours  = (inPointOMimage / fps / 60/ 60) % 60

    fn = os.path.join(omimagedir, "a_%05d_%02d_%02d_%02d.jpg" % (nr, hours, minutes, seconds ) )
    cv2.imwrite(fn,  omimage)

    print (numberofbigimages, numberofsmallimages)


filename = "../test-data/BERGWEIHNACHT.mp4"
filename = "../test-data/v.avi"

abspath = os.path.abspath(filename)
basename = os.path.basename(abspath)
dirname = os.path.dirname(abspath)
omimagedir = os.path.join(dirname, basename.rsplit('.', 1)[0] + ".omimagedata")
fn = os.path.join(omimagedir,"_scenes.csv")

with open(fn, mode='r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        print(row[0], row[1])
        generateOMimage(filename, line_count, int(row[0]), int(row[1]))
        line_count += 1