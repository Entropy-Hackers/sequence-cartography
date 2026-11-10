import os
import cv2
import numpy as np
import csv
import pafy

import scenedetect
from scenedetect.video_manager  import VideoManager
from scenedetect.scene_manager  import SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.stats_manager  import StatsManager
from scenedetect.detectors      import ContentDetector

url = 'https://youtu.be/O0Kfl2wgLtE'
url = 'https://youtu.be/aWWAeGx0noA'
url = 'https://youtu.be/qvpOIqvX3vQ'
url = 'https://youtu.be/NIM6n-c1ugE'   # die magie der schallplatte
url = 'https://youtu.be/4iwyvroMhDE'   # der henker von london

filename = "../test-data/2017-11-23 08-24-16.mp4"

readFromYoutube = 1
detectscene = 1
generateStripes = 0
makeOMImages = 0

def generateOMimage (cap, omimagedir, nr, inPointOMimage, outPointOMimage):

    oMimageDuration = outPointOMimage - inPointOMimage
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH ))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)

    seconds = (inPointOMimage / fps) % 60
    minutes = (inPointOMimage / fps / 60) % 60
    hours = (inPointOMimage / fps / 60 / 60) % 60

    omimagefilename = os.path.join(omimagedir, "a_%05d_%02d_%02d_%02d.jpg" % (nr, hours, minutes, seconds))

    if os.path.exists(omimagefilename):
        return
    else:
        print("generateOMimage Nr", nr, inPointOMimage, outPointOMimage, outPointOMimage - inPointOMimage)

    STRIPEPARTWIDTH = 1500
    stripeToRead = oMimageDuration
    stripeToReadRemaining = stripeToRead;

    firstStripeImage = int ( inPointOMimage / STRIPEPARTWIDTH )
    lastStripeImage  = int ( (outPointOMimage-1) / STRIPEPARTWIDTH )

    startInFirstStripeImage = inPointOMimage - firstStripeImage * STRIPEPARTWIDTH
    endInLastStripeImage    = outPointOMimage - lastStripeImage * STRIPEPARTWIDTH

    # print ("firstStripeImage = ", firstStripeImage, "startInFirstStripeImage = ", startInFirstStripeImage  )
    # print ("lastStripeImage = ",  lastStripeImage,  "endInLastStripeImage = ",     endInLastStripeImage )

    SMALLIMAGEWITH = 100
    BIGIMAGEWITH   = SMALLIMAGEWITH * 5
    SMALLIMAGEHEIGHT = int (SMALLIMAGEWITH * float(height) / float (width) + 0.5)
    BIGIMAGEHEIGTH   = int (BIGIMAGEWITH * float(height) / float (width) + 0.5)
    STRIPEHEIGHT     = int (BIGIMAGEHEIGTH)


    numberofbigimages = int ((oMimageDuration) / (5 * fps) + 0.5)

    if (numberofbigimages==0):
        numberofbigimages = 1

    numberofsmallimages = int (numberofbigimages * 5)
    # print(numberofbigimages, numberofsmallimages)

    fdeltasmall = oMimageDuration / numberofsmallimages
    fdeltabig   = oMimageDuration / numberofbigimages

    omimageheight = BIGIMAGEHEIGTH + SMALLIMAGEHEIGHT + STRIPEHEIGHT
    omimagewidth  = numberofsmallimages * SMALLIMAGEWITH


    omimage = np.zeros((omimageheight,omimagewidth,3), np.uint8)
    scale = omimagewidth / oMimageDuration
    # print ("oMimageDuration = ", oMimageDuration, "omimagewidth", omimagewidth, "scale" , scale )

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

        # print("copy to (scaled) ", xstripeimagesinScaled, xstripeimagesoutScaled)

        stripeCacheImageFileName = os.path.join(omimagedir, "ist_%05d.jpg" % i)
        # print("READ stripe cache nr ", i, "look for data in ", startx, endx, endx-startx)


        stripecCacheImage = cv2.imread(stripeCacheImageFileName, 3)
        sheight, swidth, schannels = stripecCacheImage.shape
        stripecCacheImageSelected = stripecCacheImage [0:sheight, startx:endx]

        striptImageWidthScaled    = xstripeimagesoutScaled - xstripeimagesinScaled
        # print ("final size = ", striptImageWidthScaled, STRIPEHEIGHT)

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

    cv2.imwrite(omimagefilename,  omimage)

    # print (numberofbigimages, numberofsmallimages)


# READ THE VIDEO

dirname = "/Users/Shared/SWD/VIDEO-ANALYZER/test-data"

abspath  = os.path.abspath(filename)
basename = os.path.basename(abspath)
dirname  = os.path.dirname(abspath)
omimagedir = os.path.join (dirname, basename.rsplit('.', 1)[0] + ".omimagedata")

if (readFromYoutube):
    omimagedirname = url.rsplit('/', 1)[-1]
    omimagedir     =  os.path.join(dirname, omimagedirname)
else:
    abspath = os.path.abspath(filename)
    basename = os.path.basename(abspath)
    dirname = os.path.dirname(abspath)
    omimagedir = os.path.join(dirname, basename.rsplit('.', 1)[0] + ".omimagedata")


fnscenes = os.path.join(omimagedir,"_scenes.csv")

if  not os.path.exists(omimagedir):
    os.mkdir(omimagedir)


if detectscene:

    if (readFromYoutube):
        vPafy = pafy.new(url)
        play = vPafy.getbest(preftype="webm")
        cap = cv2.VideoCapture(play.url)
    else:
        cap = cv2.VideoCapture(filename)

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    print("OPENING THE VIDEO WITH ", length, width, height, fps)

    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)
    scene_manager.add_detector(ContentDetector(threshold=35.0, min_scene_len=25))
    scene_manager.detect_scenes(frame_source=cap)

    basetimecode = FrameTimecode(timecode = 0, fps = fps)
    scene_list = scene_manager.get_scene_list(basetimecode)

    print('')
    print('List of scenes obtained:')

    with open(fnscenes, mode='w') as scene_file:
        scene_writer = csv.writer(scene_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i, scene in enumerate(scene_list):
            print('    Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
                i+1,
                scene[0].get_timecode(), scene[0].get_frames(),
                scene[1].get_timecode(), scene[1].get_frames(),))
            scene_writer.writerow([scene[0].get_frames(), scene[1].get_frames()])




if generateStripes:

    if (readFromYoutube):
        vPafy = pafy.new(url)
        play = vPafy.getbest(preftype="webm")
        cap = cv2.VideoCapture(play.url)
    else:
        cap = cv2.VideoCapture(filename)

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    maxstripesize = 1500
    stripeImage = np.zeros((height,maxstripesize,3), np.uint8)

    count    = 0
    countsec = 0
    countbig = 0
    seconds  = 0
    stripeimagecounter = 0
    stripenumber       = 0
    writelaststripe = 0

    success = 1
    while success:

        success, image = cap.read()

        if (success):
            stripe = image [0:height, int(width/2):int(width/2)+1]
            stripeImage [0:height, stripeimagecounter:stripeimagecounter+1] = stripe

            count    += 1
            countsec += 1
            countbig += 1
            stripeimagecounter +=1

            if  (countsec==2*fps):
                countsec = 0
                seconds +=2

            if (countbig == 10*fps):
                countbig = 0

            if (stripeimagecounter == maxstripesize):
                fn = os.path.join(omimagedir, "ist_%05d.jpg" % stripenumber)
                cv2.imwrite(fn,  stripeImage)
                stripeImage = np.zeros((height, maxstripesize, 3), np.uint8)
                stripeimagecounter = 0
                stripenumber += 1
                writelaststripe = 1

    if (writelaststripe):
        fn = os.path.join(omimagedir, "ist_%05d.jpg" % stripenumber)
        cv2.imwrite(fn, stripeImage)

    print (count+1, " frames found, theory = ", length)



if makeOMImages:

    if (readFromYoutube):
        vPafy = pafy.new(url)
        play = vPafy.getbest(preftype="webm")
        cap = cv2.VideoCapture(play.url)
    else:
        cap = cv2.VideoCapture(filename)

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    with open(fnscenes, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            # print(row[0], row[1])
            generateOMimage(cap, omimagedir, line_count, int(row[0]), int(row[1]))
            line_count += 1