import cv2
import numpy as np
import time
import math
import random
import os


def create_circles(width, height, radius, num_circles):
    '''
    :param width: int: width of circles
    :param height: int: height of circles
    :param radius: int: radius -- used for edge buffer
    :param num_circles: int: number of circles to create
    :return: circles: list of xy pos of center points of each circle
             circles_lifetime: list of lifetimes
    '''
    circles = [[], []]
    circles_lifetime = []
    radius_buffer = math.ceil(radius * 2.2)
    edge_buffer = radius * 3

    for i in range(num_circles):
        repeat_loop = True

        circlex = np.random.randint(0, width, dtype=int)
        circley = np.random.randint(0, height, dtype=int)

        while (repeat_loop):
            pos_check = False
            for j in range(len(circles[0])):
                if (((circles[0][j] - circlex) * (circles[0][j] - circlex) + (circles[1][j] - circley) * (
                        circles[1][j] - circley)) < radius_buffer * radius_buffer) or (
                        (circlex < edge_buffer) or (circlex > width - edge_buffer)) or (((circley > height - edge_buffer) or (circley < edge_buffer))):
                    circlex = np.random.randint(0, width, dtype=int)
                    circley = np.random.randint(0, height, dtype=int)
                    pos_check = True

            if pos_check == False:
                repeat_loop = False


        circles[0].append(circlex)
        circles[1].append(circley)

    for i in range(num_circles):
        circles_lifetime.append(10000)

    return (circles, circles_lifetime)


def xy_direction_speed_decoder(direction, speed, circlex, circley, width, height):
    '''

   :param direction: int: direction of video
   :param speed: int: speed of video
   :param circlex: int: x pos of center point of circle
   :param circley: int: y pos of center point of circle
   :param width: int: width of video
   :param height: int: height of video
   :return: new_x: new x pos of circle
            new_y: new y pos of circle
   '''
    dx = speed * math.sin(direction * (math.pi / 180))
    dy = -speed * math.cos(direction * (math.pi / 180))

    new_x = float(circlex) + dx
    new_y = float(circley) + dy

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


def redraw_circle(circles, width, height, radius):
    '''

   :param circles: list of len(num_circles) of xy position of center point of circles
   :param width: int: width of video
   :param height: int: height of video
   :param radius: int: radius of circle -- for edge buffer
   :return: circlex: new x position of circle
            circley: new y position of circle
   '''
    repeat_loop = True
    radius_buffer = math.ceil(radius * 2.2)
    edge_buffer = radius * 3

    circlex = np.random.randint(0, width, dtype=int)
    circley = np.random.randint(0, height, dtype=int)

    while (repeat_loop):
        pos_check = False
        for i in range(len(circles[0])):
            if (((circles[0][i]-circlex) * (circles[0][i]-circlex) + (circles[1][i]-circley) * (circles[1][i]-circley)) < radius_buffer * radius_buffer) or ((circlex < edge_buffer) or (circlex > width - edge_buffer)) or (((circley > height - edge_buffer) or (circley < edge_buffer))):
                circlex = np.random.randint(0, width, dtype=int)
                circley = np.random.randint(0, height, dtype=int)
                pos_check = True

        if pos_check == False:
            repeat_loop = False

    return(circlex, circley)

def create_vid(speed, direction, lifetime, num_circles, playback_fps, width, height, fps, seconds, circles, circles_lifetime, radius, iter):
    '''

    :param speed: int: speed of circles
    :param direction: int: direction of circles
    :param lifetime: int: lifetime of circles
    :param num_circles: int: number of circles
    :param playback_fps: int: frames per second at playback
    :param width: int: width of video
    :param height: int: height of video
    :param fps: int: creation fps
    :param seconds: int: how long the video takes
    :param circles: list: x and y position of all circles
    :param circles_lifetime: list: lifetime of all circles
    :param radius: int: radius of circles -- used for borders
    :param iter: int: video iteration for filename

    :return: null
    '''
    start = time.time()
    video_string = 'mda_sd_linear-speed-' + str(speed) + '-dir-' + str(direction) + '-lifetime-' + str(
        lifetime) + '-ndots-' + str(num_circles) + '-iter-' + str(iter) + '-.avi'
    video = cv2.VideoWriter('new_vid.avi', 0, float(playback_fps), (width, height))

    if lifetime == 0:
        lifetime = 10000

    for _ in range(int(fps * seconds)):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(num_circles):
            circles_lifetime[i] = circles_lifetime[i] - 1
            if circles_lifetime[i] <= 0:
                circles[0][i], circles[1][i] = redraw_circle(circles, width, height, radius)
                circles_lifetime[i] = lifetime

            cv2.circle(frame, (circles[0][i], circles[1][i]), radius, (255, 255, 255), -1)
            circles[0][i], circles[1][i] = xy_direction_speed_decoder(direction, speed, circles[0][i],
                                                                      circles[1][i], width, height)

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
    radius = 17
    seconds = 2.3
    lifetime = 0



    for iter in (1,2,3,4,5,6,7,8,9,10,11,12):

        for direction in (0,15,30,45,60,75,90,105,120,135,150,165,180,195,210,225,240,255,270,285,300,315,330,345):

            for speed in (6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 63, 66, 69, 72, 75):

                for num_circles in (1, 4, 16, 20):
                    circles, circles_lifetime = create_circles(width, height, radius, num_circles, lifetime)  # move into the iter loop - want diff dot patterns over iterations

                    create_vid(speed, direction, lifetime, num_circles, playback_fps, width, height, fps, seconds, circles, circles_lifetime, radius, iter)




start = time.time()
sequential_creation()

end = time.time()
cv2time = end - start
print('Total video creation time: ', cv2time)