import cv2
import mediapipe as mp
import time
from google.protobuf.json_format import MessageToDict
import math


class handDetector():
    def __init__(self,mode=False,maxhand = 2,detectionCon = 0.5, trackingCon = 0.5):
        self.mode = mode
        self.maxhand = maxhand
        self.detectionCon = detectionCon
        self.trackingCon = trackingCon
        self.mpHand = mp.solutions.hands
        self.hands = self.mpHand.Hands(static_image_mode=mode,
               max_num_hands=maxhand,
               min_detection_confidence=detectionCon,
               min_tracking_confidence=trackingCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findhand(self,frame,draw=True):

        imgRGB = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        self.RESULTS = self.hands.process(imgRGB)

        if self.RESULTS.multi_hand_landmarks:
            for handLms in self.RESULTS.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(frame,handLms,self.mpHand.HAND_CONNECTIONS)
        return frame
    def findPosition(self,frame,handno =0,draw = True):

        self.lmlist =[]
        xcoor = []
        ycoor = []
        boundary = []
        #minx , miny = 0,0
        #maxx , maxy = 0,0
        LorRHand = None
        #imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #self.RESULTS = self.hands.process(imgRGB)
        #print('Handedness:', RESULTS.multi_handedness)

        if self.RESULTS.multi_hand_landmarks:
            for idx, hand_handedness in enumerate(self.RESULTS.multi_handedness):
                handedness_dict = MessageToDict(hand_handedness)
                LorRHand=handedness_dict['classification'][0]['label']
                #print(handedness_dict['classification']['label'])#(ind,score,label) = RESULTS.multi_handedness
            myHand = self.RESULTS.multi_hand_landmarks[handno]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xcoor.append(cx)
                ycoor.append(cy)
                #print(id, cx, cy)
                self.lmlist.append([id,cx,cy,LorRHand])
            minx , miny = min(xcoor),min(ycoor)
            maxx , maxy = max(xcoor),max(ycoor)
            boundary = minx , miny , maxx , maxy
            if draw:
               cv2.rectangle(frame,(boundary[0]-20,boundary[1]-20),(boundary[2]+20,boundary[3]+20),(255,0,0),2)
        return self.lmlist , boundary

    def fingersUp(self):
        fingers = []
        # Thumb
        if self.lmlist[self.tipIds[0]][1] > self.lmlist[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Fingers
        for id in range(1, 5):

            if self.lmlist[self.tipIds[id]][2] < self.lmlist[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        # totalFingers = fingers.count(1)

        return fingers

    def findDistance(self, p1, p2, img, draw=True,r=15, t=3):
        x1, y1, label1 = self.lmlist[p1][1:]
        x2, y2, label2 = self.lmlist[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if label1 == label2:

            if draw:
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
                cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
            length = math.hypot(x2 - x1, y2 - y1)

            return length, img, [x1, y1, x2, y2, cx, cy]
        else:

            return None,None, [None]





def main():
    cap = cv2.VideoCapture(0)
    points =[]
    detector = handDetector(detectionCon=0.7)

    while True:
        _, frame = cap.read()
        frame = detector.findhand(frame)
        handlist , bbox = detector.findPosition(frame)

        if len(handlist) != 0:
            #print(handlist[4])
            #fingerup = detector.fingersUp()
            dis,frame,points = detector.findDistance(8,12,frame,True,5,1)
            print(dis)


        cv2.imshow('image', frame)
        cv2.waitKey(1)






if __name__ == "__main__":
    main()
