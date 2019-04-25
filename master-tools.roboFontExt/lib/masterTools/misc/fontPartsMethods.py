def calculateSelection(g):
    """calculate the real number of highlighted points"""
    # moveTo special misc
    # apply for qcurves!!!
    selectedPoints = 0
    #totalNumber = 0
    for c in g:
        lastSelected = None
        if c.points[-3].selected and c.points[0].selected and c.points[0].type == "curve":
            # print("add+2 a")
            selectedPoints += 2
            lastSelected=c.points[-3]

        iterC = iter(list(c.points))
        next(iterC,None)
        for i,p in enumerate(c.points):
            #totalNumber += 1
            prevP = c.points[i-1]
            if i > len(c.points)-1:
                nextP = next(iterC)
            else:
                nextP=c.points[0]
            if p.selected:
                if lastSelected is not None:
                    if lastSelected == c.points[i-3] and p.type == "curve" and i != 0:
                        # add selected handle points
                        # print("add+2 b")
                        selectedPoints += 2

                else:
                    # if the first selected point has outer handle, add 1
                    if c.points[i-1].type == "offcurve" and p.type != "offcurve":
                        # print("add+1 c")
                        selectedPoints += 1

                # if the last selected point has outer handle, add 1
                if i+3 < len(c.points):
                    if not c.points[i+3].selected and c.points[i+3].type == "curve":
                        # print("add+1 d")
                        selectedPoints += 1
                if i+3 == len(c.points):
                    if not c.points[0].selected and c.points[0].type == "curve":
                        # print("add+1 e")
                        selectedPoints += 1
                if i+2 == len(c.points):
                    if not c.points[1].selected and c.points[1].type == "curve":
                        # print("add+1 f")
                        selectedPoints += 1
                if i+1 == len(c.points):
                    if not c.points[2].selected and c.points[2].type == "curve":
                        # print("add+1 g")
                        selectedPoints += 1

                # print("add+1 h")
                selectedPoints += 1
                lastSelected = p

    return selectedPoints
