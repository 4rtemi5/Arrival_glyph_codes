#
# Takes a processd frame and attempts to decode it
#
import math
import numpy as np

from scripts.utils import *

def decode_frame(frame):
	data = []
	intermediary = []

	#TODO

	return data, intermediary


def read_circle_segment(sign):
	frame = sign.copy()
	minDist = 0  # start reading at minDist * detected radius
	maxDistCheck = int(round(math.sqrt(sign.shape[0]**2+sign.shape[1]**2)/2))  # longest readable distance from center(half of diagonal of image)
	read = []


	center, radius, arrivalidity = get_circle_from_mask(frame)

	# Todo tune arrivality limit
	if arrivalidity > 150:
		readSplits = 4 * math.pi * radius

		black_bgr, gap, inlier, minDist = find_ends(frame, center, radius, minDist, maxDistCheck)

		if inlier >= (readSplits * 0) and gap != []:
			try:
				# draw stuff in the output image,

				circle_start = gap[0]
				circle_end = gap[1]
				if circle_start[0] and circle_start[1] and circle_end[0] and circle_end[1]:

					cv2.circle(black_bgr, center, int(round(radius*0.8)), (0,255,0), 2)
					cv2.circle(black_bgr, center, int(round(radius*1.3)), (0,255,0), 2)
					cv2.circle(black_bgr, center, radius, (255,0,0), 2)
					cv2.rectangle(black_bgr, (circle_start[0] - 3, circle_start[1] - 3), (circle_start[0] + 3, circle_start[1] + 3), (0, 255, 0), -1)
					cv2.rectangle(black_bgr, (circle_end[0] - 3, circle_end[1] - 3), (circle_end[0] + 3, circle_end[1] + 3), (0, 0, 255), -1)
					cv2.line(black_bgr, center, circle_start, (0, 255, 0))
					cv2.line(black_bgr, center, circle_end, (0, 0, 255))

				angle = 180 + angleZeroRad(gap[0], center)
			except Exception as x:
				traceback.print_exc()
				pass
			mask, read = read_data_from_center(black_bgr, center, radius, angle, minDist, maxDistCheck)
			read = read.tolist()
	else:
		black_bgr = None
		read = []

	return black_bgr, read



# computes angle of vector from center in reference to zero PI
def angleZeroRad(center, vector):
	angle = np.rad2deg(np.arctan2(vector[1] - center[1], vector[0] - center[0]))
	return angle




# reads a glyph radially from its center
# returns the mask(?) and a list of read data
def read_data_from_center(mask, center, radius, angle, min_dist, max_dist_check):
	# todo tune readsplits
	readSplits = 3600
	# reads data from frame in which a valid circle has been detected
	radAngle = (angle)/180 * math.pi
	#reads thickness of sign radially
	result = []
	for ang in np.linspace(0, 2 * math.pi, readSplits):
		pixelSum = 0
		for pixel in range(int(min_dist), int(round(radius*max_dist_check))):
			pX = int(round(pixel * math.cos(ang + radAngle) + center[0]))
			pY = int(round(pixel * math.sin(ang + radAngle) + center[1]))

			if pX >= 0 and pX < mask.shape[1] and pY >= 0 and pY < mask.shape[0]:
				if mask[pY][pX][0] > 0:
					pixelSum += 1
					# mask[pY,pX] = (255,0,0)
			else:
				break
		result.append(pixelSum)

	result = np.array(result)
	result = np.trim_zeros(result, trim="f")
	result = np.pad(result, (0, (readSplits - len(result)) % readSplits), 'constant')
	result = result/radius*1000
	# result[result == 0] = -1

	return mask, result



# finds the beginning and end of a given glyph
# returns the mask, (start, end) of gap, percentage of inliers and the minimum radius for later read
def find_ends(mask, center, radius, minDist, maxDistCheck):
	start, end = None, None
	inliers = 0
	min_radius = None

	# compute necessary reads and double for good measure:
	read_splits = 2 * math.pi * radius * 2

	last = None
	this_coords = ()
	last_coords = ()
	gap = []

	for ang in np.linspace(int(round(radius/2)), 2 * math.pi, read_splits):
		found = False

		for pixel in range(int(round(radius*minDist)), int(round(radius*maxDistCheck))):
			pX = int(round(pixel * math.cos(ang) + center[0]))
			pY = int(round(pixel * math.sin(ang) + center[1]))
			this_coords = (pX,pY)

			if pX >= 0 and pX < mask.shape[1] and pY >= 0 and pY < mask.shape[0]:
				if(mask[pY][pX]) != 0:
					found = True
					inliers += 1
					distance_to_center = distance(center, this_coords)
					if min_radius is None or distance_to_center < min_radius:
						min_radius = distance_to_center
					break
			else:
				break

		if last != None:
			if found and not last:
				start = this_coords

			if not found and last:
				end = last_coords

			if start is not None and end is not None:
				gap = [start, end]
				# print("start: ", start)
				# print("end: ", end)


		last = found
		last_coords = this_coords

	mask = cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR)
	cv2.circle(mask,center,1,(255,255,255),1)

	return mask, gap, inliers, min_radius



# To move to result display

# shows graph to compare results
# def print_graphs(results):
# 	if results:
# 		for d in results:
# 			plt.plot(d)
# 		plt.ylabel("read and normaized value")
# 		plt.show()