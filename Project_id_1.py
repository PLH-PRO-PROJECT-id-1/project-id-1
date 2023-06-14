
##################################################################
#                                                                #
#         Προγραμματίζοντας έναν προσομοιωτή κυκλοφορίας         #
#                                                                #
# ################################################################              


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

import random
import time
import threading
import tkinter as tk
from tkinter import Tk, Label, PhotoImage, Canvas
from PIL import ImageTk, Image

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$



# ||||||||||| GLOBALS||||||||||||#
trafic_light_safe_distance = 30
immobilize_point = 15
free_road_ahead = 0
night_mode = False
trafic_light_safe_distance = 30
immobilize_point_right = 200
crossing_distance = 60
running_simulation = True
simulation_started = False
simulation_paused = False
paused = False
is_paused_pressed = False
paused_pressed_once = 0

##########################################################################################
# Γεφυρα για να συνεργαστουν τα αυτοκινητα με τα φαναρια χωρις να αλοιωθει ο καθε κωδικας##
fanaria = [(200, 335, 1, 1), (710, 337, 1, 1),  # To right                                       ##
           (285, 210, -1, 1), (775, 210, -1, 1),  # To left                             ##
           (190, 220, 2, 1),  # To down                                                    ##
           (773, 375, -2, 1)]  # to up                                                      ##


##########################################################################################


# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_#

##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^##
## FUNCTIONS FOR RUNNING CLASS METHODS###
def start_simulation():
    global simulation_started
    simulation_started = True


# ++++++++++++++++++++++++++++++++++++++++++++++++++++#
## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!###
def pause_all_traffic_lights(lights, pedestrian_lights):
    global is_paused_pressed
    is_paused_pressed = True
    global paused_pressed_once
    if paused_pressed_once == 0:
        for light in lights:
            light.pause_traffic_light()
        for light in pedestrian_lights:
            light.pause_pedestrian_light()
        global paused
        paused = True
    paused_pressed_once += 1

def resume_all_traffic_lights(lights, pedestrian_lights):
    global is_paused_pressed
    if is_paused_pressed:
        for light in lights:
            light.resume_traffic_light()
        for light in pedestrian_lights:
            light.resume_pedestrian_light()
        global paused
        paused = False
    is_paused_pressed = False
    global paused_pressed_once
    paused_pressed_once = 0

def pulsating_lights(lights, pedestrian_lights):
    for light in lights:
        light.start_pulse_orange()
    for light in pedestrian_lights:
        light.orange()
    global night_mode
    night_mode = True


# ++++++++++++++++++++++++++++++++++++++++++++++++++++#
def stop_simulation(root):
    global running_simulation
    running_simulation = False  # Set the variable to False
    root.destroy()


# ````````````````````````````````````````````````````#
'''Button that starts the threads of the simulation'''


def button_press(list_of_lights):
    start_simulation()

    cars_thread = threading.Thread(target=check_lights, args=(list_of_lights,))
    cars_thread.start()


# {}}{}{}{}{}{}{}{}{}{}{}{}{}{{}{}{}{}{}{{{}{}}{}}}}}{}}

# !!!! 3.14159265358979323846264338327950288419716939937510 !!!#
# _________________CLASS__DEFINITION__OF__LIGHTS_________________#
class TrafficLight:
    def __init__(self, master, x, y, direction, color_index, height=67, width=25):
        self.master = master
        self.x = x  # coordinates x
        self.y = y  # cordinates y
        self.direction = direction  # 1 for right, -1 for left , 2 for down, -2 for up
        self.width = width  # width of the traffic light
        self.height = height  # height of the traffic light
        self.colors = ["Green", "Orange", "Red"]
        self.color_index = color_index
        self.light_timer = None
        self.traffic_light = tk.Canvas(master, width=self.width, height=self.height, bg='black')
        self.traffic_light.place(x=x, y=y)
        self.paused = False
        self.light_off = False
        radius = min(self.width // 3, self.height // 2 - 5)  # Radious of creating red/green/orange circles
        # Creating the circle of red
        self.red_light = self.traffic_light.create_oval(self.width // 2 - radius, self.height // 6 - radius,
                                                        self.width // 2 + radius, self.height // 6 + radius,
                                                        fill='grey')
        # Creating the circle of orange
        self.orange_light = self.traffic_light.create_oval(self.width // 2 - radius, self.height // 2 - radius,
                                                           self.width // 2 + radius, self.height // 2 + radius,
                                                           fill='grey')
        # Creating the circle of green
        self.green_light = self.traffic_light.create_oval(self.width // 2 - radius, 5 * self.height // 6 - radius,
                                                          self.width // 2 + radius, 5 * self.height // 6 + radius,
                                                          fill='grey')
        # Initialize the color of the cirlce of the traffic light
        if self.color_index == 2:  # for red
            self.traffic_light.itemconfig(self.green_light, fill='green')
            self.traffic_light.itemconfig(self.orange_light, fill='grey')
            self.traffic_light.itemconfig(self.red_light, fill='grey')
        elif self.color_index == 1:  # orange
            self.traffic_light.itemconfig(self.red_light, fill='grey')
            self.traffic_light.itemconfig(self.orange_light, fill='orange')
            self.traffic_light.itemconfig(self.green_light, fill='grey')
        elif self.color_index == 0:  # green
            self.traffic_light.itemconfig(self.red_light, fill='red')
            self.traffic_light.itemconfig(self.orange_light, fill='grey')
            self.traffic_light.itemconfig(self.green_light, fill='grey')
        self.pulse_state = False
        self.angle = 0

    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
    # ~~~~~~~~~~~~~~~~METHODS_OF_HOW_THE_TRAFFIC_LIGHT_IS_DISPLAYED~~~~~~~~~~#

    # @@@@@@@@@@___TAKES__THE TRAFFIC__LIGHT__AND__ROTATES_IT_RIGHT___@@@@@@@@#
    def rotate_signal_right(self):
        self.width, self.height = self.height, self.width
        self.traffic_light.config(width=self.width, height=self.height)
        radius = min(self.width // 3, self.height // 2 - 5)

        self.traffic_light.coords(self.green_light,
                                  self.width // 6 - radius, self.height // 2 - radius,
                                  self.width // 6 + radius, self.height // 2 + radius)
        self.traffic_light.coords(self.orange_light,
                                  self.width // 2 - radius, self.height // 2 - radius,
                                  self.width // 2 + radius, self.height // 2 + radius)

        self.traffic_light.coords(self.red_light,
                                  5 * self.width // 6 - radius, self.height // 2 - radius,
                                  5 * self.width // 6 + radius, self.height // 2 + radius)

    # @@@@@@@@@@____ROTATES___LEFT___@@@@@@@@@@#
    def rotate_signal_left(self):
        self.width, self.height = self.height, self.width
        self.traffic_light.config(width=self.width, height=self.height)
        radius = min(self.width // 3, self.height // 2 - 5)

        self.traffic_light.coords(self.red_light,
                                  self.width // 6 - radius, self.height // 2 - radius,
                                  self.width // 6 + radius, self.height // 2 + radius)
        self.traffic_light.coords(self.orange_light,
                                  self.width // 2 - radius, self.height // 2 - radius,
                                  self.width // 2 + radius, self.height // 2 + radius)
        self.traffic_light.coords(self.green_light,
                                  5 * self.width // 6 - radius, self.height // 2 - radius,
                                  5 * self.width // 6 + radius, self.height // 2 + radius)

    # @@@@@@____ROTATES_180__DEGREES___@@@@@@@@#
    def rotate_180(self):
        radius = min(self.width // 3, self.height // 2 - 5)
        distance = self.height // 3

        self.red_light = self.traffic_light.create_oval(self.width // 2 - radius, 5 * self.height // 6 - radius,
                                                        self.width // 2 + radius, 5 * self.height // 6 + radius,
                                                        fill='grey')
        self.orange_light = self.traffic_light.create_oval(self.width // 2 - radius, self.height // 2 - radius,
                                                           self.width // 2 + radius, self.height // 2 + radius,
                                                           fill='grey')
        self.green_light = self.traffic_light.create_oval(self.width // 2 - radius, self.height // 6 - radius,
                                                          self.width // 2 + radius, self.height // 6 + radius,
                                                          fill='grey')

    # &$$$$$((((((((((((METHOD TO SWITCH FROM GREEN TO ORANGE,FROM ORANGE TO RED AND FROM RED TO GREEN)))))))))))))$$$$$$&#
    def switch_light(self):

        ##############################################
        if self.paused:
            self.light_timer = self.master.after(1000, self.pause_traffic_light)
            return
        elif self.light_off:
            self.light_timer = self.master.after(1000, self.pulse_orange)  # Delay for 1 second before checking again
            return
        ##############################################
        if self.color_index == 2:  # green
            self.traffic_light.itemconfig(self.red_light, fill='grey')
            self.traffic_light.itemconfig(self.green_light,
                                          fill='green')  # fills the green circle with green and the rest with grey
            self.traffic_light.itemconfig(self.orange_light, fill='grey')
            self.color_index = 1  # Set color_index to 0 for orange
            self.light_timer = self.master.after(10000,
                                                 self.switch_light)  # Delay for 10 seconds before switching to green
        elif self.color_index == 0:  # red
            self.traffic_light.itemconfig(self.green_light, fill='grey')
            self.traffic_light.itemconfig(self.red_light,
                                          fill='red')  # fills the red circle with red and the rest with grey
            self.traffic_light.itemconfig(self.orange_light, fill='grey')
            self.color_index = 2  # Set color_index to 1 for orange
            self.light_timer = self.master.after(13000,
                                                 self.switch_light)  # Delay for 13 seconds before switching to orange
        elif self.color_index == 1:  # Orange
            self.traffic_light.itemconfig(self.orange_light,
                                          fill='orange')  # fills the orange circle with orange and the rest with grey
            self.traffic_light.itemconfig(self.green_light, fill='grey')
            self.color_index = 0  # Set color_index to 2 for red
            self.light_timer = self.master.after(3000, self.switch_light)  # Delay for 3 seconds before switching to red

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
    #################           IN PROGRESS         ##############################
    def pulse_orange(self):
        if self.pulse_state:
            self.traffic_light.itemconfig(self.red_light, fill='grey')
            self.traffic_light.itemconfig(self.orange_light, fill='yellow')
            self.traffic_light.itemconfig(self.green_light, fill='grey')
            self.pulse_state = False
        else:
            self.traffic_light.itemconfig(self.red_light, fill='grey')
            self.traffic_light.itemconfig(self.orange_light, fill='grey')
            self.traffic_light.itemconfig(self.green_light, fill='grey')
            self.pulse_state = True
        self.master.after(500, self.pulse_orange)

    def start_pulse_orange(self):
        self.light_off = True

    def stop(self):
        if self.light_timer is not None:
            self.light_timer.cancel()
            self.traffic_light.itemconfig(self.red_light, fill='grey')
            self.traffic_light.itemconfig(self.orange_light, fill='yellow')
            self.traffic_light.itemconfig(self.green_light, fill='grey')
            self.pulse_orange()

    def pause_traffic_light(self):
        self.paused = True
        if self.light_timer is not None:
            self.master.after_cancel(self.light_timer)
        return

    def resume_traffic_light(self):
        self.paused = False
        if self.direction == 1:
            self.color_index = 0
            self.traffic_light.itemconfig(self.green_light, fill='grey')
            self.traffic_light.itemconfig(self.red_light,
                                          fill='red')  # fills the red circle with red and the rest with grey
            self.traffic_light.itemconfig(self.orange_light, fill='grey')
            self.color_index = 2  # Set color_index to 1 for orange
            self.light_timer = self.master.after(13000,
                                                 self.switch_light)
        elif self.direction == -1:
            
            self.color_index = 0
            self.traffic_light.itemconfig(self.green_light, fill='grey')
            self.traffic_light.itemconfig(self.red_light,
                                        fill='red')  # fills the red circle with red and the rest with grey
            self.traffic_light.itemconfig(self.orange_light, fill='grey')
            self.color_index = 2  # Set color_index to 1 for orange
            self.light_timer = self.master.after(13000,
                                                self.switch_light)
        elif self.direction == 2:
            self.traffic_light.itemconfig(self.red_light, fill='grey')
            self.traffic_light.itemconfig(self.green_light,
                                          fill='green')  # fills the green circle with green and the rest with grey
            self.traffic_light.itemconfig(self.orange_light, fill='grey')
            self.color_index = 1  # Set color_index to 0 for orange
            self.light_timer = self.master.after(10000,
                                                 self.switch_light)
        elif self.direction == -2:
            
            self.traffic_light.itemconfig(self.red_light, fill='grey')
            self.traffic_light.itemconfig(self.green_light,
                                          fill='green')  # fills the green circle with green and the rest with grey
            self.traffic_light.itemconfig(self.orange_light, fill='grey')
            self.color_index = 1  # Set color_index to 0 for orange
            self.light_timer = self.master.after(10000,
                                                 self.switch_light)
    
  # ______________________________________________________________#

###########################################################################
### ######### ### PEDESTRIAN LIGHT ### ########### ########################
class PedestrianLight:
    def __init__(self, master, x, y, direction, color_index, radius=16):
        self.master = master
        self.x = x
        self.y = y
        self.direction = direction
        self.radius = radius
        self.color_index = color_index
        self.traffic_light = tk.Canvas(master, width=2 * radius, height=2 * radius, bg='black')
        self.traffic_light.place(x=x, y=y)
        self.paused = False
        self.ped_off = False
        self.arrow = None  # Initialize arrow as None
        if self.color_index == 0:  # red
            self.light = self.traffic_light.create_oval(0, 0, 2 * radius, 2 * radius, fill='red')
        else:
            self.light = self.traffic_light.create_oval(0, 0, 2 * radius, 2 * radius, fill='green')
            if self.direction == 'up':
                self.arrow = self.traffic_light.create_line(
                    self.radius, self.radius + 12,  # Starting point (bottom-center of the oval)
                    self.radius, 5,  # Ending point (top-center of the oval)
                    fill='white', arrow=tk.LAST
                )
            if self.direction == 'down':
                self.arrow = self.traffic_light.create_line(
                    self.radius, self.radius + 12,  # Starting point (bottom-center of the oval)
                    self.radius, 5,  # Ending point (top-center of the oval)
                    fill='white', arrow=tk.FIRST
                )
            if self.direction == 'right':
                self.arrow = self.traffic_light.create_line(
                    self.radius - 12, self.radius,  # Starting point (left-center of the arrow)
                    self.radius + 12, self.radius,  # Ending point (right-center of the arrow)
                    fill='white', arrow=tk.LAST
                )

    def update_light_color(self):
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
        if self.paused:
            self.update_light_color()  # Delay for 1 second before checking again
            return
        elif self.ped_off:
            self.light_timer = self.master.after(1000, self.stay_orange)  # Delay for 1 second before checking again
            return
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
        if self.color_index == 2:  # green
            self.traffic_light.itemconfig(self.light, fill='green')
            if self.arrow is None:  # Add arrow if not already present
                if self.direction == 'up':
                    self.arrow = self.traffic_light.create_line(
                        self.radius, self.radius + 12,  # Starting point (bottom-center of the oval)
                        self.radius, 5,  # Ending point (top-center of the oval)
                        fill='white', arrow=tk.LAST
                    )
                # THE REVERSE OF THE ABOVE
                if self.direction == 'down':
                    self.arrow = self.traffic_light.create_line(
                        self.radius, self.radius + 12,
                        self.radius, 5,
                        fill='white', arrow=tk.FIRST
                    )
                if self.direction == 'right':
                    self.arrow = self.traffic_light.create_line(
                        self.radius - 12, self.radius,  # Starting point (left-center of the arrow)
                        self.radius + 12, self.radius,  # Ending point (right-center of the arrow)
                        fill='white', arrow=tk.LAST
                    )
                # THE REVERSE OF THE ABOVE
                if self.direction == 'left':
                    self.arrow = self.traffic_light.create_line(
                        self.radius - 12, self.radius,
                        self.radius + 12, self.radius,
                        fill='white', arrow=tk.FIRST
                    )
            self.color_index = 0
            self.light_timer = self.master.after(12000, self.update_light_color)
        else:  # red
            self.traffic_light.itemconfig(self.light, fill='red')
            if self.arrow is not None:  # Remove arrow if present
                self.traffic_light.delete(self.arrow)
                self.arrow = None
            self.color_index = 2
            self.light_timer = self.master.after(14000, self.update_light_color)

    def pause_pedestrian_light(self):
        self.paused = True
        if self.light_timer is not None:
            self.master.after_cancel(self.light_timer)

    def resume_pedestrian_light(self):
        self.paused = False
        if self.direction == 'right':
            if self.color_index == 0:
                self.traffic_light.itemconfig(self.light, fill='red')
                if self.arrow is not None:  # Remove arrow if present
                    self.traffic_light.delete(self.arrow)
                    self.arrow = None
                self.color_index = 2
                self.light_timer = self.master.after(14000, self.update_light_color)
            else:
                self.traffic_light.itemconfig(self.light, fill='green')
                self.arrow = self.traffic_light.create_line(
                self.radius - 12, self.radius,  # Starting point (left-center of the arrow)
                self.radius + 12, self.radius,  # Ending point (right-center of the arrow)
                fill='white', arrow=tk.LAST
                )
                self.color_index = 0
                self.light_timer = self.master.after(12000, self.update_light_color)
        elif self.direction == 'left':
            if self.color_index == 0:
                self.traffic_light.itemconfig(self.light, fill='red')
                if self.arrow is not None:  # Remove arrow if present
                    self.traffic_light.delete(self.arrow)
                    self.arrow = None
                self.color_index = 2
                self.light_timer = self.master.after(14000, self.update_light_color)
            else:
                self.traffic_light.itemconfig(self.light, fill='green')
                self.arrow = self.traffic_light.create_line(
                        self.radius - 12, self.radius,
                        self.radius + 12, self.radius,
                        fill='white', arrow=tk.FIRST
                )
                self.color_index = 0
                self.light_timer = self.master.after(12000, self.update_light_color)
        if self.direction == 'up':
            if self.color_index == 0:
                self.traffic_light.itemconfig(self.light, fill='red')
                if self.arrow is not None:  # Remove arrow if present
                    self.traffic_light.delete(self.arrow)
                    self.arrow = None
                self.color_index = 2
                self.light_timer = self.master.after(14000, self.update_light_color)
            else:
                self.traffic_light.itemconfig(self.light, fill='green')
                self.arrow = self.traffic_light.create_line(
                        self.radius, self.radius + 12,  # Starting point (bottom-center of the oval)
                        self.radius, 5,  # Ending point (top-center of the oval)
                        fill='white', arrow=tk.LAST
                    )
                self.color_index = 0
                self.light_timer = self.master.after(12000, self.update_light_color)
        elif self.direction == 'down':
            if self.color_index == 0:
                self.traffic_light.itemconfig(self.light, fill='red')
                if self.arrow is not None:  # Remove arrow if present
                    self.traffic_light.delete(self.arrow)
                    self.arrow = None
                self.color_index = 2
                self.light_timer = self.master.after(14000, self.update_light_color)
            else:
                self.traffic_light.itemconfig(self.light, fill='green')
                self.arrow = self.traffic_light.create_line(
                        self.radius, self.radius + 12,
                        self.radius, 5,
                        fill='white', arrow=tk.FIRST
                    )
                self.color_index = 0
                self.light_timer = self.master.after(12000, self.update_light_color)
    def stay_orange(self):
        self.traffic_light.itemconfig(self.light, fill='yellow')
        if self.arrow is not None:  # Remove arrow if present
            self.traffic_light.delete(self.arrow)
            self.arrow = None

    def orange(self):
        self.ped_off = True


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#


class MovingCar:
    number = 0
    current_cars = 0

    def __init__(self, canvas, start_X, start_Y, direction, delay=0):

        MovingCar.number += 1
        self.current_cars = 0

        self.number = MovingCar.number
        self.canvas = canvas
        self.direction = direction  # 1 for right, -1 for left
        # vehicle name creation expaination: vehicle + direcrion ( u , d, l , r ) + number  + extention
        # example for up vehicleu+"1" +".png

        if self.direction == 1:
            vehicle_type = random.randint(1, 5)
            vehicle = 'vehiclel2.png'
            self.car_image = tk.PhotoImage(file=vehicle)
        elif self.direction == -1:
            vehicle_type = random.randint(1, 5)
            vehicle = 'vehicler1.png'
            self.car_image = tk.PhotoImage(file=vehicle)
        elif self.direction == 2:
            vehicle_type = random.randint(1, 4)
            vehicle = 'vehicled4.png'
            self.car_image = tk.PhotoImage(file=vehicle)
        elif self.direction == -2:
            vehicle_type = random.randint(1, 4)
            vehicle = 'vehicleu1.png'
            self.car_image = tk.PhotoImage(file=vehicle)
        self.car_id = self.canvas.create_image(start_X, start_Y, image=self.car_image)
        self.speed = 3  # Initialize the car with a speed

    def move_car(self, speed, road_no):
        x1, y1, x2, y2 = self.canvas.bbox(self.car_id)
        self.road_no = road_no
        if self.direction == 1:  # Moving right
            self.canvas.move(self.car_id, speed * self.direction, 0)
            if x2 > 1000:  # If car reaches the right edge moving right, reset to start

                vehicle_type = random.randint(1, 5)
                vehicle = 'vehiclel2.png'
                self.car_image = tk.PhotoImage(file=vehicle)
                self.car_id = self.canvas.create_image(0, 323, image=self.car_image)
        elif self.direction == -1:  # If car reaches the left edge moving left, reset to start
            self.canvas.move(self.car_id, speed * self.direction, 0)

            if x1 < 30:
                vehicle_type = random.randint(1, 5)
                vehicle = 'vehicler1.png'
                self.car_image = tk.PhotoImage(file=vehicle)
                self.car_id = self.canvas.create_image(990, 253, image=self.car_image)

        elif self.direction == 2:  # Moving down
            self.canvas.move(self.car_id, 0, speed)  # Note the 0 in the x-coordinate change
            x1, y1, x2, y2 = self.canvas.bbox(self.car_id)
            if y2 > 700:  # If car reaches the bottom edge moving down, reset to start
                vehicle_type = random.randint(1, 4)
                vehicle = 'vehicled4.png'
                self.car_image = tk.PhotoImage(file=vehicle)
                self.car_id = self.canvas.create_image(232, 40, image=self.car_image)

        elif self.direction == -2:  # Moving up
            self.canvas.move(self.car_id, 0, -speed)  # Note the 0 in the x-coordinate change
            x1, y1, x2, y2 = self.canvas.bbox(self.car_id)
            if y2 < 10 and self.direction == -2:  # If car reaches the bottom edge moving down, reset to start

                vehicle_type = random.randint(1, 4)
                vehicle = 'vehicleu1.png'
                self.car_image = tk.PhotoImage(file=vehicle)
                self.car_id = self.canvas.create_image(740, 700, image=self.car_image)

        self.canvas.after(50,
                          lambda: self.move_car(self.speed, road_no))  # Continue moving the car at its current speed

    def start_moving(self, speed):
        self.speed = speed  # Update the car's speed

    def stop_moving(self):
        self.speed = 0


# def generate_cars():

def check_lights(xromata):
    crossing = False
    while True:
        global moving_cars
        global paused

        time.sleep(0.005)  # check every 5 ms
        if paused:
            for car in moving_cars:
                car.stop_moving()  # Delay for 1 second before checking again
            continue
        for moving_car in moving_cars:
            x1, y1, x2, y2 = moving_car.canvas.bbox(moving_car.car_id)  # get current car position
            if moving_car.direction == 1:
                minimum_distance = 10
                # Check for other cars ahead within the minimum distance
                for other_car in moving_cars:
                    # If same car or not in the same direction
                    if other_car == moving_car or moving_car.direction != other_car.direction:
                        continue  # Skip checking the car against itself or other direction
                    other_x1, other_y1, other_x2, other_y2 = other_car.canvas.bbox(other_car.car_id)
                    # if other car is  front of moving car  AND other car is
                    if other_x1 > x2 and other_x1 - x2 < minimum_distance:  # **** working code ****
                        moving_car.start_moving(speed=min(other_car.speed, moving_car.speed))  # Adjust speed
                        break
                else:  # No other cars ahead within the minimum distance
                    road = free_road_ahead
                    for i, (trafic_light_X, trafic_light_Y, trafic_light_direction, trafic_light_type) in enumerate(
                            fanaria):
                        distance_to_trafic_light = trafic_light_X - x2
                        if trafic_light_direction == moving_car.direction and trafic_light_type == 1 and x2 < trafic_light_X:
                            road = i
                            break

                    if road == free_road_ahead:  # No traffic lights ahead or enough distance from the last point
                        moving_car.start_moving(speed=6)  # Normal speed
                    else:  # There's a traffic light or another car ahead
                        # and fanaria[road].color_index != 1) \
                        # print(fanaria[road].color_index, moving_car.car_id, trafic_light_X, x1)  # if not red light
                        if (distance_to_trafic_light <= minimum_distance and xromata[road].color_index != 1) or \
                                (distance_to_trafic_light <= minimum_distance and night_mode):  # If the car is near the traffic light or Night mode is enabled
                            # Check the priority if night mode
                            if night_mode:
                                for crossing_car in moving_cars:
                                    # If same car or not in the crossing direction
                                    if crossing_car == moving_car or crossing_car.direction != -2:
                                        continue  # Skip checking the car against itself
                                    else:
                                        crossing_car_x1, crossing_car_y1, crossing_car_x2, crossing_car_y2 = crossing_car.canvas.bbox(
                                            crossing_car.car_id)

                                        #if (0 < crossing_car_x1 - x2 < crossing_distance and 0 < crossing_car_y1 - y2 < crossing_distance):
                                                #or (0 < crossing_car_x1 - x2 < crossing_distance and 0 < crossing_car_y2 - y1 < crossing_distance):
                                        if (750 >  x2 > 700  ) and (350 < crossing_car_y1 < 410) or (750 >  x2 > 700  ) and (300 < crossing_car_y2 < 400) :
                                            crossing = True
                                            moving_car.start_moving(speed=0)
                                            xromata[road].color_index = 2
                                            break
                                        else:
                                            crossing = False
                                            xromata[road].color_index = 1
                                            moving_car.start_moving(speed=6)

                            if (distance_to_trafic_light < immobilize_point and xromata[road].color_index == 2 ) :  # Stop at all cases

                                moving_car.start_moving(speed=0)
                            elif xromata[road].color_index == 0:  # Orange Light
                                moving_car.start_moving(speed=2)
                        else:
                            moving_car.start_moving(speed=6)  # Normal speed

            if moving_car.direction == -1:

                minimum_distance = 15
                for other_car in moving_cars:
                    if other_car == moving_car or moving_car.direction != other_car.direction:
                        continue  # Skip checking the car against itself
                    other_x1, other_y1, other_x2, other_y2 = other_car.canvas.bbox(other_car.car_id)
                    if other_x2 < x1 and x1 - other_x2 < minimum_distance:
                        moving_car.start_moving(speed=min(other_car.speed, moving_car.speed))  # Adjust speed
                        break

                else:  # No other cars ahead within the minimum distance
                    road = free_road_ahead
                    for i, (trafic_light_X, trafic_light_Y, trafic_light_direction, trafic_light_type) in reversed(
                            list(enumerate(fanaria))):
                        distance_to_trafic_light = x1 - trafic_light_X
                        if trafic_light_direction == moving_car.direction and trafic_light_type == 1 and trafic_light_X < x1:
                            road = i
                            break
                        else:
                            road = free_road_ahead
                    if road == free_road_ahead:  # No traffic lights ahead or enough distance from the last point
                        moving_car.start_moving(speed=6)  # Normal speed
                    else:  # There's a traffic light or another car ahead

                        if (distance_to_trafic_light <= minimum_distance and xromata[road].color_index != 1) or \
                                (
                                        distance_to_trafic_light <= minimum_distance and night_mode):  # If the car is near the traffic light or Night mode is enabled
                            # Check the priority if night mode
                            if night_mode:
                                for crossing_car in moving_cars:
                                    # If same car or not in the crossing direction
                                    if crossing_car == moving_car or crossing_car.direction != 2:
                                        continue  # Skip checking the car against itself
                                    else:
                                        crossing_car_x1, crossing_car_y1, crossing_car_x2, crossing_car_y2 = crossing_car.canvas.bbox(
                                            crossing_car.car_id)
                                        # print(crossing_car_x1 - x2)
                                        if ((280 <  x1 < 380)  and (220 < crossing_car_y2 < 340) )or ((280 < x1 <  390) and (230 < crossing_car_y1 < 300)):
                                            crossing = True
                                            moving_car.start_moving(speed=0)
                                            xromata[road].color_index = 2
                                            break
                                        else:
                                            crossing = False
                                            xromata[road].color_index = 1
                                            moving_car.start_moving(speed=6)
                            if distance_to_trafic_light < immobilize_point and xromata[
                                road].color_index == 2:  # Stop at all cases
                                moving_car.start_moving(speed=0)
                            elif xromata[road].color_index == 0:
                                moving_car.start_moving(speed=2)
                        else:
                            moving_car.start_moving(speed=6)  # Normal speed
            elif moving_car.direction == 2:  # Code for down movement
                minimum_distance = 15
                for other_car in moving_cars:
                    if other_car == moving_car or moving_car.direction != other_car.direction:
                        continue  # Skip checking the car against itself
                    other_x1, other_y1, other_x2, other_y2 = other_car.canvas.bbox(other_car.car_id)
                    if other_y1 - minimum_distance / 2 < y2 and y1 < other_y2:  # other_y1
                        moving_car.start_moving(speed=min(other_car.speed, moving_car.speed))  # Adjust speed
                        break
                else:  # No other cars ahead within the minimum distance
                    road = free_road_ahead
                    for i, (trafic_light_X, trafic_light_Y, trafic_light_direction, trafic_light_type) in enumerate(
                            fanaria):
                        distance_to_trafic_light = trafic_light_Y - y2
                        if trafic_light_direction == moving_car.direction and y2 < trafic_light_Y:
                            road = i

                            break
                        else:
                            road = free_road_ahead
                    if road == free_road_ahead:  # No traffic lights ahead or enough distance from the last point
                        moving_car.start_moving(speed=4)  # Normal speed
                    else:  # There's a traffic light or another car ahead

                        if (xromata[road].color_index != 1 and 0 < distance_to_trafic_light <= minimum_distance) or \
                                (distance_to_trafic_light <= minimum_distance and night_mode):
                            # If the car is near the traffic light or Night mode is enabled
                            if night_mode:
                                for crossing_car in moving_cars:
                                    # If same car or not in the crossing direction
                                    if crossing_car == moving_car or crossing_car.direction != 1:
                                        continue  # Skip checking the car against itself
                                    else:
                                        crossing_car_x1, crossing_car_y1, crossing_car_x2, crossing_car_y2 = crossing_car.canvas.bbox(
                                            crossing_car.car_id)
                                        if ((180 < y2 < 330) and (90 < crossing_car_x2 < 270)) or((150 < crossing_car_x1 < 270) and (180 < y2 < 330)):
                                            crossing = True
                                            moving_car.start_moving(speed=0)
                                            xromata[road].color_index = 2
                                            break
                                        else:
                                            crossing = False
                                            xromata[road].color_index = 0
                            if distance_to_trafic_light < immobilize_point and xromata[
                                road].color_index == 2:  # Stop at all cases
                                moving_car.start_moving(speed=0)
                            elif xromata[road].color_index == 0:
                                moving_car.start_moving(speed=2)
                        else:
                            moving_car.start_moving(speed=6)  # Normal speed
            elif moving_car.direction == -2:  # Code for down movement
                minimum_distance = 15
                for other_car in moving_cars:
                    if other_car == moving_car or moving_car.direction != other_car.direction:
                        continue  # Skip checking the car against itself
                    other_x1, other_y1, other_x2, other_y2 = other_car.canvas.bbox(other_car.car_id)
                    if other_y2 < y1 and y1 - other_y2 < minimum_distance:
                        moving_car.start_moving(speed=min(other_car.speed, moving_car.speed))  # Adjust speed
                        break
                else:  # No other cars ahead print('before for ')
                    for i, (trafic_light_X, trafic_light_Y, trafic_light_direction, trafic_light_type) in enumerate(
                            fanaria):
                        distance_to_trafic_light = trafic_light_Y - y1
                        if trafic_light_direction == moving_car.direction and trafic_light_type == 1 and y1 < trafic_light_Y:
                            road = i
                            break
                        else:
                            road = free_road_ahead
                    if road == free_road_ahead or distance_to_trafic_light < 0:  # no traffic light ahead
                        moving_car.start_moving(speed=6)  # Normal speed
                    else:  # There's a traffic light or another car ahead

                        if (xromata[road].color_index != 1 and 0 < distance_to_trafic_light <= minimum_distance) or \
                                (
                                        distance_to_trafic_light <= minimum_distance and night_mode):  # If the car is near the traffic light or Night mode is enabled

                            if night_mode:
                                for crossing_car in moving_cars:
                                    # If same car or not in the crossing direction
                                    if crossing_car == moving_car or crossing_car.direction != -1:
                                        continue  # Skip checking the car against itself
                                    else:
                                        crossing_car_x1, crossing_car_y1, crossing_car_x2, crossing_car_y2 = crossing_car.canvas.bbox(
                                            crossing_car.car_id)
                                        if ((200 < y1 < 410) and ( 700 < crossing_car_x1  < 850))\
                                                or ((690 < crossing_car_x2 < 800) and (200 < y1 < 410)):
                                            crossing = True
                                            moving_car.start_moving(speed=0)
                                            xromata[road].color_index = 2
                                            break
                                        else:
                                            crossing = False
                                            xromata[road].color_index = 0
                            if distance_to_trafic_light < immobilize_point and xromata[
                                road].color_index == 2:  # Stop at all cases
                                moving_car.start_moving(speed=0)
                            elif xromata[road].color_index == 0:
                                moving_car.start_moving(speed=2)
                        else:
                            moving_car.start_moving(speed=6)  # Normal speed

                    distance_to_trafic_light = 99


# ~~$~$~$~$~$~$~$~$~$~$~$~$~$~$~$~$~$~$~$~$~$
if __name__ == "__main__":

    # ^*^**^*^**^*^**^^**^*^^***^*^**^*^^**^^**^^*#
    #                   TITLE                    #
    # Create the Tkinter window
    root = tk.Tk()

    # Set the title and center the window

    window_title = "THE MOST AMAZING SIMULATION"
    root.wm_title(window_title)
    root.wm_attributes('-alpha', 1)  # Bring the window to the front

    # ^*^**^*^**^*^**^^**^*^^***^*^**^*^^**^^**^^*#

    img = Image.open('background.png')
    tkimage = ImageTk.PhotoImage(img)
    label1 = Label(root, image=tkimage)
    label1.image = tkimage  # Keep a reference
    label1.place(x=0, y=0)
    label1.lower()  # move the background image to the back
    # now creatιng the car widgets and they will be above the background
    canvas = tk.Canvas(root, width=1025, height=563)
    canvas.grid()
    background_id = canvas.create_image(0, 0, anchor='nw', image=tkimage)

    ########_________TRAFFIC LIGHTS______###############

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    global traffic_lights
    traffic_lights = []
    global pedestrian_lights
    pedestrian_lights = []
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
    #              FIRST INTERSECTION           #
    # ~~~~~~~~~~~~~~~~~~~RIGHT~~~~~~~~~~~~~~~~~~~#
    # Right traffic light in the first intersection
    traffic_light1 = TrafficLight(root, 148, 335, 1, color_index=2)
    traffic_light1.rotate_signal_right()
    traffic_lights.append(traffic_light1)
    # Right traffic light in the second intersection
    traffic_light5 = TrafficLight(root, 652, 337, 1, color_index=2)
    traffic_light5.rotate_signal_right()
    traffic_lights.append(traffic_light5)

    # ~~~~~~~~~~~~~~~~~~LEFT~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # Left traffic light in the first  intersection
    traffic_light2 = TrafficLight(root, 267, 210, -1, color_index=2)
    traffic_light2.rotate_signal_left()
    traffic_lights.append(traffic_light2)
    # ______________________________________________#
    # Left traffic light in the second  intersection
    traffic_light8 = TrafficLight(root, 770, 210, -1, color_index=2)
    traffic_light8.rotate_signal_left()
    traffic_lights.append(traffic_light8)

    # ~~~~~~~~~~~~~~~~~~DOWN~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # Downwards traffic light in the first intersection
    traffic_light4 = TrafficLight(root, 190, 171, 2, color_index=0)
    traffic_light4.rotate_180()
    traffic_lights.append(traffic_light4)

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
    #              SECOND INTERSECTION             #
    # ______________________________________________#
    # ______________________________________________#
    # ~~~~~~~~~~~~~~~~~~UP~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # Upwards traffic light in the second intersection
    traffic_light7 = TrafficLight(root, 772, 333, -2, color_index=0)
    traffic_lights.append(traffic_light7)
    # ______________________________________________#

    #######################################################
    #########~~~~~~PEDESTRIAN LIGHTS~~~~~##################
    pedestrian_light1 = PedestrianLight(root, 267, 336, 'up', 0)
    pedestrian_lights.append(pedestrian_light1)
    pedestrian_light2 = PedestrianLight(root, 687, 205, 'down', 0)
    pedestrian_lights.append(pedestrian_light2)

    pedestrian_light3 = PedestrianLight(root, 688, 365, 'right', 2)
    pedestrian_lights.append(pedestrian_light3)

    pedestrian_light4 = PedestrianLight(root, 267, 174, 'left', 2)
    pedestrian_lights.append(pedestrian_light4)
    #######################################################

    #########!!!!CARS!!!!###############
    global moving_cars
    moving_cars = [
        MovingCar(canvas, 30, 323, 1),
        MovingCar(canvas, 100, 323, 1),
        MovingCar(canvas, 0, 323, 1),
        MovingCar(canvas, 400, 323, 1),
        MovingCar(canvas, 250, 323, 1),
        MovingCar(canvas, 500, 323, 1),
        MovingCar(canvas, 1000, 253, -1),
        MovingCar(canvas, 800, 253, -1),
        MovingCar(canvas, 600, 253, -1),
        MovingCar(canvas, 200, 253, -1),
        MovingCar(canvas, 900, 253, -1),
        MovingCar(canvas, 232, 0, 2),
        MovingCar(canvas, 232, 50, 2),
        MovingCar(canvas, 232, 120, 2),
        MovingCar(canvas, 740, 500, -2),
        MovingCar(canvas, 740, 540, -2),
        MovingCar(canvas, 740, 600, -2),
    ]

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
    road = 0
    free_road_ahead = 0
    for x in range(len(traffic_lights)):
        free_road_ahead += 1

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
    ####################################
    start_button = tk.Button(root, text="Εναρξη", command=lambda: button_press(traffic_lights, ))
    start_button.place(x=0, y=0)

    pause_button = tk.Button(root, text="Παύση",
                             command=lambda: pause_all_traffic_lights(traffic_lights, pedestrian_lights))
    pause_button.place(x=50, y=0)

    resume_button = tk.Button(root, text="Συνέχεια",
                              command=lambda: resume_all_traffic_lights(traffic_lights, pedestrian_lights))
    resume_button.place(x=100, y=0)

    off_lights_button = tk.Button(root, text="Απενεργοποίηση Φαναριών",
                                  command=lambda: pulsating_lights(traffic_lights, pedestrian_lights))
    off_lights_button.place(x=157, y=0)
    # Bind the close event to the stop_simulation function
    root.protocol("WM_DELETE_WINDOW", lambda: stop_simulation(root))
    ####################################
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    print("Simulation started...:", simulation_started)

    while not simulation_started:
        root.update()
        pass
    for light in traffic_lights:
        light.switch_light()
    for pedestrian in pedestrian_lights:
        pedestrian.update_light_color()
    for car in moving_cars:
        car.move_car(3, 0)
    root.update()
    root.mainloop()
