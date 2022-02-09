from flask import Flask , render_template, request
import cv2
import HandMovement
from FPSUpgrade import FPS
from FPSUpgrade import WebcamVideoStream
import numpy as np
import math
import time
import autopy


###########

box = []
handlist = []
fingerup = []
smoothenagent = 8

plocX, plocY = 0, 0
clocX, clocY = 0, 0
i =0

# mouse_down =False
mouse_on_button = False
click_check = False
Hold_bool = False
switch = False
###########


   
def click_callback(event, x, y, flags, param):
    global mouse_on_button #,mouse_down
    mouse_on_button = False
    if x >= 150 and x <= 165 and y >= 150 and y <= 165:
            mouse_on_button = True
    

def blurarea(frame,hweb,wweb,InorOut = -1):
    global mouse_on_button
    h = int(hweb - 150)
    x = int(wweb-150)
    roi = frame[150:h,150:x]
    if InorOut == -1:
        frame = cv2.GaussianBlur(frame,(5,5),100)
        cv2.rectangle(frame, (150, 150), (x, h),
                        (255, 105, 255), 2)

    else:
        roi = cv2.GaussianBlur(frame,(5,5),10)
        cv2.rectangle(frame, (100, 100), (x, h),
                    (255, 100, 255), 2)

    frame[150:h,150:x] = roi

    if mouse_on_button == False:
        cv2.rectangle(frame, (150,150),(160,160), (255,0,0),-1)
        cv2.line(frame,(150,150),(160,160), (255,255,255),1)
        cv2.line(frame,(160,150),(150,160), (255,255,255),1)
    if mouse_on_button == True:
        cv2.rectangle(frame, (150,150),(165,165), (0,0,250),-1)
        cv2.line(frame,(150,150),(165,165), (255,255,255),1)
        cv2.line(frame,(165,150),(150,165), (255,255,255),1)
        cv2.rectangle(frame,(150,150),(168,168),(255,255,255),2)

    return frame


app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/vm")
def vm():
    global box,handlist,fingerup,smoothenagent,plocX,plocY,clocX,clocY,i,mouse_on_button,click_check,Hold_bool,switch

    detector = HandMovement.handDetector(detectionCon=0.7)

    videoCam = WebcamVideoStream(src=0).start()

    fps = FPS().start()

    hweb,wweb = videoCam.getWebcamHandW()

    screenW ,screenH = autopy.screen.size()


    cv2.namedWindow("frame")
    cv2.setMouseCallback("frame", click_callback)

    while True:

        frame = videoCam.read()

        frame = detector.findhand(frame,draw=False)
        handlist , box = detector.findPosition(frame,draw=False)

        if len(handlist) !=0:

            x1,y1,label1 = handlist[8][1:]
            x2, y2, label2 = handlist[12][1:]
            thumb_middle, image, lineInfo_thumbm = detector.findDistance(4,10,frame,False,2,1)
            middle_tip, image, lineInfo_thumb = detector.findDistance(10,11,frame,False,2,1)
            thumb_index, image, lineInfo_thumbI = detector.findDistance(4,8,frame,False,2,1)


            fingerup = detector.fingersUp()
            #
            if x1 >= 140 and x1<= (wweb-140):
                if y1 >= 140 and y1<= (hweb-140):
                    if fingerup[1]==1 and fingerup[2:5] == [0,0,0] and thumb_middle <= middle_tip  :


                        frame = blurarea(frame,hweb,wweb)
                        cv2.circle(frame, (handlist[8][1], handlist[8][2]), 5, (0, 11, 232), -1)
                        x3 = np.interp(x1,(150,wweb-150),(0,screenW))
                        y3 = np.interp(y1,(150,hweb-150),(0,screenH))
                        #
                        clocX = plocX + (x3 - plocX) / smoothenagent
                        clocY = plocY + (y3 - plocY) / smoothenagent

                        try:
                            autopy.mouse.move(screenW-clocX,clocY)
                            plocX, plocY = clocX, clocY

                        except:
                         pass
                    if fingerup[1] == 1 and fingerup[2] == 1 and fingerup[3] == 0 and mouse_on_button ==True:
                        # 9. Find distance between fingers
                        length, img, lineInfo = detector.findDistance(8, 12, frame,draw=False)
                        l2,i2,lf = detector.findDistance(8,7,frame,draw=False)
                        #print(length,l2)

                        # 10. Click mouse if distance short
                        if length <= l2 and click_check == False:
                            cv2.circle(img, (lineInfo[4], lineInfo[5]),
                                        15, (0, 255, 0), cv2.FILLED)
                            cv2.putText(frame,'Closing...',(160,300),cv2.FONT_HERSHEY_COMPLEX_SMALL,3,(10,255,10))

                            time.sleep(0.3)
                            break
                           
                    if fingerup[1] == 1 and fingerup[2] == 1 and fingerup[3] == 0:
                        # 9. Find distance between fingers
                        length, img, lineInfo = detector.findDistance(8, 12, frame,draw=False)
                        l2,i2,lf = detector.findDistance(8,7,frame,draw=False)
                        #print(length,l2)

                        # 10. Click mouse if distance short
                        if length <= l2 and click_check == False:
                            cv2.circle(img, (lineInfo[4], lineInfo[5]),
                                        15, (0, 255, 0), cv2.FILLED)
                            cv2.putText(frame,'Clicking..',(160,300),cv2.FONT_HERSHEY_COMPLEX_SMALL,3,(10,255,10))

                            time.sleep(0.3)
                            autopy.mouse.click()
                            click_check = True
                        if length > l2 and click_check:
                            click_check = False
                    
                        

            if x1 >= 150 and x1<= (wweb-150):
                if y1 >= 150 and y1<= (hweb-150):
                    if fingerup[1]==1 and fingerup[2:5] == [0,0,0] and thumb_index <= thumb_middle :

                        cv2.circle(frame, (x1, x2),15, (0, 255, 0), cv2.FILLED)
                        cv2.putText(frame, 'holding..', (160, 300), cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, (10, 255, 10))

                        if Hold_bool == False :
                            autopy.mouse.toggle(down = True,button = None)
                            Hold_bool = True

                        x3 = np.interp(x1, (150, wweb - 150), (0, screenW))
                        y3 = np.interp(y1, (150, hweb - 150), (0, screenH))
                        #
                        clocX = plocX + (x3 - plocX) / smoothenagent
                        clocY = plocY + (y3 - plocY) / smoothenagent

                        try:
                            autopy.mouse.move(screenW - clocX, clocY)
                            plocX, plocY = clocX, clocY

                        except:
                            pass

                        #time.sleep(0.5)
                        #if length > l2:
                        #   break
                        #length, img, lineInfo = detector.findDistance(4, 8, frame, draw=False)
                        #l2, i2, lf = detector.findDistance(8, 7, frame, draw=False)

                    if fingerup[1] == 1 and fingerup[2:5] == [0, 0, 0] and thumb_index >= thumb_middle and Hold_bool == True and switch == False:

                        switch = True
                        autopy.mouse.toggle(down=False, button=None)



                    if fingerup[1] == 1 and fingerup[2:5] == [0, 0, 0] and thumb_middle <= middle_tip and Hold_bool and switch:
                        cv2.putText(frame, 'not holding..', (160, 300), cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, (10, 10, 200))
                        Hold_bool = False
                        switch = False

                        #autopy.mouse.toggle(down=False, button=None)
                        '''
                        if length <= l2:
                            while True:
                        '''

        #print("hand in frame")

        cv2.imshow('frame',frame)

        k =cv2.waitKey(1)
        fps.update()
        if cv2.getWindowProperty('frame', cv2.WND_PROP_VISIBLE) <1:
            break
        if k == 27:
            break
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    cv2.destroyAllWindows()
    videoCam.stop()

    box = []
    handlist = []
    fingerup = []
    smoothenagent = 8

    plocX, plocY = 0, 0
    clocX, clocY = 0, 0
    i =0

    # mouse_down =False
    mouse_on_button = False
    click_check = False
    Hold_bool = False
    switch = False
    ###########

    return render_template('thankyoupage.html')
    

if __name__ == "__main__":
    app.run(debug=True)