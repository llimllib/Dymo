from math import ceil, log

from shapely.geometry import Point

from ModestMaps.OpenStreetMap import Provider
from ModestMaps.Core import Coordinate

class Index:
    """ Primitive quadtree for checking collisions based on a known radius.
    """
    def __init__(self, zoom, radius):
        """ Zoom is the base zoom level we're annealing to, radius is
            the pixel radius around each place to check for collisions.
        """
        self.zoom = zoom
        self.diff = ceil(log(radius * 2) / log(2))
        self.radius = radius
        self.quads = {}
    
    def add(self, name, location):
        """ Add a new place name and location to the index.
        """
        coord = Provider().locationCoordinate(location).zoomTo(self.zoom + 8)
        point = Point(coord.column, coord.row)
        
        area = point.buffer(self.radius, 4)
        xmin, ymin, xmax, ymax = area.bounds

        quads = [quadkey(Coordinate(y, x, self.zoom + 8).zoomBy(-self.diff))
                 for (x, y) in ((xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin))]
        
        for quad in set(quads):
            if quad in self.quads:
                self.quads[quad].append((name, area))
            else:
                self.quads[quad] = [(name, area)]
    
    def blocks(self, location):
        """ If the location is blocked by some other location
            in the index, return the blocker's name or False.
        """
        coord = Provider().locationCoordinate(location).zoomTo(self.zoom + 8)
        point = Point(coord.column, coord.row)
        
        coord = coord.zoomBy(-self.diff)
        key = quadkey(coord)
        
        if key in self.quads:
            for (name, area) in self.quads[key]:
                if point.intersects(area):
                    return name or True
        
        return False

def quadkey(coord):
    return str(coord.container())