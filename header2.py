import math
import cv2
import mido
import time
import copy
import serial
import re

fsr_threshold = 1800
blackkeypproportions = [(1, 28.5, 2, 6), (2, 34.1, 3, 12.9), (3, 41.1, 4, 20.3), (5, 32.5, 6, 11.5), (6, 35.5, 7, 14.5), (8, 28.5, 9, 6), (9, 34.1, 10, 12.9), (10, 41.1, 11, 20.3), (12, 32.5, 13, 11.5), (13, 35.5, 14, 14.5), (15, 28.5, 16, 6), (16, 34.1, 17, 12.9), (17, 41.1, 18, 20.3), (19, 32.5, 20, 11.5), (20, 35.5, 21, 14.5), (22, 28.5, 23, 6), (23, 34.1, 24, 12.9), (24, 41.1, 25, 20.3)]
landmark_labels = [
    'WRIST',
    'THUMB_CMC', 'THUMB_MCP', 'THUMB_IP', 'THUMB_TIP',
    'INDEX_FINGER_MCP', 'INDEX_FINGER_PIP', 'INDEX_FINGER_DIP', 'INDEX_FINGER_TIP',
    'MIDDLE_FINGER_MCP', 'MIDDLE_FINGER_PIP', 'MIDDLE_FINGER_DIP', 'MIDDLE_FINGER_TIP',
    'RING_FINGER_MCP', 'RING_FINGER_PIP', 'RING_FINGER_DIP', 'RING_FINGER_TIP',
    'PINKY_MCP', 'PINKY_PIP', 'PINKY_DIP', 'PINKY_TIP'
]
fingertip_indices = [4, 8, 12, 16, 20]
whitekeymidinotes = [41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84]
blackkeymidinotes = [42, 44, 46, 49, 51, 54, 56, 58, 61, 63, 66, 68, 70, 73, 75, 78, 80, 82]
finger_colours = [(0, 255, 255), (255, 255, 0), (255, 0, 255), (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 255), (255, 128, 0), (0, 255, 128), (128, 0, 255)]
moveunit = 2 
rotateunit = 0.25 
keyplayedradius = 10
pianoproportion = 270 / 1222
serial_port = '/dev/tty.usbmodem101'

def point_at_parameter(p1, p2, t):
    x = p1.x() + t * (p2.x() - p1.x())
    y = p1.y() + t * (p2.y() - p1.y())
    z = p1.z() + t * (p2.z() - p1.z())
    return point(x, y, z)
def center_of_keys(keys):
    return center(keys[0].topleft, keys[-1].topright, keys[-1].bottomright, keys[0].bottomleft)
def center(p1, p2, p3, p4):
    return point((p1.x() + p2.x() + p3.x() + p4.x()) / 4, (p1.y() + p2.y() + p3.y() + p4.y()) / 4, (p1.z() + p2.z() + p3.z() + p4.z()) / 4)
def length(p1, p2):
    return math.sqrt((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2)
def point_in_quad(point, key_to_check):
    p1 = key_to_check.topleft
    p2 = key_to_check.topright
    p3 = key_to_check.bottomright
    p4 = key_to_check.bottomleft
    def area(a, b, c):
        return 0.5 * abs(a.x() * (b.y() - c.y()) + b.x() * (c.y() - a.y()) + c.x() * (a.y() - b.y()))

    # Total area of the quadrilateral
    total_area = area(p1, p2, p3) + area(p1, p3, p4)

    # Area of triangles formed with point_to_check
    area1 = area(point, p1, p2)
    area2 = area(point, p2, p3)
    area3 = area(point, p3, p4)
    area4 = area(point, p4, p1)

    # Check if the sum of the areas equals the total area of the quadrilateral
    return abs((area1 + area2 + area3 + area4) - total_area) < 1e-5
def printcoordinates(keylist):
    for somekey in keylist:
        print(somekey.topleft.tuple(), somekey.topright.tuple(), somekey.bottomright.tuple(), somekey.bottomleft.tuple())

class point:
    def __init__(self, x, y, z):
        self.px = x
        self.py = y
        self.pz = z
    def __add__(self, other):
        if isinstance(other, point):
            return point(self.px + other.px, self.py + other.py, self.pz + other.pz)
        return NotImplemented
    def x(self):
        return self.px
    def y(self):
        return self.py
    def z(self):
        return self.pz
    def tuple(self):
        return (self.px, self.py)
    def move(self, axis, units):
        if axis == 'x':
            self.px += units
        if axis == 'y':
            self.py += units
        if axis == 'z':
            self.pz += units
    def rotate(self, axis, center, d):
    # Convert degrees to radians
        radians = math.radians(d)
        
        # Translate point to origin
        translated_x = self.px - center.x()
        translated_y = self.py - center.y()
        translated_z = self.pz - center.z()
        
        if axis == 'z':
            rotated_x = translated_x * math.cos(radians) + translated_y * math.sin(radians)
            rotated_y = -translated_x * math.sin(radians) + translated_y * math.cos(radians)
            self.px = rotated_x + center.x()
            self.py = rotated_y + center.y()
        elif axis == 'x':
            rotated_y = translated_y * math.cos(radians) - translated_z * math.sin(radians)
            rotated_z = translated_y * math.sin(radians) + translated_z * math.cos(radians)
            self.pz = rotated_z + center.z()
            self.py = rotated_y + center.y()
        elif axis == 'y':
            rotated_x = translated_x * math.cos(radians) + translated_z * math.sin(radians)
            rotated_z = -translated_x * math.sin(radians) + translated_z * math.cos(radians)
            self.pz = rotated_z + center.z()
            self.px = rotated_x + center.x()        
    def project(self, centreofscreen, initialz):
        return point_at_parameter(centreofscreen, self, initialz / self.pz)   
    def integer(self):
        return point(int(self.px), int(self.py), int(self.pz))


class key:
    def __init__(self, topleft, topright, bottomright, bottomleft, note, type = 'white'):
        self.topleft = topleft
        self.topright = topright
        self.bottomright = bottomright
        self.bottomleft = bottomleft
        self.type = type
        self.note = note
        self.previouslyplaying = False
        self.currentlyplaying = False
        self.blackkeyonright = False
        self.blackkeyonleft = False
        self.initialposition = (copy.copy(topleft), copy.copy(topright), copy.copy(bottomright), copy.copy(bottomleft))
    def toplength(self):
        return length(self.topleft, self.topright)   
    def bottomlength(self):
        return length(self.bottomleft, self.bottomright)   
    def coordinates(self):
        return (self.topleft, self.topright, self.bottomright, self.bottomleft)  
    def center(self):
        x = (self.topleft.x() + self.topright.x() + self.bottomright.x() + self.bottomleft.x()) / 4
        y = (self.topleft.y() + self.topright.y() + self.bottomright.y() + self.bottomleft.y()) / 4
        z = (self.topleft.z() + self.topright.z() + self.bottomright.z() + self.bottomleft.z()) / 4
        return point(x, y, z)
    def draw(self, frame, center_of_screen, initialz):
        mycoordinates = self.coordinates()
        if self.type == 'white':
            keycolour = (150, 0, 0)
        else:
            keycolour = (0, 200, 255)

        cv2.line(frame, mycoordinates[0].project(center_of_screen, initialz).integer().tuple(), mycoordinates[(1) % 4].project(center_of_screen, initialz).integer().tuple(), keycolour, 2)
        firstpointonright = point_at_parameter(self.topright, self.bottomright, 8 / 13 * self.blackkeyonright)
        cv2.line(frame, firstpointonright.project(center_of_screen, initialz).integer().tuple(), mycoordinates[(2) % 4].project(center_of_screen, initialz).integer().tuple(), keycolour, 2)
        cv2.line(frame, mycoordinates[2].project(center_of_screen, initialz).integer().tuple(), mycoordinates[(3) % 4].project(center_of_screen, initialz).integer().tuple(), keycolour, 2)
        firstpointonleft = point_at_parameter(self.topleft, self.bottomleft, 8 / 13 * self.blackkeyonleft)
        cv2.line(frame, firstpointonleft.project(center_of_screen, initialz).integer().tuple(), mycoordinates[(3) % 4].project(center_of_screen, initialz).integer().tuple(), keycolour, 2)
    def play(self, outport):
        if (not self.previouslyplaying):
            outport.send(mido.Message('note_on', note=self.note, velocity=100))
        self.currentlyplaying = True
    def stop(self, outport):
        outport.send(mido.Message('note_off', note=self.note, velocity=100))
        self.currentlyplaying = False  
    def move(self, axis, units):
        self.topleft.move(axis, units)
        self.topright.move(axis, units)
        self.bottomleft.move(axis, units)
        self.bottomright.move(axis, units) 
    def rotate(self, axis, center, degrees):
        self.topleft.rotate(axis, center, degrees)
        self.topright.rotate(axis, center, degrees)
        self.bottomleft.rotate(axis, center, degrees)
        self.bottomright.rotate(axis, center, degrees)
    def project(self, center_of_screen, initialz):
        return key(self.topleft.project(center_of_screen, initialz), self.topright.project(center_of_screen, initialz), self.bottomright.project(center_of_screen, initialz), self.bottomleft.project(center_of_screen, initialz), note = self.note)
    def reset_position(self):
        self.topleft = copy.copy(self.initialposition[0])
        self.topright = copy.copy(self.initialposition[1])
        self.bottomright = copy.copy(self.initialposition[2])
        self.bottomleft = copy.copy(self.initialposition[3])
