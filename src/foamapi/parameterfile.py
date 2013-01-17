from pyparsing import Dict, Forward, Group, Literal, SkipTo, Word, ZeroOrMore
from pyparsing import alphanums, cStyleComment, cppStyleComment
from pyparsing import ParseResults

from common import norm_path


class ParameterFile():
    def __init__(self, filename):
        self.path = norm_path(filename)
        parsed = self._grammar.parseFile(self.path, parseAll=True)
        self._data = self._as_dict(parsed)
        
    @property
    def _grammar(self):        
        ident = Word(alphanums + ".")
        semi = Literal(";").suppress()
        # lrb =  Literal("(").suppress()
        # rrb =  Literal(")").suppress()
        lcb =  Literal("{").suppress()
        rcb =  Literal("}").suppress()

        Value = SkipTo(semi)
        KeyValue = Dict(Group(ident + Value + semi))
        Dictionary = Forward()
        Block = lcb + ZeroOrMore(Dictionary | KeyValue) + rcb
        Dictionary << Dict(Group(ident + Block))
        ParameterFile = ZeroOrMore(Dictionary |  KeyValue)
        
        ParameterFile.ignore(cStyleComment)
        ParameterFile.ignore(cppStyleComment)

        return ParameterFile

    def _as_dict(self, parse_results):
        """ Recursively converts the ParseResults object to a dict. """
        d = parse_results.asDict()
        for i in d:
            if type(d[i]) == ParseResults:
                d[i] = self._as_dict(d[i])
        return d
                
                    
    def write(self, filename = None):
        """ Write file to disc. If no filename is specified, save under the same name as opened. """
        if filename:
            fd = file(filename, "w")
        else:
            fd = file(self.path, "w")

        # First write the FoamFile header
        header = ""
        try:
            d = self._data["FoamFile"]
            header += "FoamFile" + "\n"
            header += "{" + "\n"
            header += self._write_dict(d, 4)
            header += "}" + "\n\n"
        except KeyError:
            pass
        
        fd.write(header + self._write_dict(self._data))
        
        

    def _write_dict(self, data, indent = 0):
        str_keyval = ""
        str_dict = ""
        indention = " " * indent
                
        for k in data:
            v = data[k]
            if k == "FoamFile" and type(v) == dict:
                pass # Header has already been written
            elif type(v) == dict:
                str_dict += "\n" + indention + k + "\n"
                str_dict += indention + "{" + "\n"
                str_dict += self._write_dict(v, indent+4)
                str_dict += indention + "}" + "\n"
            else:
                str_keyval += indention + k + " " + v + ";\n"
                
        return str_keyval + str_dict

                
    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __len__(self):
        return len(self._data)
   
