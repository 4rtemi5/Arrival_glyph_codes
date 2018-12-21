#
# Process a single frame
#
import traceback

import cv2
import numpy as np
import math

from scripts.decode_frame import *
from scripts.debug_utils import *
from scripts.utils import *


def process_frame(frame):

	intermediary = []
	#intermediary.append(("original", frame))

	# The resolution on which to work
	# dest_height = 1080 # Full HD (1080p), in a 16:9 aspect ratio
	dest_height = 720 # HD Ready (720p), in a 16:9 aspect ratio

	# Computes the size to which the frame is resized. Mantains original aspect ratio
	dest_size = (int(round((frame.shape[1]/frame.shape[0])*dest_height)),dest_height)

	# Resize to computable resolution
	frame_resized = cv2.resize(frame, dest_size, interpolation = cv2.INTER_AREA)
	#intermediary.append(("resized", frame_resized))

	# Convert to grayscale
	grayscale = cv2.cvtColor(frame_resized, cv2.COLOR_RGB2GRAY)

	# Gaussian blur to reduce camera noise
	blurred = cv2.GaussianBlur(grayscale, (3, 3), 0)

	# Adaptive tresholding: always creates a precise separation between
	# the glyph and everything else
	gauss = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C , cv2.THRESH_BINARY_INV,201,2)
	#intermediary.append(('Adaptive Gauss Tresh', gauss))

	# Detecting contours
	im2, contours, hierarchy = cv2.findContours(gauss, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	# Filtering contours too big or too small
	# NOTE: In your code you filtered in this way: 6000 < area < 100000. Values to tweak.
	contours = [c for c in contours if 1000 <= cv2.contourArea(c) <= 70000]
	#intermediary.append(("Contours", draw_all_contours(frame_resized.shape, contours)))

	# Computes the arrivality of each contours
	cnt_with_arrivality = [(_arrivality_for_contour(c, gauss.shape), c) for c in contours]
	#intermediary.append(("Arrivalities", draw_contours_arrivality(frame_resized.shape, cnt_with_arrivality)))
	
	# Gets the contour with maximum arrivality
	cnt_with_arrivality = max(cnt_with_arrivality, key = lambda x: x[0])
	chosen_contour = cnt_with_arrivality[1]

	# Drawing the choosen contour
	chosen = np.zeros(frame_resized.shape)
	cv2.fillPoly(chosen, pts=[chosen_contour], color=(255, 255, 255))

	# Resizing the final frame to contain only the choosen contour
	x,y,w,h = cv2.boundingRect(chosen_contour)
	final = chosen[y:y+h, x:x+w]
	intermediary.append(('Processed frame', final))

	return final, intermediary




# Given a contour and the shape of the resized frame, computes the
# arrivality of that contour. The higher the better.
def _arrivality_for_contour(contour, shape):
	mask = np.zeros(shape, dtype='uint8')
	mask = cv2.fillPoly(mask, pts=[contour], color=(255, 255, 255))

	x, y, w, h = cv2.boundingRect(contour)
	cnt_mask = mask[y:y + h, x:x + w]

	distance_map = cv2.distanceTransform(cnt_mask, cv2.DIST_L2, 5)

	# Given the image of this contours, tries to find a circle for the contour
	center, radius = _circle_from_contour_image(cnt_mask, distance_map)

	# Given the circle, the arrivality is computed.
	arrivality = _get_total_arrivality(distance_map, center, radius)

	return arrivality


# Given an image containing a contour and the distance map of the contour,
# finds a circle that is approximately the furthest from the borders of the contour.
# If such circle is not found, a negative radius is returned.
def _circle_from_contour_image(cnt_image, dist):
	center = (int(round(cnt_image.shape[1]/2)), int(round(cnt_image.shape[0]/2)))
	radius = None
	circle_points = []

	diagonal_half = int(round(math.sqrt(cnt_image.shape[0]**2+cnt_image.shape[1]**2)/2 ))     # diagonal/2 - short_side

	for ang in [0, math.pi/2, math.pi, 3*math.pi/2]:
		lightest = 0
		for pixel in range(0, int(round(diagonal_half))):
			pX = int(round(pixel * math.cos(ang) + center[0]))
			pY = int(round(pixel * math.sin(ang) + center[1]))

			if pX >= 0 and pX < cnt_image.shape[1] and pY >= 0 and pY < cnt_image.shape[0]:
				if dist[pY][pX] > lightest:
					lightest = dist[pY][pX]
					lightest_point = (pX, pY)
			else:
				break
		if lightest > 0:
			circle_points.append(lightest_point)
		if len(circle_points) >= 3:
			break

	if len(circle_points) < 3:
		center, radius = (-1, -1), -1
	else:
		try:
			center, radius = get_circle_from_points(circle_points[0],circle_points[1],circle_points[2])
		except:
			center, radius = (-1, -1), -1

	return center, radius





# Gives the image of a contour and a circles, computes the arrivality of the contour.
# The higher the better. The current interval of the metric is [-200, +100].
def _get_total_arrivality(mask, center, radius):

	if (radius < 0): 
		return -200

	# TUNE
	inner_radius = 0.8 * radius
	outer_radius = 1.3 * radius

	radius_a = _get_arrivality_for_radius(mask, center, radius)
	outer_a = _get_arrivality_for_radius(mask, center, outer_radius)
	inner_a = _get_arrivality_for_radius(mask, center, inner_radius)

	return radius_a - outer_a - inner_a

# Calculates the arrivality coefficient for single radius in contour.
def _get_arrivality_for_radius(mask, center, radius):
	arrivality = 0
	for ang in np.linspace(0, 2 * math.pi, 100) :
		pX = int(round(radius * math.cos(ang) + center[0]))
		pY = int(round(radius * math.sin(ang) + center[1]))

		if pX >= 0 and pX < mask.shape[1] and pY >= 0 and pY < mask.shape[0]:
			if mask[pY][pX] > 0:
				arrivality +=1
	return arrivality