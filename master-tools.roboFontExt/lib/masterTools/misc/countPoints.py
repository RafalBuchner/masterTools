# coding: utf-8
def countContourPoints(c):
    count = 0
    for s in c:
        for p in s:
            count += 1
    return count

def countGlyphCurvesPoints(g,contourIndexes=False):
    """ Returns list that contains number of points for every countur in the glyph
        If contourIndexes, returns also list with indexes of contours
    """
    glyphCurvesPoints = []
    cIndexes = []
    for i in range(len(g)):
        if contourIndexes:
          cIndexes.append(i)
        glyphCurvesPoints.append(countContourPoints(g[i]))

    if contourIndexes:
        return  glyphCurvesPoints, cIndexes
    else:
        return glyphCurvesPoints

def compatibilityCheck(currGlyph,fonts):
    """Checks if the glyphs across the familly are compatible (all of the ufos have to be opened in RF)"""
    compatibility = True
    listOfnumOfPoints = []
    for font in fonts:

        glyph = font[currGlyph.name]
        # print(currGlyph.font, type(currGlyph), font, type(glyph))
        if not currGlyph.isCompatible(glyph):
            compatibility = False
            break

        # step:1 checks number of points, including BCPs: RF g.isCompatible doesn't check this
        numOfPointsPerContour = countGlyphCurvesPoints(glyph)
        listOfnumOfPoints.append(numOfPointsPerContour)

    if compatibility: # step:2 checks number of points, including BCPs: RF g.isCompatible doesn't check this
        compatibility = all(x==listOfnumOfPoints[0] for x in listOfnumOfPoints)

    return compatibility





