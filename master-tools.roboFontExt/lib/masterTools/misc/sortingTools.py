from fontTools.pens.pointPen import AbstractPointPen

class SortingPen(AbstractPointPen):
    
    def __init__(self):
        self._contours = []
        self._components = []
        
    def beginPath(self):
        self._contours.append([])
                       
    def addPoint(self, pt, segmentType=None, smooth=False, name=None, identifier=None, **kwargs):
        self._contours[-1].append((pt, segmentType, smooth, name, identifier, *kwargs))
        
    def addComponent(self, baseGlyphName, transformation, identifier=None, **kwargs):
        self._components += [(baseGlyphName, transformation, identifier, *kwargs)]
        
    def endPath(self):
        pass

    def sortContoursByIndexes(self, indexes):
        print(len(indexes) == len(self._contours),len(indexes),len(self._contours))
        assert len(indexes) == len(self._contours), 'number of indexes should be the same as contours'
        assert all(isinstance(x, int) for x in indexes), 'all indexes should be intigers'
        
        contours_ = []
        for i in indexes:
            contours_ += [self._contours[i]]
        self._contours = contours_
        
    def sortComponentsByIndexes(self, indexes):
        assert len(indexes) == len(self._components), 'number of indexes should be the same as components'
        assert all(isinstance(x, int) for x in indexes), 'all indexes should be intigers'
        
        components_ = []
        for i in indexes:
            components_ += [self._components[i]]
        self._components = components_

def rearrangeOrder(glyph, newContourIndexes=None,newComponentIndexes=None,):
    '''
        map current contours or components 
        with given arrays of reordered indexes
    '''
    
    pen = SortingPen()
    glyph.drawPoints(pen)
    pointPen = glyph.getPointPen()
    if newContourIndexes is not None:
        pen.sortContoursByIndexes(newContourIndexes)
    if newComponentIndexes is not None:
        pen.sortComponentsByIndexes(newComponentIndexes)
    glyph.clear()
    
    for contour in pen._contours:
        pointPen.beginPath()
        for point in contour:
            pointPen.addPoint(*point)
        pointPen.endPath()
        
    for component in pen._components:
        pointPen.addComponent(*component)

def reorderContourToIndex(glyph, oldContourIndex, toNewIndex):
    indexOrder = list(range(len(glyph.contours)))
    indexOrder.insert(toNewIndex, indexOrder.pop(oldContourIndex))
    rearrangeOrder(glyph,newContourIndexes=indexOrder)

def reorderComponentToIndex(glyph, oldComponentIndex, toNewIndex):
    indexOrder = list(range(len(glyph.components)))
    indexOrder.insert(toNewIndex, indexOrder.pop(oldComponentIndex))
    rearrangeOrder(glyph,newComponentIndexes=indexOrder)
