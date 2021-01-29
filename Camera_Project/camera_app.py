import tkinter as tk
import cv2
import numpy as np
from PIL import Image, ImageTk
import time
from datetime import datetime
import training
import face_recognition

default_cam = 0
fps = 5

class CamProgram:
    def __init__(self,win):

        image_empty = np.zeros([480,640,3], np.uint8)
        cv_img = cv2.cvtColor(image_empty, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv_img);
        self.empty_image= ImageTk.PhotoImage(image = img)

        self.is_cam_open = False

        # FRAMES
        main_frame = tk.Frame(win)
        cam_frame = tk.Frame(main_frame)
        right_frame = tk.Frame(main_frame)

        main_frame.grid(row = 0, column = 0)
        cam_frame.grid(row = 0, column = 0)
        right_frame.grid(row = 0, column = 1)

        # Camera Frame
        self.cam_label = tk.Label(cam_frame,image = self.empty_image)


        # Right Frame
        self.open_cam_button = tk.Button(right_frame,text = 'Open the Camera', command = self.open_cam_button_fnc)
        self.pause_cam_button = tk.Button(right_frame,text = 'Pause the Camera', command = self.pause_cam)
        self.close_cam_button = tk.Button(right_frame,text = 'Close the Camera', command = self.close_cam)


        # Placing Camera Frame
        self.cam_label.grid(row = 0, column = 0)

        # Placing Right Frame
        self.open_cam_button.grid(row = 0, column = 0)
        self.pause_cam_button.grid(row = 1, column = 0)
        self.close_cam_button.grid(row = 2, column = 0)


    def open_cam_button_fnc(self):
        global is_moving_stat
        global default_cam
        global fps
        is_moving_stat = False
        self.cap = cv2.VideoCapture(default_cam)
        ret, self.prev_frame = self.cap.read()
        ret, self.frame = self.cap.read()
        self.is_cam_open = True
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter('MyVideo.avi', self.fourcc, fps, (640,480))
        self.open_cam()


    def open_cam(self):
        global is_moving_stat
        global counter2
        global counter3
        if self.is_cam_open == True:
            self.open_cam_button['state'] = 'disabled'
            now = datetime.now()
            self.current_time = now.strftime("%d/%m/%Y %H:%M:%S")
            frm2 = self.frame.copy()
            cv2.putText(self.frame,self.current_time,(280,30),cv2.FONT_HERSHEY_SIMPLEX,1,[0,0,0],2)
            is_moving = self.motion_detection(frm2)
            if counter2 > 10:
                frame2 = self.check_face(frm2)
                counter2 = 0
            else:
                frame2 = frm2
            counter2 += 1
            cv2.putText(frm2,self.current_time,(280,30),cv2.FONT_HERSHEY_SIMPLEX,1,[0,0,0],2)
            frame_rgb = cv2.cvtColor(frame2,cv2.COLOR_BGR2RGB)
            if is_moving:
                cv2.putText(frame_rgb,'Movement',(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,[0,30,30],2)
                is_moving_stat = True

            if is_moving_stat == True:
                self.out.write(self.frame)
                counter3 += 1

            if counter3 == 50:
                counter3 = 0
                is_moving_stat = False

            frm = Image.fromarray(frame_rgb)
            frame_tk = ImageTk.PhotoImage(image = frm)
            self.cam_label.imgtk = frame_tk # Put image into the label
            self.cam_label.configure(image = frame_tk) # Set width and height according to camera
            self.frame = self.prev_frame
            ret, self.prev_frame = self.cap.read()
            self.cam_label.after(10,self.open_cam) # After 10ms it will call himself


    def pause_cam(self):
        self.is_cam_open = False
        self.cap.release()
        self.open_cam_button['state'] = 'normal'


    def close_cam(self):
        self.is_cam_open = False
        self.cap.release()
        self.open_cam_button['state'] = 'normal'
        self.cam_label.imgtk = self.empty_image # Put image into the label
        self.cam_label.configure(image = self.empty_image) # Set width and height according to picture


    def motion_detection(self,frm2):
        diff = cv2.absdiff(frm2,self.prev_frame)
        gray = cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray,(7,7), cv2.BORDER_DEFAULT)
        _,thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh,None,iterations = 3)
        _,contours,_ = cv2.findContours(dilated,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            (x,y,w,h) = cv2.boundingRect(contour)
            if cv2.contourArea(contour) > 100:
                # cv2.rectangle(frm2,(x,y),(x+w, y+h),(0,0,255),2)
                # font_1 = cv2.FONT_HERSHEY_SIMPLEX
                # cv2.putText(frm2,'Movement',(10,30),font_1,1,[0,30,30],2)
                return True
            else:
                return False
        # cv2.drawContours(self.frame,contours,-1,(0,255,0),2)

    def check_face(self,frm2):
        global face1
        global face2
        global face3
        global face4
        global names
        frame_rgb = cv2.cvtColor(frm2,cv2.COLOR_BGR2RGB)
        frame_rgb_resized = cv2.resize(frame_rgb,(0,0), fx = 1/4, fy = 1/4)
        counter = 0
        try:
            frame_face_locs = face_recognition.face_locations(frame_rgb_resized)
            frame_face_encodes = face_recognition.face_encodings(frame_rgb_resized,frame_face_locs)
            for face_encode in frame_face_encodes:
                check_person1 = face_recognition.compare_faces([face1],face_encode)
                check_person2 = face_recognition.compare_faces([face2],face_encode)
                check_person3 = face_recognition.compare_faces([face3],face_encode)
                check_person4 = face_recognition.compare_faces([face4],face_encode)
                y1,x2,y2,x1 = frame_face_locs[counter]
                y1 *= 4
                y2 *= 4
                x1 *= 4
                x2 *= 4
                cv2.rectangle(frm2,(x1,y1),(x2,y2),(100,145,10), 2)

                if check_person1[0]:
                    print(names[0])
                    cv2.putText(frm2,names[0],(x1+15,y2+15),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(255,25,10),2)
                    with open('People.csv','a') as f:
                        f.write( names[0]+','+self.current_time+'\n')
                elif check_person2[0]:
                    print(names[1])
                    cv2.putText(frm2,names[1],(x1+15,y2+15),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(255,25,10),2)
                    with open('People.csv','a') as f:
                        f.write( names[1]+','+self.current_time+'\n')
                elif check_person3[0]:
                    print(names[2])
                    cv2.putText(frm2,names[2],(x1+15,y2+15),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(255,25,10),2)
                    with open('People.csv','a') as f:
                        f.write( names[2]+','+self.current_time+'\n')

                elif check_person4[0]:
                    print(names[3])
                    cv2.putText(frm2,names[3],(x1+15,y2+15),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(255,25,10),2)
                    with open('People.csv','a') as f:
                        f.write( names[3]+','+self.current_time+'\n')

                else:
                    print('Bilinmeyen Kişi')
                    with open('People.csv','a') as f:
                        cv2.putText(frm2,'Bilinmeyen Kişi',(x1+15,y2+15),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(255,25,10),2)
                        f.write('Bilinmeyen Kişi,'+self.current_time+'\n')


                counter += 1
        except IndexError:
            pass
        return frm2
face1 = training.image_encoding0
face2 = training.image_encoding1
face3 = training.image_encoding2
face4 = training.image_encoding3
counter2 = 0
counter3 = 0
names = training.image_names
encodings = training.encodings
win = tk.Tk()
win.title('Camera Application')
prog = CamProgram(win)
win.mainloop()
