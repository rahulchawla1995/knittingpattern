"""Build SVG files


"""
import xmltodict

SVG_FILE = """
<svg xmlns:ns="http://PURL.org/dc/elements/1.1/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" version="1.1">
    <title>knittingpattern</title>
    <defs></defs>
</svg>"""
END_OF_SVG_FILE = """</svg>"""
ELEMENT_STRING = """        <g transform=\"translate({x},{y})\">
        {content}
    </g>"""
LAYER_START = """    <g class="row" id="{id}" inkscape:label="{id}"
                      inkscape:groupmode="layer">"""
LAYER_END = """    </g>"""


class SVGBuilder(object):
    """This class builds an SVG to a file.

    The class itself does not know what the objects look like.
    It offers a more convinient interface to build SVG files.
    """

    def __init__(self):
        """Initialize this object with the file for the SVG."""
        self._structure = xmltodict.parse(SVG_FILE)
        self._layer_id_to_layer = {}
        self._svg = self._structure["svg"]
    
    @property
    def bounding_box(self):
        """Returns (min_x, min_y, max_x, max_y)"""
        return (self._min_x, self._min_y, self._max_x, self._max_y)
        
    @bounding_box.setter
    def bounding_box(self, bbox):
        min_x, min_y, max_x, max_y = bbox
        self._min_x = min_x
        self._min_y = min_y
        self._max_x = max_x
        self._max_y = max_y
        self._svg["@height"] = str(max_y - min_y)
        self._svg["@width"] = str(max_x - min_x)
        self._svg["@viewBox"] = "{} {} {} {}".format(*bbox)


    def place(self, x, y, svg, layer_id):
        """Place the `svg` content at `(x, y)` position in the file, in
        a layer with the id `layer_id`.

        This can be used to place instructions in layers."""
        content = xmltodict.parse(svg)
        content["@transform"] = "translate({},{})".format(x, y)
        layer = self._get_layer(layer_id)
        layer["g"].append(content)
        
    def _get_layer(self, layer_id):
        if layer_id not in self._layer_id_to_layer:
            self._svg.setdefault("g", [])
            layer = {
                    "g":[], 
                    "@inkscape:label": layer_id,
                    "@id": layer_id,
                    "@inkscape:groupmode":"layer"
                }
            self._layer_id_to_layer[layer_id] = layer
            self._svg["g"].append(layer)
        return self._layer_id_to_layer[layer_id]
        
    def write_to_file(self, file):
        """Writes to the file"""
        xmltodict.unparse(self._structure, file, pretty=True)


__all__ = [
        "SVGBuilder", "START_OF_SVG_FILE", "END_OF_SVG_FILE",
        "ELEMENT_STRING", "ROW_START", "ROW_END"
    ]
