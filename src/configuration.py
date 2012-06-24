import ConfigParser, re, StringIO
from common import norm_path


default_config = StringIO.StringIO("""
[DEFAULT]
do = True
log = True

[general]
server_port = 18000
slave_port = 18001
""")



class Configuration(ConfigParser.SafeConfigParser):
    """ Creates a new Configuration object. Data sources are evaluated in order:
        
    cmd_config
      Additional configuration from the command line, section.key=value,...
          
    case_config
      Case configuration file
          
    global_config
      Global configuration file
          
    defaults
      A dictionary of default values """
        
    def __init__(self, case_config = None, cmd_config = None, global_config = "~/.flof", defaults = None):
        
        ConfigParser.SafeConfigParser.__init__(self, defaults=defaults)

        self.readfp(default_config)
        default_config.seek(0) # Rewind default_config after usage
        
        self.read(norm_path(global_config))
        if case_config:
            case_config = norm_path(case_config)
            self.read(case_config)
            self.case_config = case_config
        if cmd_config:
            self.merge_config(cmd_config)


    def update_defaults(self, defaults):
        """ Updates the defaults. This is needed because the DEFAULT section can't be modified directly.
        Code taken from ConfigParser.py """        
        if defaults:
            for key, value in defaults.items():
                self._defaults[self.optionxform(key)] = value

               
    def merge_config(self, args):
        """ Merge configuration options from the command line.
        Syntax: section.key=value,... """
        for a in args.split(","):
            parts = re.split(r"\.|=", a, maxsplit=2)
            if not len(parts) == 3:
                continue
            if parts[0] == "DEFAULT": # Modifying the DEFAULT section needs special treatment
                self.update_defaults( {parts[1] : parts[2]} )
                continue
            try:
                self.add_section(parts[0])
            except ConfigParser.DuplicateSectionError:
                pass
            self.set(*parts)

            
    def get(self, section, option, raw=False, vars={}):
        i_dict = self._interp_dict
        i_dict.update(vars)
        return ConfigParser.SafeConfigParser.get(self, section, option, raw, i_dict)

    @property
    def _interp_dict(self):
        """ Returns a dictionary that contains additional values for interpolation.
        For each [section] with key there will be an interpolation entry like
        section.key which can be used. """
        i_dict = {}
        for section in self.sections():
            for item in self.items(section, raw=True):
                i_dict[section + "." + item[0]] = item[1] 
        return i_dict

    
    def option_dict(self, section):
        """ Returns a dictionary that contains all option key/values from the named section. Ensures that do is a boolean. """
        d = dict(self.items(section))

        try:
            d["do"] = self.getboolean(section, "do")
        except:
            pass
        
        return d
