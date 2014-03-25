# coding: utf-8

import sys
from PyQt4 import QtGui
from qjuliancalendarwidget import QJulianCalendarWidget

class CalendarWidget(QJulianCalendarWidget):
    def __init__(self, parent=None):
         QJulianCalendarWidget.__init__(self, parent)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    gui = CalendarWidget()
    gui.show()
    sys.exit(app.exec_())
