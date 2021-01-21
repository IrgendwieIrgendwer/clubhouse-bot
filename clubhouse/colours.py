from PyDrocsid.material_colours import MaterialColours, NestedInt
from discord import Colour


class Colours(MaterialColours):
    # General
    error = MaterialColours.red
    blue = MaterialColours.blue

    github = MaterialColours.teal[800]
    info = MaterialColours.indigo
    ping = MaterialColours.green["a700"]
    prefix = MaterialColours.indigo
    version = MaterialColours.indigo
