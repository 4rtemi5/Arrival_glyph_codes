#
# Random utils used in the code
#

# Computes the Euclidian distance between two point
def distance(p1, p2):
	return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

# Computes the center and the radius of a circle defined by 3 points
def get_circle_from_points(a,b,c):
	x, y, z = complex(a[0], a[1]), complex(b[0], b[1]), complex(c[0], c[1])
	w = z - x
	w /= y - x
	c = (x - y) * (w - abs(w) ** 2) / 2j / w.imag - x
	return (int(round(-c.real)), int(round(-c.imag))), int(round(abs(c + x)))