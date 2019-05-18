from AppKit import NSColor, NSGraphicsContext, NSForegroundColorAttributeName, NSAttributedString, NSFont, \
    NSFontAttributeName, NSAffineTransform, NSRectFill, NSRectFillListUsingOperation, NSImage, NSParagraphStyleAttributeName, \
    NSBezierPath, NSMutableParagraphStyle, NSCenterTextAlignment, NSLineBreakByTruncatingMiddle, NSCompositeSourceOver

if __name__ != "__main__":
    from masterTools.UI.settings import Settings
    uiSettings = Settings().getDict()

GlyphCellHeaderHeight = 14
GlyphCellMinHeightForHeader = 40


cellBackgroundColor = NSColor.clearColor()
cellHeaderBaseColor = NSColor.colorWithCalibratedWhite_alpha_(0.968, 1.0)
cellHeaderHighlightColor = NSColor.colorWithCalibratedWhite_alpha_(0.98, 1.0)
cellHeaderLineColor = NSColor.colorWithCalibratedWhite_alpha_(0, .2)
cellMetricsLineColor = NSColor.colorWithCalibratedWhite_alpha_(0, .08)
cellMetricsFillColor = NSColor.colorWithCalibratedWhite_alpha_(0, .08)


def GlyphCellFactory(glyph, width, height, glyphColor, bufferPercent=.2, drawHeader=False, drawMetrics=False):
    obj = GlyphCellFactoryDrawingController(glyph=glyph, font=glyph.font, width=width, height=height,glyphColor=glyphColor,bufferPercent=bufferPercent, drawHeader=drawHeader, drawMetrics=drawMetrics)
    return obj.getImage()


class GlyphCellFactoryDrawingController(object):

    """
    This draws the cell with the layers stacked in this order:
    ------------------
    header text
    ------------------
    header background
    ------------------
    foreground
    ------------------
    glyph
    ------------------
    vertical metrics
    ------------------
    horizontal metrics
    ------------------
    background
    ------------------
    Subclasses may override the layer drawing methods to customize
    the appearance of cells.
    """


    def __init__(self, glyph, font, width, height, bufferPercent, glyphColor, drawHeader=False, drawMetrics=False):
        self.glyph = glyph
        self.glyphColor = glyphColor
        self.font = font
        self.width = width
        self.height = height
        self.bufferPercent = bufferPercent
        self.shouldDrawHeader = drawHeader
        self.shouldDrawMetrics = drawMetrics

        self.headerHeight = 0
        if drawHeader:
            self.headerHeight = GlyphCellHeaderHeight
        availableHeight = (height - self.headerHeight) * (1.0 - (self.bufferPercent * 2))
        self.buffer = height * self.bufferPercent
        self.scale = availableHeight / font.info.unitsPerEm
        self.xOffset = (width - (glyph.width * self.scale)) / 2
        self.yOffset = abs(font.info.descender * self.scale) + self.buffer

    def getImage(self):
        image = NSImage.alloc().initWithSize_((self.width, self.height))
        image.setFlipped_(False)
        image.lockFocus()
        context = NSGraphicsContext.currentContext()
        bodyRect = ((0, 0), (self.width, self.height - self.headerHeight))
        headerRect = ((0, -self.height + self.headerHeight), (self.width, self.headerHeight))
        # draw a background color
        cellBackgroundColor.set()
        NSRectFill(((0, 0), (self.width, self.height)))
        # background
        context.saveGraphicsState()
        bodyTransform = NSAffineTransform.transform()
        bodyTransform.translateXBy_yBy_(0, self.height - self.headerHeight)
        bodyTransform.scaleXBy_yBy_(1.0, -1.0)
        bodyTransform.concat()
        self.drawCellBackground(bodyRect)
        context.restoreGraphicsState()
        # glyph
        if self.shouldDrawMetrics:
            self.drawCellHorizontalMetrics(bodyRect)
            self.drawCellVerticalMetrics(bodyRect)
        context.saveGraphicsState()
        NSBezierPath.clipRect_(((0, 0), (self.width, self.height - self.headerHeight)))
        glyphTransform = NSAffineTransform.transform()
        glyphTransform.translateXBy_yBy_(self.xOffset, self.yOffset)
        glyphTransform.scaleBy_(self.scale)
        glyphTransform.concat()
        self.drawCellGlyph()
        context.restoreGraphicsState()
        # foreground
        context.saveGraphicsState()
        bodyTransform.concat()
        self.drawCellForeground(bodyRect)
        context.restoreGraphicsState()
        # header
        if self.shouldDrawHeader:
            context.saveGraphicsState()
            headerTransform = NSAffineTransform.transform()
            headerTransform.translateXBy_yBy_(0, self.headerHeight)
            headerTransform.scaleXBy_yBy_(1.0, -1.0)
            headerTransform.concat()
            self.drawCellHeaderBackground(headerRect)
            self.drawCellHeaderText(headerRect)
            context.restoreGraphicsState()
        # done
        image.unlockFocus()
        return image

    def drawCellBackground(self, rect):
        pass

    def drawCellHorizontalMetrics(self, rect):
        (xMin, yMin), (width, height) = rect
        font = self.font
        scale = self.scale
        yOffset = self.yOffset
        path = NSBezierPath.bezierPath()
        lines = set((0, font.info.descender, font.info.xHeight, font.info.capHeight, font.info.ascender))
        for y in lines:
            y = round((y * scale) + yMin + yOffset) - .5
            path.moveToPoint_((xMin, y))
            path.lineToPoint_((xMin + width, y))
        cellMetricsLineColor.set()
        path.setLineWidth_(1.0)
        path.stroke()

    def drawCellVerticalMetrics(self, rect):
        (xMin, yMin), (width, height) = rect
        glyph = self.glyph
        scale = self.scale
        xOffset = self.xOffset
        left = round((0 * scale) + xMin + xOffset) - .5
        right = round((glyph.width * scale) + xMin + xOffset) - .5
        rects = [
            ((xMin, yMin), (left - xMin, height)),
            ((xMin + right, yMin), (width - xMin + right, height))
        ]
        cellMetricsFillColor.set()
        NSRectFillListUsingOperation(rects, len(rects), NSCompositeSourceOver)

    def drawCellGlyph(self):
        self.glyphColor.set()
        path = self.glyph.getRepresentation("defconAppKit.NSBezierPath")
        path.fill()

    # def drawCellGlyph(self):
    #     layers = self.font.layers
    #     if isinstance(layers,tuple):
    #         layerOrder = layers
    #     else:
    #         layerOrder = layers.layerOrder
    #     for layerName in reversed(layerOrder):
    #         if isinstance(layers,tuple):
    #             layer = layerName
    #         else:
    #             layer = layers[layerName]
    #         if self.glyph.name not in layer:
    #             continue
    #         layerColor = None
    #         if layer.color is not None:
    #             layerColor = colorToNSColor(layer.color)
    #         if layerColor is None:
    #             layerColor = glyphColor
    #         glyph = layer[self.glyph.name]
    #         path = glyph.getRepresentation("defconAppKit.NSBezierPath")
    #         layerColor.set()
    #         path.fill()

    def drawCellForeground(self, rect):
        pass

    def drawCellHeaderBackground(self, rect):
        (xMin, yMin), (width, height) = rect
        # background
        try:
            gradient = NSGradient.alloc().initWithColors_([cellHeaderHighlightColor, cellHeaderBaseColor])
            gradient.drawInRect_angle_(rect, 90)
        except NameError:
            cellHeaderBaseColor.set()
            NSRectFill(rect)
        # bottom line
        cellHeaderLineColor.set()
        bottomPath = NSBezierPath.bezierPath()
        bottomPath.moveToPoint_((xMin, yMin + height - .5))
        bottomPath.lineToPoint_((xMin + width, yMin + height - .5))
        bottomPath.setLineWidth_(1.0)
        bottomPath.stroke()

    def drawCellHeaderText(self, rect):
        paragraph = NSMutableParagraphStyle.alloc().init()
        paragraph.setAlignment_(NSCenterTextAlignment)
        paragraph.setLineBreakMode_(NSLineBreakByTruncatingMiddle)
        attributes = {
            NSFontAttributeName: NSFont.systemFontOfSize_(10.0),
            NSForegroundColorAttributeName: NSColor.colorWithCalibratedRed_green_blue_alpha_(.22, .22, .27, 1.0),
            NSParagraphStyleAttributeName: paragraph,
        }
        text = NSAttributedString.alloc().initWithString_attributes_(self.glyph.name, attributes)
        text.drawInRect_(rect)
if __name__=="__main__":

    from vanilla import *


    class ListDemo(object):
        def __init__(self):
            path = '/Users/rafalbuchner/Dropbox/tests/Book-Rafal-03.ufo'
            # path = '/Users/rafalbuchner/Documents/repos/work/+GAMER/gamer/+working_files/regular/G-Re-Medium-02.ufo'
            font = OpenFont(path, False)
            fontListColumnDescriptions = [
                dict(title="glyph",cell=ImageListCell(), width=220)
                ]
            items = [dict(glyph=GlyphCellFactory(g, 240, 240, glyphColor=NSColor.blackColor()))for g in font]
            self.w = HUDFloatingWindow((400, 700))
            self.w.list = List(
                            (0,0,-0,-0),
                            items,# test
                            rowHeight=250,
                            columnDescriptions=fontListColumnDescriptions)
            self.w.open()
    ListDemo()
