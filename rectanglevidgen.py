'''
Author: Luke Bernier
Date: 4/1/22

Creates videos of rotating rectangles
'''

import cv2
import numpy as np
import time
import math
import random
import os

def create_rectangles(width, height, radius, num_rectangles):
    '''

    :param width: int: width of rect
    :param height: int: height of rect
    :param radius: int: radius -- used for edge buffer
    :param num_rectangles: int: number of rectangles to create
    :return: rectangles: list of xy pos of center points of each rectangle
             rectangles_lifetime: list of lifetimes
             rectangles_initial_angle: list of initial angles for rectangles
    '''
    rectangles = [[], []]
    rectangles_lifetime = []
    rectangles_initial_angle = []
    radius_buffer = math.ceil(radius * 2.2)
    edge_buffer = radius * 3

    for i in range(num_rectangles):
        repeat_loop = True

        rect_x = np.random.randint(0, width, dtype=int)
        rect_y = np.random.randint(0, height, dtype=int)

        while (repeat_loop):
            pos_check = False
            for j in range(len(rectangles[0])):
                if (((rectangles[0][j] - rect_x) * (rectangles[0][j] - rect_x) + (rectangles[1][j] - rect_y) * (
                        rectangles[1][j] - rect_y)) < radius_buffer * radius_buffer) or (
                        (rect_x < edge_buffer) or (rect_x > width - edge_buffer)) or (((rect_y > height - edge_buffer) or (rect_y < edge_buffer))):
                    rect_x = np.random.randint(0, width, dtype=int)
                    rect_y = np.random.randint(0, height, dtype=int)
                    pos_check = True

            if pos_check == False:
                repeat_loop = False


        rectangles[0].append(rect_x)
        rectangles[1].append(rect_y)


    for i in range(num_rectangles):
        rectangles_lifetime.append(0)
        rectangles_initial_angle.append(random.randint(0, 360))


    return (rectangles, rectangles_lifetime, rectangles_initial_angle)


def xy_direction_speed_decoder(direction, speed, rect_x, rect_y, width, height):
    '''

    :param direction: int: direction of video
    :param speed: int: speed of video
    :param rect_x: int: x pos of center point of rectangle
    :param rect_y: int: y pos of center point of rectangle
    :param width: int: width of rect
    :param height: int: height of rect
    :return: new_x: new x pos of rect
             new_y: new y pos of rect
    '''
    dx = speed * math.sin(direction * (math.pi / 180))
    dy = -speed * math.cos(direction * (math.pi / 180))

    new_x = float(rect_x) + dx
    new_y = float(rect_y) + dy

    new_x = np.float32(new_x)
    new_y = np.float32(new_y)

    if new_x > width - 15:
        new_x = 15
    if new_y > height - 15:
        new_y = 15
    if new_x < 15:
        new_x = width - 15
    if new_y < 15:
        new_y = height - 15

    return (new_x, new_y)


def redraw_rectangle(rectangles, width, height, radius):
    '''

    :param rectangles: list of len(num_rectangles) of xy position of center point of rectangles
    :param width: int: width of video
    :param height: int: height of video
    :param radius: int: radius of circle -- for edge buffer
    :return: rect_x: new x position of circle
             rect_y: new y position of circle
    '''
    repeat_loop = True
    radius_buffer = math.ceil(radius * 2.2)
    edge_buffer = radius * 3

    rect_x = np.random.randint(0, width, dtype=int)
    rect_y = np.random.randint(0, height, dtype=int)

    while (repeat_loop):
        pos_check = False
        for i in range(len(rectangles[0])):
            if (((rectangles[0][i]-rect_x) * (rectangles[0][i]-rect_x) + (rectangles[1][i]-rect_y) * (rectangles[1][i]-rect_y)) < radius_buffer * radius_buffer) or ((rect_x < edge_buffer) or (rect_x > width - edge_buffer)) or (((rect_y > height - edge_buffer) or (rect_y < edge_buffer))):
                rect_x = np.random.randint(0, width, dtype=int)
                rect_y = np.random.randint(0, height, dtype=int)
                pos_check = True

        if pos_check == False:
            repeat_loop = False

    return(rect_x, rect_y)

def get_points(rect_x, rect_y, height, width, rectangles_angle):
    '''

    :param rect_x: int: x pos
    :param rect_y: int: y pos
    :param height: int: rect height
    :param width:  int: rect width
    :param rectangles_angle: int: angle of rectangle
    :return: points: list len(4) of x and y for each point in a rectangle
    '''

    points = []
    points.append([-(width/2), height/2]) #point A, top left
    points.append([width/2, height/2 ])  #point B, top right
    points.append([width / 2, -(height / 2)])  # point C, bottom right
    points.append([-(width / 2), -(height / 2)])  # point D, bottom left

    theta = np.radians(rectangles_angle)
    c, s = np.cos(theta), np.sin(theta)

    for i in range(len(points)):

        new_x = points[i][0] * c - points[i][1] * s
        new_y = points[i][0] * s + points[i][1] * c

        points[i][0] = new_x
        points[i][1] = new_y

        points[i][0] = points[i][0] + rect_x
        points[i][1] = points[i][1] + rect_y

    return(points)

def draw_rectangle(rectangle_x, rectangle_y, height, width, rectangle_angle, rotation_angle):
    '''

    :param rectangle_x: int: x pos
    :param rectangle_y: int: y pos
    :param height: int: height of rectangle
    :param width: int: width of rectangle
    :param rectangle_angle: int: current angle of rectangle
    :param rotation_angle: int: degrees that the rectangle rotates per frame
    :return: box: list len(4) of  verticies of rectangle
             rectangle_angle: int: new angle of rectangle
    '''

    rectangle_angle = rectangle_angle + rotation_angle
    if rectangle_angle >= 360:
        rectangle_angle = 0

    if rectangle_angle < 0:
        rectangle_angle = 359

    points = get_points(rectangle_x, rectangle_y, height, width, rectangle_angle)
    points = np.uint64(points)

    rect = cv2.minAreaRect(points)
    box = cv2.boxPoints(rect)  # cv2.boxPoints(rect) for OpenCV 3.x
    box = np.int0(box)

    return(box, rectangle_angle)

def create_vid(speed, direction, lifetime, num_rectangles, playback_fps, width, height, fps, seconds, rectangles, rectangles_lifetime, radius, iter, rectangles_angle, rotation_angle, rect_height, rect_width, ccw):
    '''

    :param speed: int: speed of rectangles
    :param direction: int: direction of rectangles
    :param lifetime: int: lifetime of rectangles
    :param num_rectangles: int: number of rectangles
    :param playback_fps: int: frames per second at playback
    :param width: int: width of video
    :param height: int: height of video
    :param fps: int: creation fps
    :param seconds: int: how long the video takes
    :param rectangles: list: x and y position of all rectangles
    :param rectangles_lifetime: list: lifetime of all rectangles
    :param radius: int: radius of rectangles -- used for borders
    :param iter: int: video iteration for filename
    :param rectangles_angle: int: angle of rectangle
    :param rotation_angle: int: degree at which the rectangle rotates per frame
    :param rect_height: int: height of rectangle
    :param rect_width: int: width of rectangle
    :param ccw: bool: counter clockwise rotation if true, clockwise rotation if false
    :return: null
    '''
    start = time.time()

    if ccw:
        video_string = 'mda_sd_linear_rotation-ccw-rotangle-' + str(abs(rotation_angle)) + '-speed-' + str(speed) + '-dir-' + str(direction) + '-lifetime-' + str(
            lifetime) + '-ndots-' + str(num_rectangles) + '-iter-' + str(iter) + '-.avi'
    else:
        video_string = 'mda_sd_linear_rotation-cw-rotangle-' + str(abs(rotation_angle)) + '-speed-' + str(
            speed) + '-dir-' + str(direction) + '-lifetime-' + str(
            lifetime) + '-ndots-' + str(num_rectangles) + '-iter-' + str(iter) + '-.avi'

    video = cv2.VideoWriter('new_vid.avi', 0, float(playback_fps), (width, height))

    if lifetime == 0:
        lifetime = 10000
    for _ in range(int(fps * seconds)):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(num_rectangles):
            rectangles_lifetime[i] = rectangles_lifetime[i] - 1
            if rectangles_lifetime[i] <= 0:
                rectangles[0][i], rectangles[1][i] = redraw_rectangle(rectangles, width, height, radius)
                rectangles_lifetime[i] = lifetime

            box, rectangles_angle[i] = draw_rectangle(rectangles[0][i], rectangles[1][i], rect_height, rect_width, rectangles_angle[i], rotation_angle)
            cv2.drawContours(frame, [box], 0, (255, 255, 255), -1)
            rectangles[0][i], rectangles[1][i] = xy_direction_speed_decoder(direction, speed, rectangles[0][i],
                                                                      rectangles[1][i], width, height)

        video.write(frame)
    video.release()

    cmd_string = 'ffmpeg -y -i new_vid.avi -vf scale=400:400 -c:v libx264 -b:v 5000k -crf 0 -preset veryslow -qp 0 ' + video_string
    os.system(cmd_string)



    end = time.time()
    cv2time = end - start
    print('Created video: ' + video_string)
    print('video creation + resize time: ', cv2time)


def sequential_creation():
    #create videos

    width = 1600
    height = 1600
    fps = 77
    playback_fps = 30
    seconds = 2.3
    num_rectangles = 20
    lifetime = 0
    iter = 1

    rect_height = 22
    rect_width = 42
    radius = rect_width

    for l in range(12):
        for i in (-32, -16, -8, -4, 4, 8, 16, 32):
            if i < 0:
                ccw = True
            else:
                ccw= False
            for j in (6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 63, 66, 69, 72, 75):
                for k in range(0,15,30,45,60,75,90,105,120,135,150,165,180,195,210,225,240,255,270,285,300,315,330,345):
                    rectangles, rectangles_lifetime, rectangles_angle = create_rectangles(width, height, radius, num_rectangles, lifetime)  # move into the iter loop - want diff dot patterns over iterations

                    create_vid(j, k, lifetime, num_rectangles, playback_fps, width, height, fps, seconds, rectangles, rectangles_lifetime, radius, iter, rectangles_angle, i, rect_height, rect_width, ccw)

        iter = iter + 1



start = time.time()
sequential_creation()

end = time.time()
cv2time = end - start
print('Total video creation time: ', cv2time)