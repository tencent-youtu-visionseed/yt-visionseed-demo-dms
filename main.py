import visionseed as vs
import serial
import time
import numpy as np
import cv2
from collections import deque
import pygame

datalink = vs.YtDataLink( serial.Serial("/dev/ttyACM0",115200,timeout=0.5) )
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_CONVERT_RGB, True)
if (cap.isOpened() == False):
    print("Unable to read camera feed")
    exit(0)
ringEyeOpenTotal=4
ringHasPersonTotal=20
ringEyeOpen=deque([],maxlen=ringEyeOpenTotal)
ringHasPerson=deque([],maxlen=ringHasPersonTotal)
working=False

pygame.mixer.init()

def reallyClosed():
    for i in range(len(ringEyeOpen)):
        if ringEyeOpen[i] == 0:
            return False
    return len(ringEyeOpen) == ringEyeOpenTotal;

def afterBlink():
    if len(ringEyeOpen) != ringEyeOpenTotal:
        return False
    if ringEyeOpen[0] != 0 or ringEyeOpen[len(ringEyeOpen) - 2] != 1 or ringEyeOpen[len(ringEyeOpen) - 1] != 0:
        return False
    return True

def reallyNewPerson():
    global working
    if (len(ringHasPerson)) != ringHasPersonTotal:
        return False
    curAllOne = True
    curAllZero = True
    for i in range(len(ringHasPerson)):
        if ringHasPerson[i] == 0:
            curAllOne = False
        else:
            curAllZero = False

    if (working==False and curAllOne):
        working=True
        print("Enter\n")
        return 1

    elif (working == True and curAllZero):
        working = False
        print("Leave\n")
        ringEyeOpen.clear()
        return 2

    return 0

def millis():
    t=time.time()
    return (int(round(t*1000)))

def checkEyeBlink(hasPerson):
    last = 0
    ts = millis()
    blinkCount = 0
    print('[afterBlink]:',afterBlink())
    if afterBlink():
        if hasPerson:
            blinkCount += 1
            print("[Blink] detected!\n")
    if (ts - last > 60000):
        print("[Blink] last minute count:%d\n" % blinkCount)
        blinkCount = 0
        last = ts

def main():
    openness=[1,1]
    MIN_FACE=100
    playingWelcome=False
    while True:
        if (cap.isOpened()):
                ret,frame=cap.read()
                cv2.namedWindow('frame',cv2.WINDOW_NORMAL)
                cv2.setWindowProperty('frame',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                cv2.imshow('frame',frame)
                cv2.waitKey(1)
        result,msg=datalink.recvRunOnce()
        if result:
            YtVisionSeedModel=vs.YtDataLink.YtVisionSeedModel
            biggestArea=0
            hasPerson=False
            rect=result.getResult([YtVisionSeedModel.FACE_DETECTION,0])
            if(rect):
                if(rect.w*rect.h>biggestArea):
                    biggestArea=rect.w*rect.h
                pose=result.getResult([YtVisionSeedModel.FACE_DETECTION,0,YtVisionSeedModel.FACE_POSE])
                shape=result.getResult([YtVisionSeedModel.FACE_DETECTION,0,YtVisionSeedModel.FACE_LANDMARK])
                if(shape):
                    shape=shape.faceShape
                    yaw=pose.array[1]
                    vec1f=np.array([shape.leftEye[6].x,shape.leftEye[6].y])
                    vec2f=np.array([shape.leftEye[2].x,shape.leftEye[2].y])
                    l1=np.sqrt(np.sum(np.square(vec1f-vec2f)))
                    vec3f=np.array([shape.leftEye[0].x,shape.leftEye[0].y])
                    vec4f=np.array([shape.leftEye[4].x,shape.leftEye[4].y])
                    l2=np.sqrt(np.sum(np.square(vec3f-vec4f)))
                    openness[0]=l1/l2
                    vec1r=np.array([shape.rightEye[6].x,shape.rightEye[6].y])
                    vec2r=np.array([shape.rightEye[2].x,shape.rightEye[2].y])
                    r1=np.sqrt(np.sum(np.square(vec1r-vec2r)))
                    vec3r=np.array([shape.rightEye[0].x,shape.rightEye[0].y])
                    vec4r=np.array([shape.rightEye[4].x,shape.rightEye[4].y])
                    r2=np.sqrt(np.sum(np.square(vec3r-vec4r)))
                    openness[1]=r1/r2
                    hasPerson=biggestArea > MIN_FACE*MIN_FACE
                    eyeclosed=openness[0 if yaw<0 else 1]<0.1

                    if(working and hasPerson):
                        if(len(ringEyeOpen) == ringEyeOpenTotal):
                            ringEyeOpen.pop()
                        ringEyeOpen.appendleft(eyeclosed)
                        if(reallyClosed()):
                            # 可以打断welcome
                            if playingWelcome or not pygame.mixer.music.get_busy():
                                print('ALARM')
                                playingWelcome=False
                                pygame.mixer.music.load("alarming.mp3")
                                pygame.mixer.music.play()
                    '''checkEyeBlink(working and hasPerson)'''

            if (len(ringHasPerson) == ringHasPersonTotal):
                ringHasPerson.pop()
            ringHasPerson.appendleft(hasPerson)
            rnp = reallyNewPerson()
            if (rnp == 1):
                print('WELCOME')
                playingWelcome=True
                pygame.mixer.music.load("welcome.mp3")
                pygame.mixer.music.play()

            elif (rnp == 2):
                print('BYE')
                pygame.mixer.music.load("bye.mp3")
                pygame.mixer.music.play()

if __name__=='__main__':
    main()
