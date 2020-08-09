import cv2
import math, time
import numpy as np
import pydirectinput,keyboard
#import threading


def nothing(x):
     pass

# def press_key():
#     if direction==-1:
#         pydirectinput.keyDown('left')
#         # time.sleep(0.5)
#         # pydirectinput.keyUp('left')
#         print('left')

#     elif direction==1:
#         pydirectinput.keyDown('right')
#         # time.sleep(0.5)
#         # pydirectinput.keyUp('right')
#         print('right')
            
if __name__ == "__main__":
    cap= cv2.VideoCapture(0)        #18,132,84-yellow   and 79,100,12  162-violet
    press_count= 0
    
    # cv2.namedWindow('trackbar')
    # cv2.createTrackbar('h', 'trackbar', 121, 255, nothing)
    # cv2.createTrackbar('s', 'trackbar',55, 255, nothing)
    # cv2.createTrackbar('v', 'trackbar', 60, 255, nothing)
    # cv2.createTrackbar('h2', 'trackbar', 176, 255, nothing)
    # cv2.createTrackbar('s2', 'trackbar', 227, 255, nothing)
    # cv2.createTrackbar('v2', 'trackbar', 190, 255, nothing)

    last_direction=0
    #left_key=right_key=0    
    while True:
        _, frame= cap.read()
        frame= cv2.flip(frame,1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # h = cv2.getTrackbarPos('h', 'trackbar')
        # s = cv2.getTrackbarPos('s', 'trackbar')
        # v = cv2.getTrackbarPos('v', 'trackbar')
        # h2 = cv2.getTrackbarPos('h2', 'trackbar')
        # s2 = cv2.getTrackbarPos('s2', 'trackbar')
        # v2 = cv2.getTrackbarPos('v2', 'trackbar')

        # Normal masking algorithm
        lower1 = np.array([111, 102, 72])#([h,s,v])# 
        upper1 = np.array([176, 227, 190])#([h2,s2,v2])#

        mask1 = cv2.inRange(hsv, lower1, upper1)
        #cv2.imshow('temp',mask1)
        #ret,thresh = cv2.threshold(mask1, 40, 255, 0)
        #dilated = cv2.dilate(thresh, None, iterations=1)
        contours1, hierarchy = cv2.findContours(mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        #c1=None
        if len(contours1) != 0:
            c1 = max(contours1, key = cv2.contourArea)
        
        lower2 = np.array([19, 132, 84])#([h,s,v]) 
        upper2 = np.array([91, 255, 255])#([h2,s2,v2]) 
        
        mask2 = cv2.inRange(hsv, lower2, upper2)
        #ret,thresh2 = cv2.threshold(mask2, 40, 255, 0)
        #dilated2 = cv2.dilate(thresh2, None, iterations=1)
       
        #c2=None
        contours2, hierarchy2 = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(contours2) != 0 :
            c2 = max(contours2, key = cv2.contourArea)
        
        if cv2.contourArea(c1)>12000 and cv2.contourArea(c2)>12000:
            x1,y1,w1,h1 = cv2.boundingRect(c1)
            cv2.rectangle(frame,(x1,y1),(x1+w1,y1+h1),(255,0,0),2)
        
            x2,y2,w2,h2 = cv2.boundingRect(c2)
            cv2.rectangle(frame,(x2,y2),(x2+w2,y2+h2),(255,0,0),2)

            #cv2.line(frame,(x2+int(w2/2),y2+int(h2/2)),(frame.shape[1],y2+int(h2/2)),(0,0,255),5)
            cv2.line(frame,(x1+int(w1/2),y1+int(h1/2)),(x2+int(w2/2),y2+int(h2/2)),(0,255,0),5)
            
            angleInDegrees = math.atan2((y2-y1), (x2-x1)) * 180 / math.pi
            if angleInDegrees!= None:# and not key_thread.is_alive() :
                #print(angleInDegrees)
                if angleInDegrees>0 and angleInDegrees<170:
                    if last_direction!=-1:
                        if keyboard.is_pressed('right'):
                            pydirectinput.keyUp('right')
                        #direction=-1
                        last_direction=-1
                        pydirectinput.keyDown('left')
                        #print('left')
                        # key_thread= threading.Thread(target=press_key)
                        # key_thread.start()
                elif angleInDegrees<0 and angleInDegrees>-170:
                    if last_direction!=1:
                        if keyboard.is_pressed('left'):
                            pydirectinput.keyUp('left')
                        #direction=1
                        last_direction=1
                        pydirectinput.keyDown('right')
                        #print('right')
                        # key_thread= threading.Thread(target=press_key)
                        # key_thread.start()
                else:
                    #print('Stop')
                    if keyboard.is_pressed('left'):
                        pydirectinput.keyUp('left')
                    if keyboard.is_pressed('right'):    
                        pydirectinput.keyUp('right')
                    last_direction=0
        cv2.imshow('Camera', frame)
        
        k = cv2.waitKey(2) & 0xFF
        if k == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
