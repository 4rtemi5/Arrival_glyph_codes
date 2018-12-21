#
# Arrival Glyph Encoder and Decoder
#	by Matteo Nardini and Raphael Pisoni
#

from scripts.process_file import *

def main():

	# ALl glyphs, all numbers
	#glyphs = []
	#numbers = []

	glyphs = ["AbbotIsDead"]
	numbers = ["00"]

	clean_output_folder()

	process_pictures(glyphs, numbers, debug = True)
	#process_videos(glyphs, numbers, debug = True)




if __name__ == "__main__":
	main()
