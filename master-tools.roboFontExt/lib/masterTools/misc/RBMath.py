"""
Author: Rafal Buchner
Date: 30.8.2018

Warning: this code is compatible only with RoboFont3!!!

"""
from __future__ import division
from fontTools.misc.bezierTools import splitCubicAtT, splitQuadraticAtT
# import line_profiler
import math

def getClosestInfo(cursorPoint, segment, *points):
    """
        returns info about closest point on curve
    """
    curve, info = closestPointAndT_binaryIndexSearch_withSegments(cursorPoint, segment, *points)
    closestPoint = calcSeg(0.5,*curve)
    return (closestPoint, info)

def closestPointAndT_binaryIndexSearch_withSegments(pointOffCurve, segment, *segPoints):
    """Returns returns the curve, which is segment cutted from the given curve. 
        it returns more info on curve than method closestPointAndT_binaryIndexSearch.
        Therefore it is heavier
    """
    curveDiv = 12

    lowerBound = 0
    upperBound = curveDiv - 1
    found = False
    count = 0
    points = segPoints
    while found == False:

        if count == 10:
            break
        count += 1
        #print(f"closestPointAndT_binaryIndexSearch\nlen{len(points)}\npoints{points}")###TESt
        LUT = getLut(segment.type, curveDiv, *points)
        minimalDist = 20000


        for i in range(curveDiv+1):
            n = (i,i/curveDiv)
            # print(f"\n\n\nTEST::::::\n {LUT}\n\n\n")
            distance = lenghtAB(pointOffCurve, LUT[n])

            if distance < minimalDist:
                minimalDist = distance
                t = n[1]


        points1,points2 = splitSegAtT(segment.type,points,.5)

        if t >= .5:
            points = points2

        else:
            points = points1

    return (points, (segment.contour.index, segment.index, segPoints))


def closestPointAndT_binaryIndexSearch(pointOffCurve,segType, *points):
    """Returns returns the curve, which is segment cutted from the given curve. """

    ### Quicker?
    # if segType != 'qcurve':
    #     curveDiv = 3
    # else:
    #     curveDiv = 12
    curveDiv = 12

    lowerBound = 0
    upperBound = curveDiv - 1
    found = False
    count = 0
    while found == False:

        if count == 10:
            break
        count += 1
        #print(f"closestPointAndT_binaryIndexSearch\nlen{len(points)}\npoints{points}")###TESt
        LUT = getLut(segType, curveDiv, *points)
        minimalDist = 20000


        for i in range(curveDiv+1):
            n = (i,i/curveDiv)
            # print(f"\n\n\nTEST::::::\n {LUT}\n\n\n")
            distance = lenghtAB(pointOffCurve, LUT[n])

            if distance < minimalDist:
                minimalDist = distance
                t = n[1]


        points1,points2 = splitSegAtT(segType,points,.5)

        if t >= .5:
            points = points2

        else:
            points = points1

    return points

def stemThicnkessGuidelines(cursorPoint,segType, *points):
    """
        calculate guidelines for stem thickness
        returnt two lines, every line has two points
        every point is represented as a touple with x, y values
    """
    #print(f"stemThicnkessGuidelines\nlen{len(points)}\npoints{points}")###TESt
    curve = closestPointAndT_binaryIndexSearch(cursorPoint,segType, *points)
    closestPointx,closestPointy = calcSeg(0.5,*curve)

    guide1,guide2 = getPerpedicularLineToTangent(segType,.5,*curve)
    guide1A,guide1B = guide1
    guide2A,guide2B = guide2

    guide1Ax,guide1Ay = guide1A
    guide1Bx,guide1By = guide1B
    guide2Ax,guide2Ay = guide2A
    guide2Bx,guide2By = guide2B

    guide1Ax += closestPointx
    guide1Ay += closestPointy
    guide1Bx += closestPointx
    guide1By += closestPointy
    guide2Ax += closestPointx
    guide2Ay += closestPointy
    guide2Bx += closestPointx
    guide2By += closestPointy

    return ((guide1Ax,guide1Ay),(guide1Bx,guide1By)),((guide2Ax,guide2Ay),(guide2Bx,guide2By))


def getLut( segType, accuracy=12, *points):
    """Returns Look Up Table, which contains pointsOnPath for calcBezier/calcLine,
    if getT=True then returns table with points and their factors"""
    lut_table = {}

    #print(f"getLut\nlen{len(points)}\npoints{points}")###TESt

    # print('otherCurve') ###TEST
    for i in range(accuracy+1):
        t=i/accuracy

        if len(points) == 4 and segType != "qcurve":
            calc = calcBezier(t,*points)

        elif len(points) == 4 and segType == "qcurve":
            calc = calcQbezier(t,*points)

        elif len(points) == 2:
            calc = calcLine(t,*points)

        lut_table[(i,t)] = calc
        #######
    # if segType == "qcurve":
    #
    #     accuracy = 12
    #     for i in range(accuracy+1):
    #         t=i/accuracy
    #         calc = calcQbezier(t,*points)
    #         lut_table[(i,t)] = calc
    # print(lut_table) ###TEST
    return lut_table


def sortPointsDistances(myPoint,points):

    def _sorter(point):
        return lenghtAB(myPoint, point)

    points = sorted(points, key=_sorter)
    return points

def bs(searchFor,array):
    lowerBound = 0
    upperBound = len(array)-1
    found = False

    while found == False and lowerBound <= upperBound:
        midpoint = (lowerBound + upperBound)//2

        if array[midpoint] == searchFor:
            found = True
            return midpoint

        elif array[midpoint] < searchFor:
            lowerBound = midpoint + 1
        elif array[midpoint] >= searchFor:
            upperBound = midpoint - 1

    raise AssertionError("The value wasn't found in the array")

def splitSegAtT(segType, points,*t):
    if len(points) == 2:
        assert isinstance(t[0], float), "splitSegAtT ERROR: t is not a float"
        a,b = points
        segments = splitLineAtT(a,b, *t)
    if len(points) == 4:

        a,b,c,d = points
        if segType == "qcurve":####WIP
            segments = splitQatT(a,b,c,d, *t)
        else:
            segments = splitCubicAtT(a,b,c,d, *t)

    return segments
def splitQatT(p1,h1,h2,p2, t):########WIP NIE SĄDZĘ ABY MOJ POMYSL DZIALAL


    """divides ROBOFONT quadratic bezier paths (wich are strange, stored as pairs of two curves) into two, t factor here is only for having consistency between this version and cubic. This factor should be 0.5"""
    c = calcLine(.5,h1,h2)
    split_1 = splitQuadraticAtT(p1,h1,c,t)
    split_2 = splitQuadraticAtT(p2,h2,c,t)
    div1 = [split_1[0][0],split_1[0][1],split_1[1][1],split_1[1][2]]
    div2 = list(reversed([split_2[0][0],split_2[0][1],split_2[1][1],split_2[1][2]]))
    return [div1,div2]

def splitLineAtT(a,b, *ts):
    '''Splits line into two at given t-factors (where 1>t>0)
    sort t-factors before using it1'''
    ### very bad code

    if a != b:###AVODING ERROR - IF a = b, than calcLine break, t is equal to those points
        ts = [a] + list(ts) + [b]
        lines = []
        for i in range(len(ts)):

            if ts[i] == a and ts[i] != b :
                A = ts[i]
            else:
                A = calcLine(ts[i], a,b)


            if ts[i+1] == b and ts[i+1] != a :
                B = ts[-1]
            else:
                B = calcLine(ts[i+1], a,b)


            myLine = (A,B)
            lines.append(myLine)
            if ts[i+1] == b:
                break
    else:###ERROR
        lines = [(a,b),(a,b)]
    return lines

def calcSeg(t,*points):
    assert isinstance(t,float), "calcSeg ERROR: t is not a float"
    if len(points) == 2:
        a,b = points
        point = calcLine(t,a,b)
    if len(points) == 4:
        a,b,c,d = points
        point = calcBezier(t,a,b,c,d)

    return point

def lenghtAB(A,B):
    """Returns distance value between two points: A and B"""
    bx,by = B
    ax,ay = A
    sqA = (bx - ax) **2
    sqB = (by - ay) **2
    sqC = sqA + sqB
    if sqC > 0:
        lengthAB = math.sqrt(sqC)
        return lengthAB
    else:
        return 0

def rotatePoint( P,angle, originPoint):
    """Rotates x/y around x_orig/y_orig by angle and returns result as [x,y]."""
    alfa = math.radians(angle)
    px,py=P
    originPointX, originPointY = originPoint

    x = ( px - originPointX ) * math.cos( alfa ) - ( py - originPointY ) * math.sin( alfa ) + originPointX
    y = ( px - originPointX ) * math.sin( alfa ) + ( py - originPointY ) * math.cos( alfa ) + originPointY

    return x, y

def angle( A, B ):
    """returns angle between line AB and axis x"""
    ax, ay = A
    bx, by = B
    xDiff = ax - bx
    yDiff = ay - by
    if yDiff== 0 or xDiff== 0 and ay == by:
        angle = 0
    elif yDiff== 0 or xDiff== 0 and ax == bx:
        angle = 90
    else:
        tangens = yDiff / xDiff
        angle = math.degrees(math.atan( tangens ))


    return angle

def calcBezier(t, *pointList):
    """returns coordinates for factor called "t"(from 0 to 1). Based on cubic bezier formula.
    """
    assert len(pointList) == 4 and isinstance(t, float)
    p1x,p1y = pointList[0]
    p2x,p2y = pointList[1]
    p3x,p3y = pointList[2]
    p4x,p4y = pointList[3]

    x = p1x*(1-t)**3 + p2x*3*t*(1-t)**2 + p3x*3*t**2*(1-t) + p4x*t**3
    y = p1y*(1-t)**3 + p2y*3*t*(1-t)**2 + p3y*3*t**2*(1-t) + p4y*t**3

    return x, y

def calcQbezier(t,*pointList):
    """returns coordinates for factor called "t"(from 0 to 1). Based on Quadratic Bezier formula.
    """
    def calcQuadraticBezier(t,*pointList):
        assert len(pointList) == 3 and isinstance(t, float)
        p1x,p1y = pointList[0]
        p2x,p2y = pointList[1]
        p3x,p3y = pointList[2]
        x = (1-t)**2*p1x + 2*(1-t)*t*p2x+t**2*p3x
        y = (1-t)**2*p1y + 2*(1-t)*t*p2y+t**2*p3y
        return x, y

    assert len(pointList) == 4 and isinstance(t, float)
    p1 = pointList[0]
    h1 = pointList[1]
    h2 = pointList[2]
    p2 = pointList[3]
    c = calcLine(.5, h1,h2)
    if t <= 0.5:
        t_segment = t*2
        return calcQuadraticBezier(t_segment,p1,h1,c)
    else:
        t_segment = (t-0.5)*2
        return calcQuadraticBezier(t_segment,p2,h2,c)




def calcLine(t, *pointList):
    """returns coordinates for factor called "t"(from 0 to 1). Based on cubic bezier formula.
    """
    assert len(pointList) == 2 and isinstance(t, float)

    p1x,p1y = pointList[0]
    p2x,p2y = pointList[1]

    x = interpolation(p1x,p2x,t)
    y = interpolation(p1y,p2y,t)

    return x, y


def interpolation(v1, v2, t):
    """one-dimentional bezier curve equation for interpolating"""
    vt = v1 * (1 - t) + v2 * t
    return vt

def derivativeBezier(t,*pointList):
    """ calculates derivative values for given control points and current t-factor """
    ### http://www.idav.ucdavis.edu/education/CAGDNotes/Quadratic-Bezier-Curves.pdf ### Quadratic
    p1x,p1y = pointList[0]
    p2x,p2y = pointList[1]
    p3x,p3y = pointList[2]
    p4x,p4y = pointList[3]

    summaX = -3*p1x*(1 - t)**2 + p2x*(3*(1 - t)**2 - 6*(1 - t)*t) + p3x*(6*(1 - t)*t - 3*t**2) + 3*p4x*t**2
    summaY = -3*p1y*(1 - t)**2 + p2y*(3*(1 - t)**2 - 6*(1 - t)*t) + p3y*(6*(1 - t)*t - 3*t**2) + 3*p4y*t**2

    return summaX,summaY
def derivativeQBezier(t,*pointList):
    def derivativeQuadraticBezier(t,*pointList):
        """ calculates derivative values for given control points and current t-factor """
        p1x,p1y = pointList[0]
        p2x,p2y = pointList[1]
        p3x,p3y = pointList[2]

        summaY = 2*(1-t)*(p2y-p1y) + 2*t*(p3y-p2y)
        summaX = 2*(1-t)*(p2x-p1x) + 2*t*(p3x-p2x)

        return summaX,summaY

    assert len(pointList) == 4 and isinstance(t, float)
    p1 = pointList[0]
    h1 = pointList[1]
    h2 = pointList[2]
    p2 = pointList[3]
    c = calcLine(.5, h1,h2)
    if t <= 0.5:
        t_segment = t*2
        return derivativeQuadraticBezier(t_segment,p1,h1,c)
    else:
        t_segment = (t-0.5)*2
        return derivativeQuadraticBezier(t_segment,p2,h2,c)


def calculateTangentAngle(segType,t, *points):
    """Calculates tangent angle for curve's/lines's current t-factor"""
    if len(points) == 4 and segType != "qcurve":
        xT,yT = calcBezier(t, *points)
        xB,yB = derivativeBezier(t,*points)
    if len(points) == 4 and segType == "qcurve":
        xT,yT = calcQbezier(t, *points)
        xB,yB = derivativeQBezier(t,*points)
    if len(points) == 2:
        xB,yB = points[-1]

    return angle((0,0),(xB,yB))

def getPerpedicularLineToTangent(segType,t,*points):
    """ Calculates 2 perpedicular lines to curve's/line's tangent angle with current t-factor. It places it in the position 00
        returnt two lines, every line has two points
        every point is represented as a touple with x, y values.
        Lines starting point is at 0,0 of canvas
    """

    if len(points) == 4 and segType != "qcurve":
        # P1,P2,P3,P4 = points
        xT,yT = calcBezier(t, *points)
        if t == 0: # exception for dividing by zero in calculateTangentAngle
            t = 0.001

        tanAngle = calculateTangentAngle(segType,t, *points)

    if len(points) == 4 and segType == "qcurve":
        # P1,P2,P3,P4 = points
        xT,yT = calcQbezier(t, *points)
        if t == 0: # exception for dividing by zero in calculateTangentAngle
            t = 0.001

        tanAngle = calculateTangentAngle(segType,t, *points)

    if len(points) == 2:
        xT,yT = calcLine(t, *points)
        A,B = points
        xa,ya=A
        xb,yb=B
        tanAngle = angle(A,B)

        if (ya-yb) == 0 and xa != xb: # exception for horizontal lines
            tanAngle = 0
        elif (xa-xb) == 0 and ya != yb: # exception for vertical lines
            tanAngle = 90


    tanPx1,tanPy1 = rotatePoint( (0,1000),tanAngle, (0,0)) # oneLine
    tanPx2,tanPy2 = rotatePoint( (0,1000),tanAngle-180, (0,0)) # secondLine - extention of the second line in the other direction
    return ((tanPx1,tanPy1),(0,0)) , ((0,0),(tanPx2,tanPy2))
