#give flag to each object to see at end of while loop whether this object was present in this frame or not from obj_list

import cv2
import os
import shutil
from scipy.interpolate import interp1d
from os import path
import feature_extraction

obj_list=[]
all_obj=[]
threshold_frame=5

class Object:
    def __init__(self):
        self.tid=-1
        self.path=[]
        self.exist=False
        self.enter_frame=-1
        self.exit_frame=-1
        self.slope=0
        self.duration=0
        self.box=[]
        
    def save(self,x,y,w,h,tid,point,enter_frame,exit_frame):
        self.box.append((x,y,w,h))
        self.tid=tid
        self.path.append(point)
        self.enter_frame=int(enter_frame)
        self.exit_frame=int(exit_frame)

        
def inbetween(xc,yc):
    res=[]
    
    for tobj in obj_list:
        if(xc>=tobj.box[len(tobj.box)-1][0] and xc<=(tobj.box[len(tobj.box)-1][0]+tobj.box[len(tobj.box)-1][2]) and yc>=tobj.box[len(tobj.box)-1][1] and yc<=(tobj.box[len(tobj.box)-1][1]+tobj.box[len(tobj.box)-1][3])):
            res.append(tobj)    
    return res
      
def print_path(tobj,frame):
    if(len(tobj.path)>=2):
         for i in range(0, len(tobj.path), 1):  
               if(i+1<len(tobj.path)):
                   cv2.line(frame,tobj.path[i],tobj.path[i+1],(255,255,255),5)         
    #cv2.line(frame1,tobj.path[0],tobj.path[len(tobj.path)-1],(255,255,255),5)         
              
def fill_all_obj():
    for i in obj_list:
        if(all_obj.count(i)==0):
            all_obj.append(i)
   
def match_slope(obj1,obj2):  
    if( int(obj1.slope//1) == int(obj2.slope//1)): 
        temp1=str(abs(obj1.slope*100000))
        temp2=str(abs(obj2.slope*100000))
        
        if(temp1[0] == temp2[0]):            
                return 1
        else:
                return 0   
    else:
        return 0
           
def match_duration(obj1,obj2):
    if(obj1.duration in range(obj2.duration-1,obj2.duration+2)):
        return 1
    else:
        return 0
    
def match_image(obj1,obj2):
    w_diff= obj1.box[threshold_frame][2]-obj2.box[threshold_frame][2]
    h_diff= obj1.box[threshold_frame][3]-obj2.box[threshold_frame][3]
    
    if(abs(w_diff)<=8 and abs(h_diff)<=8):
        path1= "Input Frame/{}.jpg".format(obj1.enter_frame+threshold_frame)
        temp1= cv2.imread(path1)
        crop_img1 = temp1[obj1.box[threshold_frame][1]:obj1.box[threshold_frame][1]+obj1.box[threshold_frame][3], obj1.box[threshold_frame][0]:obj1.box[threshold_frame][0]+obj1.box[threshold_frame][2]]

        path2= "Input Frame/{}.jpg".format(obj2.enter_frame+threshold_frame)
        temp2= cv2.imread(path2)
        crop_img2 = temp2[obj2.box[threshold_frame][1] : (obj2.box[threshold_frame][1]+obj2.box[threshold_frame][3]) , obj2.box[threshold_frame][0] : (obj2.box[threshold_frame][0]+obj2.box[threshold_frame][2]) ]
        
        w_final=h_final=0
        
        if( (obj1.box[threshold_frame][2]-obj2.box[threshold_frame][2]) < 0 ):
            w_final=obj1.box[threshold_frame][2]
        else:
            w_final=obj2.box[threshold_frame][2]
            
        if( (obj1.box[threshold_frame][3]-obj2.box[threshold_frame][3]) < 0 ):
            h_final=obj1.box[threshold_frame][3]
        else:
            h_final=obj2.box[threshold_frame][3]
            
        crop_img1=cv2.resize(crop_img1,(w_final,h_final))
        crop_img2=cv2.resize(crop_img2,(w_final,h_final))

        SSIM=feature_extraction.process(obj1, obj2, threshold_frame)
        if(SSIM > 0.50):
            return SSIM
        else:
            return 0
    else:
        return 0
              
def check_forgery(): 
   for check_obj in all_obj:
            for cur_obj in all_obj:
                 if(cur_obj!=check_obj and check_obj.slope!=0 and cur_obj.slope!=0 and check_obj.duration>threshold_frame and cur_obj.duration>threshold_frame):
                    if(match_slope(check_obj,cur_obj)==1):
                        if(match_duration(check_obj,cur_obj)==1):
                            SSIM=match_image(check_obj, cur_obj)
                            if(SSIM>0.5):
                                return [check_obj,cur_obj,check_obj.slope,check_obj.duration,check_obj.box[threshold_frame][2],check_obj.box[threshold_frame][3],SSIM]  
   return None                        
    
def initialize_files(video_name): 
    if(path.exists("Input Frame")):
        shutil.rmtree("Input Frame")
    if(path.exists("Output")):
        shutil.rmtree("Output") 
    if(path.exists("Process Frame")):
        shutil.rmtree("Process Frame")
    os.mkdir("Input Frame")
    os.mkdir("Output") 
    os.mkdir("Process Frame") 
    if(path.exists(video_name)):
        cap = cv2.VideoCapture(video_name)
        return cap   
    else:
        return None  
    
def main(fname,first_window):
    
    cap=initialize_files(fname)  
    obj_list.clear()
    all_obj.clear()

    if( cap is None ):
        print("\n\nNo File Found ")
        return None

    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_rate=cv2.CAP_PROP_FPS
    total_frames=cap.get(cv2.CAP_PROP_FRAME_COUNT)
    frames_remaining=total_frames
    print("Frames Remaining"+str(frames_remaining))
    
    original_fname=gray_fname=box_fname=fourcc=None

    if(fname.endswith(".mp4")):
        original_fname="Output/Original_video.mp4"
        gray_fname="Output/Gray_video.mp4"
        box_fname="Output/Box_video.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'MPEG')
    elif(fname.endswith(".avi")):
        original_fname="Output/Original_video.avi"
        gray_fname="Output/Gray_video.avi"
        box_fname="Output/Box_video.avi"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    else:
        return None
    
    original_video = cv2.VideoWriter(original_fname, fourcc, 25, (width, height))
    gray_video = cv2.VideoWriter(gray_fname, fourcc, 25, (width, height),isColor=False)
    box_video = cv2.VideoWriter(box_fname, fourcc, 25, (width, height))

    map = interp1d([0,frames_remaining],[0,100])
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    frames_remaining-=2

    cnt=1
    x_new_center=y_new_center=0
    flag=False
    count_frame=0
    
    while cap.isOpened():
      if(frame1 is not None and frame2 is not None):
        
        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        cv2.imwrite("Input Frame/%d.jpg" % count_frame, frame1)
        
        #cv2.imshow("Grey",gray)
        original_video.write(frame1)
        gray_video.write(gray)

        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        
        dilated = cv2.dilate(thresh, None, iterations=3)
        _,contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for i in obj_list:
            i.exist=False
        temp_flag=False
            
        for contour in contours:
            
            if cv2.contourArea(contour) < 900:
                continue
            frame_no=cap.get(cv2.CAP_PROP_POS_FRAMES)-2
            tid=-1
            
            (x, y, w, h) = cv2.boundingRect(contour)
            x_new_center=x+int(w/2)
            temp_flag=True
            y_new_center=y+int(h/2)
                    
            res=inbetween(x_new_center,y_new_center)
            if(len(res)>=1):
                tobj=res[0]
                tid=tobj.tid
                tobj.exist=True
                tobj.save(x,y,w,h,tid,(x_new_center,y_new_center),tobj.enter_frame,frame_no)
            else:
                tobj=Object()
                tid=cnt
                cnt+=1
                tobj.exist=True
                tobj.save(x,y,w,h,tid,(x_new_center,y_new_center),frame_no,frame_no)
                obj_list.append(tobj)
                
            #print('Object :- {}  and contour :- {}'.format(tobj.tid,cv2.contourArea(contour)))
            cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 255), 2)
           
            print_path(tobj,frame1)
            
            if(flag==False):
                flag=True
            
        #cv2.putText(frame1,"X:-{} and y:-{}".format(x_new_center,y_new_center),(5, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255),2)
        #cv2.drawContours(frame1, contours, -1, (0, 255, 255), 2)
        fill_all_obj()
        for i in obj_list:
            if(i.exist==False):
                obj_list.remove(i)
            
    
        if(temp_flag is False):
            flag=False
            obj_list.clear()

        #image = cv2.resize(frame1, (1280,720))
        #cv2.imshow("Result", frame1)
        box_video.write(frame1)
        cv2.imwrite("Process Frame/%d.jpg" % count_frame, frame1)

        count_frame+=1
        frame1 = frame2
        ret, frame2 = cap.read()
        frames_remaining-=1

        if(frames_remaining%10==0):
            first_window.progressBar.setValue(int(map(total_frames-frames_remaining)))  
      if cv2.waitKey(1)==-1 and frames_remaining==0:#& 0xFF == ord('q'):
            break
    #cv2.destroyAllWindows()  
    original_video.release()
    gray_video.release()
    box_video.release()
    cap.release()
    
    for tobj in all_obj:
        if((tobj.path[len(tobj.path)-1][0]-tobj.path[0][0]) !=0):
             tobj.slope = (tobj.path[len(tobj.path)-1][1]-tobj.path[0][1]) / (tobj.path[len(tobj.path)-1][0]-tobj.path[0][0])  #(tobj.path[1][1]-tobj.path[0][1]) / (tobj.path[1][0]-tobj.path[0][0])
             tobj.duration=tobj.exit_frame-tobj.enter_frame
             #print('Object:- {}  and Enter Frame:- {}  and Exit Frame:- {}'.format(tobj.tid,tobj.enter_frame,tobj.exit_frame) )
             #print('Object :- {}  and Slope={} and Duration={}'.format(tobj.tid,tobj.slope,tobj.duration))
    

    match_list=check_forgery()
    
    if(match_list is None):
        print('\n\nNo Forgery Detected.')
        Results={
            'result':'Original'
        }
    else:
        #print('\nForged objects are {}  and  {} \n'.format(match_list[0].tid , match_list[1].tid))
        forged_image_path="Input Frame/{}.jpg".format(match_list[1].enter_frame+threshold_frame)
        if(path.exists(forged_image_path)):
            forged_image= cv2.imread(forged_image_path)
            #forged_image= cv2.resize(forged_image, (1280,720))
            #cv2.rectangle(forged_image, (match_list[1].box[threshold_frame][0],match_list[1].box[threshold_frame][1]) , (match_list[1].box[threshold_frame][0]+match_list[1].box[threshold_frame][2],match_list[1].box[threshold_frame][1]+match_list[1].box[threshold_frame][3]),(0, 255, 0), 2)
            #cv2.putText(forged_image, 'Forged Frame:- {}  and  {}'.format(match_list[0].enter_frame + threshold_frame , match_list[1].enter_frame + threshold_frame) ,(30,70), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255),2)        
            #print('\n\nForged Object Start Frame:- {} and {}'.format(match_list[0].enter_frame,match_list[1].enter_frame))
            Results={
                'result':'Forged',
                'slope':match_list[2],
                'duration':match_list[3],
                'height':match_list[4],
                'width':match_list[5],
                'SSIM':match_list[6],
                'original_frame':match_list[0].enter_frame,
                'copied_frame':match_list[1].enter_frame
            }
        else:
            print("Forged Image Not Found in the Directory")
            Results={
                'result':'Error'
            }
    return Results
