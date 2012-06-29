#!/usr/bin/python2

import optparse, sys, os, string

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile 

def add_options():
    """ Factory function for the OptionParser. """
    parser = optparse.OptionParser(usage="%prog [options] CASE PFCBFILE")
    parser.add_option("-t", "--timestep", default="0", help="Timestep to take the boundary information from. Defaults to 0.")
    parser.add_option("-v", "--variable", default="U", help="Variable to take boundary information form. Defaults to U.")
    return parser



def boundaries(filename):
    """ Extracts the boundaries from the filename. """
    template = '      <boundary name="%s" description="%s" pattern="%s" /> \n'
    text = ""
    ppf = ParsedParameterFile(filename)
    for boundary in ppf["boundaryField"]:
        text += template % (str(boundary), str(boundary), str(boundary))
    return text

def param_dict(bc_data):
    """ Remove the type attribute from the bc_data and returns the string representation. """
    try:
        del bc_data["type"]
    except KeyError:
        pass
    s= str(bc_data)
    return s[1:-1]
    
    
def fields(files):
    bc_templ = '''          <bc name="%s" type="%s" /> \n'''
    bc_templ_params = '''          <bc name="%s" type="%s" parameters="%s" /> \n'''
    text = ""

    for f in files:
        vals = {}
        ppf = ParsedParameterFile(f)
        vals["field_name"] = os.path.split(f)[-1]
        vals["ic_value"] = str(ppf["internalField"])[8:] # Strip the uniform in front
        vals["bc"] = ""
        for boundary, bc_data in ppf["boundaryField"].items():
            if "value" in bc_data:
                vals["bc"] += bc_templ_params % (boundary, bc_data["type"], param_dict(bc_data))
            else:
                vals["bc"] += bc_templ % (boundary, bc_data["type"])
        text += field_templ % vals
    return text
            
    
def param_files(files):
    """ Lists the parameter files in constant and system. """
    template = '        <file name="%s" /> \n'
    text = ""
    for f in files:
        text += template % f
    return text
    

def main():
    oparser = add_options()
    options, args = oparser.parse_args()
    if not args:
        oparser.print_help()
        sys.exit()

    templ_subst = {}
    case_dir = sys.argv[1]
    for (dirpath, dirnames, filenames) in os.walk(case_dir):
        path_head, path_tail = os.path.split(dirpath)
        if path_tail == options.timestep and path_head == case_dir:
            templ_subst["boundaries"] = boundaries(os.path.join(dirpath, options.variable))
            templ_subst["fields"] = fields( [os.path.join(dirpath, f) for f in filenames] )
        elif path_tail == "constant":
            templ_subst["param_constant"] = param_files(filenames)
        elif path_tail == "system":
            templ_subst["param_system"] = param_files(filenames)


    templ = string.Template(pfcb_template)
    f = open(args[1], "w")
    f.write(templ.safe_substitute(templ_subst))
    f.close()
    print "PFCB File %s created." % f.name
    
    


field_templ = '''
        <field name="%(field_name)s">
	  <ic value="%(ic_value)s"/>
%(bc)s
	  <defaultbc type="not_set" />
        </field>
'''

    
pfcb_template = r"""<?xml version="1.0"?>
<!DOCTYPE casebuilder SYSTEM "casebuilder.dtd" >

<casebuilder name="Autogenerated PFCB file" 
	     version="1"
	     description="Case Description" 
	     template="case.template">
  <helptext>
    some help
  </helptext>

  <arguments />

  <meshpreparation> <copy template="case.mesh" time="0" /> </meshpreparation> 
  
  <files>
    <boundaries>
$boundaries
    </boundaries>

    <parameterfiles>
      <directory name="constant">
$param_constant
      </directory>
      <directory name="system">
$param_system
      </directory>
    </parameterfiles>

    <fieldfiles>
      $fields
    </fieldfiles>

  </files>

</casebuilder>
"""


if __name__ == "__main__":
    main()
