from mojo.drawingTools import *
def _drawPSCurve(*points):
    p1, h1, h2, p2 = points
    newPath()
    moveTo(p1)
    curveTo(h1, h2, p2)
    drawPath()

def _drawLine(*points):
    line(*points)

def _offsetPoint(p, op):
    x,y = p
    ox,oy = op
    return (x+ox,y+oy)

def _drawPoint(p, scale , s=6, shape='rect'):
            x,y = p
            s = s /scale
            r = s/2
            if shape == 'rect':
                shape = rect
            else:
                shape = oval
            shape(x-r,y-r,s,s)

def _drawBPoints(p, scale, color ,s=6,l=1):
    stroke(None)
    fill(*color)
    _drawPoint(p.anchor, scale)
    if p.bcpIn != (0,0):
        bcpIn = _offsetPoint(p.anchor, p.bcpIn)
        _drawPoint(
                bcpIn, scale, s=6
            )
        save()
        strokeWidth(l/scale)
        stroke(*color)
        line(p.anchor, bcpIn)
        restore()
    if p.bcpOut != (0,0):
        bcpOut = _offsetPoint(p.anchor, p.bcpOut)
        _drawPoint(
            bcpOut, scale, s=6
            )
        save()
        strokeWidth(l/scale)
        stroke(*color)
        line(p.anchor, bcpOut)
        restore()