import cv2
import pafy


print (cv2.__version__)

url = 'https://youtu.be/4iwyvroMhDE'
vPafy = pafy.new(url)
print(vPafy)
play = vPafy.getbest(preftype="webm")
print(play)
print(play.url)
cap = cv2.VideoCapture(play.url)

length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
print("OPENING THE VIDEO WITH ", length, width, height, fps)

