import numpy as np
import cv2
import pafy


url = 'https://youtu.be/W1yKqFZ34y4'
vPafy = pafy.new(url)
play = vPafy.getbest(preftype="webm")

# start the video
cap = cv2.VideoCapture(play.url)
i = 0
while (True):
    ret, frame = cap.read()
    """
    your code....
    """

    cv2.imwrite('frame%04d.jpg' % i, frame)
    i +=1
cap.release()
