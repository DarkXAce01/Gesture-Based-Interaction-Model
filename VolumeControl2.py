import cv2
import time
import numpy as np
import HandTrackModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 640, 480  # cap.set doesnt work for some reason

cap = cv2.VideoCapture(0)
pTime = 0
detector = htm.HandDetector(detectionCon=0.5)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volumeRange = volume.GetVolumeRange()
minVol = math.log(volumeRange[0],10)
maxVol = math.log(volumeRange[1],10)
vol=0
volBar=400
volPer = 0
print(volumeRange)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        #print(lmList[4], lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2
        length = math.hypot((x2-x1), (y2-y1))
        #print(length)

        cv2.circle(img, (x1, y1), 10, (255,0,255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255,0,255), cv2.FILLED)
        cv2.line(img, (x1,y1), (x2,y2), (255,0,255), 2) #Bungee Gum!!!
        cv2.circle(img, (cx,cy), 10, (255,0,255), cv2.FILLED)

        #lowest length = 28-32
        #highest length = 298-307
        #HandRange = 28-307
        #VolumeRange = -63.5-0

        vol = np.interp(length, [30,250],[minVol,maxVol])
        volBar = np.interp(length, [30, 250], [400, 150])
        volPer = np.interp(length, [30, 250], [0, 100])

        volume.SetMasterVolumeLevel(vol, None)
        print(int(length),vol)

        cv2.rectangle(img, (30,150), (85,400), (255,0,69), 3)
        cv2.rectangle(img, (30,int(volBar)), (85,400),(255,0,69),cv2.FILLED)
        cv2.putText(img, f": {int(volPer)}%", (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (250, 0, 69), 3)

        if length < 35:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f"FPS: {int(fps)}",(10,50), cv2.FONT_HERSHEY_SIMPLEX,1, (250,9,69), 3)

    cv2.imshow('Img ', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()