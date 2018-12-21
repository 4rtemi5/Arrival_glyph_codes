#
# Random debug utils, used mainly to populate the intermediary
# results list.
#

import numpy as np
import cv2
import random

# Draws all the circles and their centers on a given frame.
# The drawn frame is returned. The "circles" array is expected to
# be similar to the one returned by cv2.HoughCircles.
def draw_all_circles(frame, circles):
	res = np.copy(frame)

	for x, y, radius in circles:
		# outer circle
		cv2.circle(res, (x,y), radius, (0, 255, 0), 2)
		# center
		cv2.circle(res, (x,y), 2, (0, 0, 255), 3)

	return res


# Draws all the contours on a black frame. Each contour is drawn 
# with a random color. The drawn frame is returned. The "contours" list
# is expected to be as the one returned by cv2.findContours
def draw_all_contours(shape, contours):
	black = np.zeros(shape)

	for cnt in contours:
		cv2.drawContours(black, [cnt], 0, random_color(), 1)

	return black

def draw_contours_arrivality(shape, list):
	black = np.zeros(shape)

	for (arrivality, cnt) in list:
		color = random_color()
		cv2.drawContours(black, [cnt], 0, color, 1)

		cnt = cnt[0]
		cv2.putText(black, str(arrivality), (cnt[0][0], cnt[0][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1, cv2.LINE_AA)

	return black

# Returns a random BGR color as a tuple (b, g, r).
def random_color():
	b = random.randint(0, 255)
	g = random.randint(0, 255)
	r = random.randint(0, 255)

	return (b, g, r)