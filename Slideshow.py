import Tkinter as tk
from Tkinter import *
from tkFileDialog import askopenfilename
from tkMessageBox import *
import os
import cv2
import time
import operator
from PIL import Image, ImageTk, ImageOps
import subprocess
import sys



class Slideshow(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master=master

        self.left_cam, self.right_cam = self.enter_filename()    # get left and right image filenames that user selects
        
        self.master.focus_force()           # allows you to type in text boxex

        self.create_widgets()


    def create_widgets(self):
        '''
        Creates all the components that are displayed on the interface
        '''

        # open up left and right images
        self.left_frame = Image.open(self.left_cam)

        self.left_frame = ImageOps.autocontrast(self.left_frame)
        self.right_frame = Image.open(self.right_cam)
        self.right_frame = ImageOps.autocontrast(self.right_frame)

        #pdb.set_trace()

        left_frame_gif = ImageTk.PhotoImage(self.left_frame)
        right_frame_gif = ImageTk.PhotoImage(self.right_frame)

        # define a list of speeds for the radio buttons and a variable to keep track of which is pressed
        self.speed = IntVar()
        self.speed.set(0)
        speeds = [("stop", 0), ("1x", 1), ("2x", 2), ("3x", 3), ("4x", 4)]

        # user can see which frame they chose or choose another as the starting frame
        self.Label1 = Label(self.master,  text="Starting frame: ", fg = 'Black')
        self.Label1.place(x = 500, y = 10, width=150, height=20)
        self.starting_frame = Entry(self.master)
        self.starting_frame.place(x = 650, y = 10, width = 150, height = 20)
        l, r = self.get_frame_location(self.left_cam)
        self.starting_frame.insert(10, self.left_cam[l:r])
        self.start_frame = int(self.left_cam[l:r])

        # user can pick which frame to end on
        self.Label2 = Label(self.master, text="Ending frame: ", fg = 'Black')
        self.Label2.place(x=500, y = 30, width = 150, height = 20)
        self.ending_frame = Entry(self.master)
        self.ending_frame.place(x = 650, y = 30, width = 150, height = 20)
        self.ending_frame.insert(10, "None selected")
        self.end_frame = self.ending_frame.get()


        #display left image
        self.left_image = Label(self.master, image=left_frame_gif)
        self.left_image.image = left_frame_gif
        self.left_image.place(x =  5, y = 90, width = 640, height = 480)

        #display right image
        self.right_image = Label(self.master, image=right_frame_gif)
        self.right_image.image = right_frame_gif
        self.right_image.place(x = 650, y = 90, width = 640, height = 480)

        # allow user to choose video framerate
        for name, framerate in speeds:
            fps = Radiobutton(self.master, text = name, variable = self.speed, value = framerate * 30)
            fps.place(x = 375 + 50 * 2 * framerate, y = 600, width = 50, height = 60)


        # start slideshow button
        self.PLAY = Button(self.master)
        self.PLAY["text"] = "Start Slideshow"
        self.PLAY["command"] = self.play_slideshow
        self.PLAY.place(x = 250, y = 610, width = 100, height = 20)

        # save button
        self.SAVE = Button(self.master)
        self.SAVE["text"] = "Save"
        self.SAVE["command"] =  self.save_text_file
        self.SAVE.place(x = 1170, y = 610, width = 70, height = 20)

        # create a video button
        self.VIDEO = Button(self.master)
        self.VIDEO["text"] = "Make Video"
        self.VIDEO['command'] = self.save_video
        self.VIDEO.place(x = 1080, y = 610, width = 90, height = 20)

        # display the frame number
        l, r = self.get_frame_location(self.left_cam)
        self.frame_number = Label(self.master, text = "Current Frame = " + self.left_cam[l:r], fg = 'Black')
        self.frame_number.place(x = 500, y = 60, width = 250, height = 20)

        # choose start frame
        self.START = Button(self.master)
        self.START["text"] = "Choose Start Frame"
        self.START['command'] = self.choose_start_frame
        self.START.place(x = 810, y = 60, width = 120, height = 20)

        # choose end frame
        self.END = Button(self.master)
        self.END["text"] = "Choose End Frame"
        self.END['command'] = self.choose_end_frame
        self.END.place(x = 935, y = 60, width = 120, height = 20)

        # create slider with proper range
        slider_end_frame = self.slider_end(self.left_cam)
        self.slider = Scale(self.master, from_=self.start_frame, to=slider_end_frame, orient=HORIZONTAL)
        self.slider.place(x = 350, y = 650, width = 700, height = 40)

        # map a button to the slider that actually displays the frame
        self.SELECT = Button(self.master)
        self.SELECT["text"] = "Select frame"
        self.SELECT["command"] = self.display_frame
        self.SELECT.place(x = 225, y = 670, width = 100, height = 20)

        # map a button to the start frame entry to display the start frame
        self.SELECT_START = Button(self.master)
        self.SELECT_START["text"] = "Display start frame"
        self.SELECT_START["command"] = self.display_start_frame
        self.SELECT_START.place(x = 810, y = 25, width = 120, height = 20)

    def display_images(self):
        self.left_frame = Image.open(self.left_cam)
        self.left_frame = ImageOps.autocontrast(self.left_frame)
        self.right_frame = Image.open(self.right_cam)
        self.right_frame = ImageOps.autocontrast(self.right_frame)

        left_frame_gif = ImageTk.PhotoImage(self.left_frame)
        right_frame_gif = ImageTk.PhotoImage(self.right_frame)

    def play_slideshow(self):
        '''
        This function loops through a series of frames. When it is clicked
        it starts at the frame specified by the start frame textbox and loops until it reaches the end of the
        images or if the stop radiobutton is pressed.
        '''
        # choose start frame (if the entry in the start frame textbox is not a valid image then don't change start frame)
        frame = self.get_frame_number(self.start_frame, self.starting_frame.get())
        self.starting_frame.delete(0, END)
        self.starting_frame.insert(10, str(frame))
        self.start_frame = frame
        l, r = self.get_frame_location(self.left_cam)
        self.left_cam = self.left_cam[:l] + str(frame) + self.left_cam[r:]
        self.right_cam = self.right_cam[:l] + str(frame) + self.right_cam[r:]

        # open image
        self.left_frame = Image.open(self.left_cam)
        self.right_frame = Image.open(self.right_cam)

        self.left_frame = ImageOps.autocontrast(self.left_frame)
        self.right_frame = ImageOps.autocontrast(self.right_frame)
            
        left_frame_gif = ImageTk.PhotoImage(self.left_frame)
        right_frame_gif = ImageTk.PhotoImage(self.right_frame)

        # choose end frame
        if (self.ending_frame.get().isdigit() and self.ending_frame.get() > self.starting_frame.get()):
            self.end_frame = int(self.ending_frame.get())
        elif (self.ending_frame.get().isdigit() and self.ending_frame.get() < self.starting_frame.get()):
            self.ending_frame.delete(0, END)
            self.ending_frame.insert(10, "None selected")


        continue_slideshow = ""
        while self.speed.get() != 0 and continue_slideshow == "":
                l, r = self.get_frame_location(self.left_cam)
                frame = int(self.left_cam[l:r])

                if (self.ending_frame.get().isdigit() and self.end_frame <= frame):
                    continue_slideshow = "stop"
                    frame = self.end_frame - self.speed.get() / 30

                # determine frame rate (how many frames to skip)
                if self.speed.get() == 30:
                    frame += 1
                elif self.speed.get() == 60:
                    frame += 2
                elif self.speed.get() == 90:
                    frame += 3
                elif self.speed.get() == 120:
                    frame += 4

                # get file names
                self.left_cam = self.left_cam[:l] + str(frame) + self.left_cam[r:]
                self.right_cam = self.right_cam[:l] + str(frame) + self.right_cam[r:]

                try:
                    # open image
                    self.left_frame = Image.open(self.left_cam)
                    self.right_frame = Image.open(self.right_cam)

                    self.left_frame = ImageOps.autocontrast(self.left_frame)
                    self.right_frame = ImageOps.autocontrast(self.right_frame)

                    left_frame_gif = ImageTk.PhotoImage(self.left_frame)
                    right_frame_gif = ImageTk.PhotoImage(self.right_frame)
                    
                   # time.sleep(1/(self.speed.get()*30))

                except:
                    # image does not exist, find previous image
                    continue_slideshow = "stop"
                    
                    if self.speed.get() == 30:
                        frame -= 1
                    elif self.speed.get() == 60:
                        frame -= 2
                    elif self.speed.get() == 90:
                        frame -= 3
                    elif self.speed.get() == 120:
                        frame -= 4                    

                    self.left_cam = self.left_cam[:l] + str(frame) + self.left_cam[r:]
                    self.right_cam = self.right_cam[:l] + str(frame) + self.right_cam[r:]

                    self.left_frame = Image.open(self.left_cam)
                    self.right_frame = Image.open(self.right_cam)

                    self.left_frame = ImageOps.autocontrast(self.left_frame)
                    self.right_frame = ImageOps.autocontrast(self.right_frame)

                    left_frame_gif = ImageTk.PhotoImage(self.left_frame)
                    right_frame_gif = ImageTk.PhotoImage(self.right_frame)

                    self.speed.set(0)

                    print "stopping"
                
                # update image on GUI
                self.left_image.configure(image = left_frame_gif)
                self.left_image.image = left_frame_gif
                self.right_image.configure(image = right_frame_gif)
                self.right_image.image = right_frame_gif
                self.frame_number.configure(text = "Current frame = " + self.left_cam[l:r])
                self.frame_number.text = "Current frame = " + self.left_cam[l:r]
                self.master.update()

        if (continue_slideshow == "stop"):
            self.speed.set(0)

    def get_frame_number(self, working_frame, testing_frame):
        ''' 
        Determines if a user entered frame value is valid or if we should revert
        to a previously working frame.
        '''
        try:
            # try new starting frame that user chose
            l, r = self.get_frame_location(self.left_cam)
            left_cam = self.left_cam[:l] + str(testing_frame) + self.left_cam[r:]
            right_cam = self.right_cam[:l] + str(testing_frame) + self.right_cam[r:]

            # try to open image
            self.left_frame = Image.open(left_cam)
            self.right_frame = Image.open(right_cam)

            left_frame = ImageOps.autocontrast(self.left_frame)
            right_frame = ImageOps.autocontrast(self.right_frame)
            
            left_frame_gif = ImageTk.PhotoImage(self.left_frame)
            right_frame_gif = ImageTk.PhotoImage(self.right_frame)

            return testing_frame
        except:
            # picture doesn't exist, start at previously working start frame
            self.start_frame = working_frame
            # get frame and filenames
            l, r = self.get_frame_location(self.left_cam)
            frame = self.start_frame
            self.left_cam = self.left_cam[:l] + str(working_frame) + self.left_cam[r:]
            self.right_cam = self.right_cam[:l] + str(working_frame) + self.right_cam[r:]
            return working_frame

    def choose_start_frame(self):
         # update filenames for current frame and entry in the textbox
        l, r = self.get_frame_location(self.left_cam)
        self.starting_frame.delete(0, END)
        self.starting_frame.insert(10, self.left_cam[l:r])
        self.start_frame = int(self.left_cam[l:r])
        self.speed.set(self.speed.get())
        self.play_slideshow 

    def choose_end_frame(self):
        l, r = self.get_frame_location(self.left_cam)
        self.ending_frame.delete(0, END)
        self.ending_frame.insert(10, self.left_cam[l:r])

    def save_text_file(self):
        '''
        when user clicks save button, interface saves a text file to current directory
        with pathname to images, start frame, and end frame.
        '''
        file_name = os.path.abspath("image_stats.txt")
        file = open(file_name, "w")
        path = self.path_location(self.left_cam)
        file.write("Path to images = " + path + "\n")
        file.write("Starting frame = " + self.starting_frame.get() + "\n")
        file.write("Ending frame = " + self.ending_frame.get() + "\n")
        file.close()

    def path_location(self, filename):
        '''
        when writing the text file, we want the path. This function removes the image name and
        returns the path to the image, given a filename as input.
        '''
        path = filename.split("cam1")
        return path[0]

    def get_frame_location(self, filepath):
        '''
        gets the location of where the frame is in the file name so that we can change frames easily.
        '''
        parsed_strings = filepath.split("frame_")
        left = len(parsed_strings[0]) + 6 # add 6 since split method removes the string
        right_parsed_strings = parsed_strings[1].split(".")
        right = left + len(right_parsed_strings[0])
        return left, right


    def enter_filename(self):
        filename = askopenfilename(title="Choose an image") # show an "Open" dialog box and return the path to the selected file
        fileName, fileExtension = os.path.splitext(filename)
            
        while not fileExtension in ['.bmp', '.png']:
            # image not in right type, ask again
            showerror("Invalid file", "Please pick an image")
            filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
            fileName, fileExtension = os.path.splitext(filename)

        # return filename for left image and right image
        right_image = filename.replace("cam1", "cam2") 
        return filename, right_image

    def slider_end(self, filename):
        '''
        Function to determine what the last value on the slider should be (either 1000 past starting frame, or last frame)
        '''
        l, r = self.get_frame_location(filename)
        frame = int(filename[l:r])
        count = frame
        while (count <= (frame + 1000)):
            new_filename = filename[:l] + str(count) + filename[r:]
            try:
                image = Image.open(new_filename)
            except:
                return count - 1 # not more than 1000 frames, return last working one
            count += 1

        return count - 1 # 1000 images loaded successfully, return frame + 1000


    def display_frame(self):
        '''
        Displays the frame that the user selected via the slider
        '''
        frame = self.slider.get()
        l, r = self.get_frame_location(self.left_cam)
        self.left_cam = self.left_cam[:l] + str(frame) + self.left_cam[r:]
        self.right_cam = self.right_cam[:l] + str(frame) + self.right_cam[r:]

        # load image
        self.left_frame = Image.open(self.left_cam)
        self.right_frame = Image.open(self.right_cam)

        self.left_frame = ImageOps.autocontrast(self.left_frame)
        self.right_frame = ImageOps.autocontrast(self.right_frame)
            
        left_frame_gif = ImageTk.PhotoImage(self.left_frame)
        right_frame_gif = ImageTk.PhotoImage(self.right_frame)

        # update image on gui
        self.left_image.configure(image = left_frame_gif)
        self.left_image.image = left_frame_gif
        self.right_image.configure(image = right_frame_gif)
        self.right_image.image = right_frame_gif
        self.frame_number.configure(text = "Current frame = " + self.left_cam[l:r])
        self.frame_number.text = "Current frame = " + self.left_cam[l:r]
        self.master.update()

    def display_start_frame(self):
        frame = self.starting_frame.get()
        l, r = self.get_frame_location(self.left_cam)
        self.left_cam = self.left_cam[:l] + str(frame) + self.left_cam[r:]
        self.right_cam = self.right_cam[:l] + str(frame) + self.right_cam[r:]

        # load image
        try:
            self.left_frame = Image.open(self.left_cam)
            self.right_frame = Image.open(self.right_cam)

            self.left_frame = ImageOps.autocontrast(self.left_frame)
            self.right_frame = ImageOps.autocontrast(self.right_frame)
            
            left_frame_gif = ImageTk.PhotoImage(self.left_frame)
            right_frame_gif = ImageTk.PhotoImage(self.right_frame)

            # update image on gui
            self.left_image.configure(image = left_frame_gif)
            self.left_image.image = left_frame_gif
            self.right_image.configure(image = right_frame_gif)
            self.right_image.image = right_frame_gif
            self.frame_number.configure(text = "Current frame = " + self.left_cam[l:r])
            self.frame_number.text = "Current frame = " + self.left_cam[l:r]
            self.master.update()
        except:
            showerror("Invalid start frame", "Please pick a valid start frame to display")


    def save_video(self):
        '''
        Saves a video from the start frame to the end frame in the current directory
        '''
        l, r = self.get_frame_location(self.left_cam)
        start_frame = int(self.starting_frame.get())
        end_frame = self.ending_frame.get()

        if end_frame != "None selected":
            end_frame = int(end_frame)
        else:
            showerror("Invalid end frame", "Please pick a valid end frame before trying to save a video")
            return 1

        # Define the codec and create VideoWriter object
        ##TIM: Make sure that hard-coding this codec works on your machine, if not, add an if clause for the OS as in
        # in line 450 below, do same at line 462
        fourcc = cv2.VideoWriter_fourcc(*'WMV1')
        out = cv2.VideoWriter('left_video.avi',fourcc, 30, (640,480))

        left_filename = self.left_cam[:l]
        right_filename = self.left_cam[r:]

        for frame in range(start_frame, end_frame+1):
            picture = left_filename + str(frame) + right_filename
            left_image = cv2.imread(picture)
            out.write(left_image)
        
        # convert from avi to mp4 if using Mac
        if sys.platform=='darwin':
            # remove mp4 file if one is there already
            if os.path.exists('left_video.mp4'):
                subprocess.call('rm {0}'.format('left_video.mp4'), shell=True)
            # call ffmpeg from command line to convert video file
            command = "ffmpeg -i left_video.avi -acodec libfaac -b:a 128k -vcodec mpeg4 -b:v 1200k -flags +aic+mv4 left_video.mp4"
            subprocess.call(command,shell=True)

        cv2.destroyAllWindows()
        out.release()

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'WMV1')
        out = cv2.VideoWriter('right_video.avi',fourcc, 30, (640,480))

        left_filename = self.right_cam[:l]
        right_filename = self.right_cam[r:]

        for frame in range(start_frame, end_frame+1):
            picture = left_filename + str(frame) + right_filename
            right_image = cv2.imread(picture)
            out.write(right_image)

        # convert from avi to mp4 if using Mac
        if sys.platform=='darwin':
            # remove mp4 file if one is there already
            if os.path.exists('right_video.mp4'):
                subprocess.call('rm {0}'.format('right_video.mp4'), shell=True)
            command = "ffmpeg -i right_video.avi -acodec libfaac -b:a 128k -vcodec mpeg4 -b:v 1200k -flags +aic+mv4 right_video.mp4"
            subprocess.call(command,shell=True)

        cv2.destroyAllWindows()
        out.release()

        return 0


root = tk.Tk()
slideshow = Slideshow( master=root)
slideshow.master.title("Slideshow")
slideshow.master.geometry("1300x700")
slideshow.master.maxsize(1300, 700)
slideshow.mainloop()