import cv2
import numpy as np
from scripts.samples_reader import *
from scripts.process_frame import process_frame
from scripts.result_display import *
from scripts.decode_frame import *

# Processes every picture in the given lists, that is, glyphs and numbers.
# If the debug flag is set to true, the intermediary outputs created by process_frame
# are saved.
def process_pictures(glyphs, numbers, debug = False):
	for folder, file, img in image_samples(glyphs, numbers):
		print("Processing image glpyh", file)

		processed, int1 = process_frame(img)
		data, int2 = decode_frame(processed)

		intermediary = int1 + int2

		if debug:
			#display_photo_parallel(file, intermediary, save = True)
			display_photo_sequential(file, intermediary, save = True)



# Processes every video in the given lists, that is, glyphs and numbers.
# If the debug flag is set to true, the intermediary outputs created are saved.
def process_videos(glyphs, numbers, debug=False):

	for folder, file, video in video_samples(glyphs, numbers):
		print("Processing video glpyh", file)

		if debug: outs = None

		stillReading = True
		while stillReading:
			stillReading, frame = video.read()

			if not stillReading : break

			processed, intermediary = process_frame(frame)

			if debug:
				# Only on the first time, outs is filled
				if outs is None:
					# Gets the names of the intermeriary outputs
					int_names = map(lambda i : i[0], intermediary) 
					# Creates a video output stream for each intermediary
					outs = create_output_video_streams(file, int_names, (1280, 720)) 

				# The current intermediaries are written to the relative output streams
				write_intermediaries_to_videos(intermediary, outs, (1280, 720))

		if debug:
			# The various output streams are closed
			close_output_video_streams(outs)
