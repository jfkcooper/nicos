from nicos.guisupport.qt import QGraphicsItem, QGraphicsItemGroup, QGraphicsEllipseItem, QGraphicsRectItem

class InteractiveEllipse(QGraphicsEllipseItem):

    def __init__(self, groupname, *args, **opts):
        QGraphicsEllipseItem.__init__(self, *args, **opts)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self._name = groupname

    def mousePressEvent(self, event):
        self.scene().parent().childSelected(self._name, self)
        QGraphicsEllipseItem.mousePressEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        self.scene().parent().childActivated(self._name, self)
        QGraphicsEllipseItem.mouseDoubleClickEvent(self, event)



class InteractiveGroup(QGraphicsItemGroup):

    def __init__(self, groupname, *args, **opts):
        QGraphicsItemGroup.__init__(self, *args, **opts)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self._name = groupname

    def mousePressEvent(self, event):
        self.scene().parent().childSelected(self._name, self)
        QGraphicsItemGroup.mousePressEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        self.scene().parent().childActivated(self._name, self)
        QGraphicsItemGroup.mouseDoubleClickEvent(self, event)


class TransmittingGroup(QGraphicsItemGroup):

    def __init__(self, *args, **opts):
        QGraphicsRectItem.__init__(self, *args, **opts)
        self._name = 'transmitter'

    def mousePressEvent(self, event):
        for child in self.childItems():
            if type(child) is InteractiveGroup and child.isUnderMouse():
                return child.mousePressEvent(event)
        return QGraphicsItemGroup.mousePressEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        for child in self.childItems():
            if type(child) is InteractiveGroup and child.isUnderMouse():
                return child.mouseDoubleClickEvent(event)
        return QGraphicsItemGroup.mouseDoubleClickEvent(self, event)
