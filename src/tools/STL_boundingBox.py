#!env python2

import fileinput, sys

if len(sys.argv) == 1:
    print "Calculates max/min values of vertexes from all files."
    print "Usage: %s FILES" % sys.argv[0]
    sys.exit()

max_x = max_y = max_z = -sys.maxint -1
min_x = min_y = min_z = sys.maxint


for line in fileinput.input():
    if line.strip().startswith("vertex"):
        coords = [ float(i) for i in line.split()[1:] ]
        max_x = coords[0] if coords[0] > max_x else max_x
        min_x = coords[0] if coords[0] < min_x else min_x

        max_y = coords[1] if coords[1] > max_y else max_y
        min_y = coords[1] if coords[1] < min_y else min_y

        max_z = coords[2] if coords[2] > max_z else max_z
        min_z = coords[2] if coords[2] < min_z else min_z


print "Max X: %s  Min X: %s" % (max_x, min_x)
print "Max Y: %s  Min Y: %s" % (max_y, min_y)
print "Max Z: %s  Min Z: %s" % (max_z, min_z)
