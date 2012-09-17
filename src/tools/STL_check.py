#!env python2
import fileinput, string, sys


if len(sys.argv) == 1:
    print "Does some basic checks on STL files:"
    print "Checks for well-formed vertices and properly closed solid/endsolid entries."
    print "Usage: %s FILES" % sys.argv[0]
    sys.exit(1)

current_solid = ""

for line in fileinput.input():
    s = line.strip()
    if s.startswith("vertex"):
        if len(s.split(" ")) != 4:
            print s
            print "File %s as not well-formed vertex at line %s" % (fileinput.filename(), fileinput.lineno())

    if fileinput.isfirstline() and current_solid != "":
        print "The file BEFORE %s has a solid not closed by 'endsolid'. Due to limitations by python's fileinput module I can't tell which file that is, sorry!" % fileinput.filename()
        current_solid = ""
            
    if s.startswith("solid"):
        if current_solid != "":
            print "solid %s in file %s not followed by endsolid." % (current_solid, fileinput.filename())
            current_solid = ""
            fileinput.nextfile()
        else:
            current_solid = string.split(s, maxsplit=1)[1]

    if s.startswith("endsolid"):
        if current_solid == "":
            print "endsolid %s in file %s has no preceding solid. " % (current_solid, fileinput.filename())
            
        elif current_solid != string.split(s, maxsplit=1)[1]:
            print "endsolid %s in file %s has wrong named preceding solid. " % (string.split(s, maxsplit=1)[1], fileinput.filename())
            
        current_solid = ""
        fileinput.nextfile()

if current_solid != "":
    print "Solid %s in file %s not closed by 'endsolid'" % (current_solid, fileinput.filename())
        
