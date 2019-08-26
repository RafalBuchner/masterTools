
def rotate( P,angle, originPoint):
    """Rotates x/y around x_orig/y_orig by angle and returns result as [x,y]."""
    alfa = angle
    px,py=P
    originPointX, originPointY = originPoint

    x = ( px - originPointX ) * math.cos( alfa ) - ( py - originPointY ) * math.sin( alfa ) + originPointX
    y = ( px - originPointX ) * math.sin( alfa ) + ( py - originPointY ) * math.cos( alfa ) + originPointY

    return x, y

def angle(p1, p2):
        p1x, p1y = p1
        p2x, p2y = p2
        return math.atan2(p2x - p1x, p2y - p1y)

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