#!/usr/bin/env python
# coding: utf-8

"""
The module Holydate-Gui represent
GUI interface for Holydate -- oldbeliever
ancient orthodox calendar.

:copyright: 2014 by Maxim Chernyatevich.
:license: GPLv3, see LICENSE for more details.

"""

import os
import sys
import calendar
from PyQt4 import QtCore, QtGui
from qjuliancalendarwidget import QJulianCalendarWidget
from holydate import AncientCalendar
from holydate import menology, holydate_func, search_saints
import qdarkstyle

sys.setrecursionlimit(18)  # Dirty hack. Fixme in future.

DIR = os.getcwd()
LOGO = os.path.join(DIR, 'images/holydate-logo.png')
LOGO_SVG = os.path.join(DIR, 'images/holydate-logo.svg')
RED = '#fe0100'
GREY = '#666666'
BLACK = 'black'
WHITE = '#F5F5F5'


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.setWindowTitle(QtCore.QString(u'Древлеправославный календарь 0.1a1'))
        self.setWindowIcon(QtGui.QIcon(LOGO_SVG))
        #windowWidh = 900
        #windowHeight = 600
        #print screen.height(), screen.width()

        self.setMinimumSize(900, 600)
        self.Widget = MainWidget(self)
        self.setCentralWidget(self.Widget)

        self.createActions()
        self.createMenus()
        self.setStyleSheet(qdarkstyle.load_stylesheet(pyside=False))

        self.statusBar()

    def about(self):
        self.aboutDialog = AboutDialog()
        self.aboutDialog.show()

    def aboutQt(self):
        pass

    def createActions(self):
        self.exitAct = QtGui.QAction(u"В&ыход", self, shortcut="Ctrl+Q",
                                     statusTip=u"Выход из календаря", triggered=self.close)
        self.aboutAct = QtGui.QAction(u"&О программе", self,
                                      statusTip=u"о программе Древлеправославный календарь",
                                      triggered=self.about)
        self.aboutAct.triggered.connect(AboutDialog)
        self.aboutQtAct = QtGui.QAction(u"О &Qt", self,
                                        statusTip=u"О библиотеке Qt",
                                        triggered=self.aboutQt)
        self.aboutQtAct.triggered.connect(QtGui.qApp.aboutQt)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu(u"&Файл")
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.helpMenu = self.menuBar().addMenu(u"&Справка")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)


class MainWidget(QtGui.QWidget):
    def __init__(self, parent=MainWindow):
        QtGui.QWidget.__init__(self, parent)

        self.calendar_system = 'gregorian'

        mainHbox = QtGui.QHBoxLayout()
        vboxLeft = QtGui.QVBoxLayout()
        vboxLeft.setContentsMargins(0, 0, 3, 0)
        self.stackedBox = QtGui.QStackedLayout()
        hboxRadioBt = QtGui.QHBoxLayout()
        hboxRadioBt.setContentsMargins(15, 10, 5, 5)
        hboxBottom = QtGui.QHBoxLayout()

        self.stackedBoxEditForm = QtGui.QStackedWidget()
        # Dirty hack. Fix in future.
        self.stackedBoxButton = QtGui.QStackedWidget()
        # Fixme:
        height = self.stackedBoxEditForm.sizeHint().height() + 38.
        self.stackedBoxEditForm.setFixedHeight(height)
        self.stackedBoxButton.setFixedHeight(height)

        vboxRight = QtGui.QVBoxLayout()
        hboxSearch = QtGui.QHBoxLayout()
        hboxSearch.setContentsMargins(0, 5, 0, 0)

        mainHbox.addLayout(vboxLeft)
        mainHbox.addLayout(vboxRight)

        self.setLayout(mainHbox)

        self.gregorianCalendarWidget = GregorianCalendarWidget()
        self.julianCalendarWidget = JulianCalendarWidget()
        # Colorize cells of current date.
        self.setGregorianBrushedCell()
        self.setJulianBrushedCell()

        #Fixme: shorcats on russian do not work.
        self.rbNewStyle = QtGui.QRadioButton(QtCore.QString(u'По но&вому стилю'))
        self.rbNewStyle.setChecked(True)
        self.rbOldStyle = QtGui.QRadioButton(QtCore.QString(u'По ста&рому стилю'))
        self.rbGroup = QtGui.QButtonGroup()
        self.rbGroup.addButton(self.rbNewStyle, 0)
        self.rbGroup.addButton(self.rbOldStyle, 1)

        self.buttonSetToday = QtGui.QPushButton()
        self.buttonSetToday.setText(QtCore.QString(u'&Сегодня'))

        self.gregorianDateEditForm = QtGui.QDateEdit()
        self.gregorianDateEditForm.setDisplayFormat(QtCore.QString('dd MMMM yyyy'))
        self.gregorianDateEditForm.setMinimumDate(QtCore.QDate(1900, 1, 1))
        self.gregorianDateEditForm.setMaximumDate(QtCore.QDate(2099, 12, 31))
        self.gregorianDateEditForm.setDate(QtCore.QDate.currentDate())

        self.julianDateEditForm = QtGui.QDateEdit()
        self.julianDateEditForm.setDisplayFormat(QtCore.QString('dd MMMM yyyy'))
        self.julianDateEditForm.setMinimumDate(QtCore.QDate(1900, 1, 1))
        self.julianDateEditForm.setMaximumDate(QtCore.QDate(2099, 12, 31))
        self.julianDateEditForm.setDate(QtCore.QDate.currentDate())

        self.textWidget = QtGui.QTextBrowser()
        # Embed custom fonts.
        pt_serif_custom = QtGui.QFontDatabase.addApplicationFont(os.path.join(DIR, 'fonts/PTSerif-Custom.ttf'))
        pt_serif_caption = QtGui.QFontDatabase.addApplicationFont(os.path.join(DIR, 'fonts/PTZ55F.ttf'))
        pt_serif_bold = QtGui.QFontDatabase.addApplicationFont(os.path.join(DIR, 'fonts/PTF75F.ttf'))
        self.textWidget.setFont(QtGui.QFont(pt_serif_custom))
        self.textWidget.setFont(QtGui.QFont(pt_serif_caption))
        self.textWidget.setFont(QtGui.QFont(pt_serif_bold))
        self.textWidget.setHtml(self.default_output())
        self.textWidget.setStyleSheet('font-size: 18px;')

        self.searchForm = SearchForm()
        self.searchForm.setFixedHeight(height)
        self.searchForm.setTextMargins(5, 0, 0, 2)
        self.buttonSearch = QtGui.QPushButton(QtCore.QString(u'&Найти'))
        self.buttonSearch.setFixedHeight(height)

        vboxLeft.addLayout(self.stackedBox)
        self.stackedBox.addWidget(self.gregorianCalendarWidget)
        self.stackedBox.addWidget(self.julianCalendarWidget)

        vboxLeft.addLayout(hboxRadioBt)
        hboxRadioBt.addWidget(self.rbNewStyle)
        hboxRadioBt.addWidget(self.rbOldStyle)
        vboxLeft.addLayout(hboxBottom)
        hboxBottom.addWidget(self.buttonSetToday)

        hboxBottom.addWidget(self.stackedBoxButton)
        hboxBottom.addWidget(self.stackedBoxEditForm)

        self.stackedBoxButton.addWidget(self.buttonSetToday)
        self.stackedBoxEditForm.addWidget(self.gregorianDateEditForm)
        self.stackedBoxEditForm.addWidget(self.julianDateEditForm)

        hboxSearch.addWidget(self.searchForm)
        hboxSearch.addWidget(self.buttonSearch)  # Dirty hack. Fixme in future.
        vboxRight.addWidget(self.textWidget)
        vboxRight.addLayout(hboxSearch)

        #Change date between widgets.
        self.gregorianCalendarWidget.selectionChanged.connect(self.setSelectedDateJulian)
        self.julianCalendarWidget.selectionChanged.connect(self.setSelectedDateGregorian)
        #Change current page between widget.  #  Fixme: this slots called undesirable recursion.
        self.gregorianCalendarWidget.currentPageChanged.connect(self.changeJulianCurrentPage)
        self.julianCalendarWidget.currentPageChanged.connect(self.changeGregorianCurrentPage)
        #Radio button of old and new style date.
        self.rbOldStyle.clicked.connect(self.setJulianCalendar)
        self.rbNewStyle.clicked.connect(self.setGregorianCalendar)
        #Button today.
        self.buttonSetToday.clicked.connect(self.setDateToday)
        #Date edit form.
        self.gregorianDateEditForm.dateChanged.connect(self.setGregorianCalendarDate)
        self.julianDateEditForm.dateChanged.connect(self.setJulianCalendarDate)
        self.gregorianCalendarWidget.clicked.connect(self.setGregorianDateEditForm)
        self.julianCalendarWidget.clicked.connect(self.setJulianDateEditForm)
        #Calendar signal.
        self.gregorianCalendarWidget.currentPageChanged.connect(self.setGregorianBrushedCell)
        self.julianCalendarWidget.currentPageChanged.connect(self.setJulianBrushedCell)
        self.gregorianCalendarWidget.selectionChanged.connect(self.output)
        self.julianCalendarWidget.selectionChanged.connect(self.output)
        #Search form.
        self.buttonSearch.clicked.connect(self.searchFormEnter)
        self.searchForm.returnPressed.connect(self.searchFormEnter)
        self.searchForm.button.clicked.connect(self.clearSearchForm)

    def setGregorianCalendar(self):
        self.calendar_system = 'gregorian'
        self.stackedBox.setCurrentWidget(self.gregorianCalendarWidget)
        self.stackedBoxEditForm.setCurrentWidget(self.gregorianDateEditForm)
        self.gregorianDateEditForm.setDate(self.gregorianCalendarWidget.selectedDate())

    def setJulianCalendar(self):
        self.calendar_system = 'julian'
        self.stackedBox.setCurrentWidget(self.julianCalendarWidget)
        self.stackedBoxEditForm.setCurrentWidget(self.julianDateEditForm)
        self.julianDateEditForm.setDate(self.julianCalendarWidget.selectedDate())

    def changeJulianCurrentPage(self):
        year = self.gregorianCalendarWidget.yearShown()
        month = self.gregorianCalendarWidget.monthShown()
        self.julianCalendarWidget.setCurrentPage(year, month)

    def changeGregorianCurrentPage(self):
        year = self.julianCalendarWidget.yearShown()
        month = self.julianCalendarWidget.monthShown()
        self.gregorianCalendarWidget.setCurrentPage(year, month)

    def setSelectedDateJulian(self):
        date_new = self.gregorianCalendarWidget.selectedDate()
        date_jd = date_new.toJulianDay()
        date_ju = holydate_func.jd_to_ju(date_jd)
        day, month, year = date_ju
        string = '{year} {month} {day}'.format(year=year, month=month, day=day)
        date_old = QtCore.QDate.fromString(string, "yyyy M d")
        self.julianCalendarWidget.setSelectedDate(date_old)

    def setSelectedDateGregorian(self):
        date = self.julianCalendarWidget.selectedDate()
        date_jd = date.toJulianDay()
        date_gr = holydate_func.jd_to_gr(date_jd + 13)
        day, month, year = date_gr
        string = '{year} {month} {day}'.format(year=year, month=month, day=day)
        date_new = QtCore.QDate.fromString(string, "yyyy M d")
        self.gregorianCalendarWidget.setSelectedDate(date_new)

    def setDateToday(self):
        """Set today from button."""

        if self.calendar_system == 'gregorian':
            self.gregorianCalendarWidget.setSelectedDate(QtCore.QDate.currentDate())
            self.gregorianDateEditForm.setDate(QtCore.QDate.currentDate())
        elif self.calendar_system == 'julian':
            date_new = QtCore.QDate.currentDate()
            date_jd = date_new.toJulianDay()
            date_ju = holydate_func.jd_to_ju(date_jd)
            day, month, year = date_ju
            string = '{year} {month} {day}'.format(year=year, month=month, day=day)
            date_old = QtCore.QDate.fromString(string, "yyyy M d")
            self.julianCalendarWidget.setSelectedDate(date_old)
            self.julianCalendarWidget.setFocus()
            self.julianDateEditForm.setDate(date_old)

    def setGregorianCalendarDate(self, date):
        self.gregorianCalendarWidget.setSelectedDate(date)

    def setJulianCalendarDate(self, date):
        self.julianCalendarWidget.setSelectedDate(date)

    def setGregorianDateEditForm(self, date):
        self.gregorianDateEditForm.setDate(date)

    def setJulianDateEditForm(self, date):
        self.julianDateEditForm.setDate(date)

    def setGregorianBrushedCell(self):
        """Colorize cells of Gregorian Calendar widget."""

        year = self.gregorianCalendarWidget.yearShown()

        f = QtGui.QTextCharFormat()
        fast_and_feast = {}

        for month in range(1, 13):
            days_in_month = calendar.monthrange(year, month)[1] + 1
            for day in range(1, days_in_month):
                cal = HolydateGui(day, month, year, calendar='gregorian')
                fast_and_feast.setdefault(month, {}).update({day: cal.getFeastAndFastStatus()})

        try:
            for month in range(1, 13):
                days_in_month = calendar.monthrange(year, month)[1] + 1
                for day in range(1, days_in_month):
                    if fast_and_feast[month][day] is 3:
                        f.setForeground(QtGui.QBrush(QtGui.QColor(RED)))
                        f.setBackground(QtGui.QBrush(QtGui.QColor(GREY)))
                    elif fast_and_feast[month][day] is 2:
                        f.setForeground(QtGui.QBrush(QtGui.QColor(WHITE)))
                        f.setBackground(QtGui.QBrush(QtGui.QColor(GREY)))
                    elif fast_and_feast[month][day] is 1:
                        f.setForeground(QtGui.QBrush(QtGui.QColor(RED)))
                        f.setBackground(QtGui.QBrush(QtGui.QColor(WHITE)))
                    elif fast_and_feast[month][day] is 0:
                        f.setForeground(QtGui.QBrush(QtGui.QColor(BLACK)))
                        f.setBackground(QtGui.QBrush(QtGui.QColor(WHITE)))
                    self.gregorianCalendarWidget.setDateTextFormat(QtCore.QDate(year, month, day), f)
        except KeyError:
            pass

    def setJulianBrushedCell(self):
        """Colorize cells of Julian Calendar widget."""

        year = self.julianCalendarWidget.yearShown()

        f = QtGui.QTextCharFormat()
        fast_and_feast = {}

        for month in range(1, 13):
            days_in_month = calendar.monthrange(year, month)[1] + 1
            for day in range(1, days_in_month):
                cal = HolydateGui(day, month, year, calendar='julian')
                fast_and_feast.setdefault(month, {}).update({day: cal.getFeastAndFastStatus()})

        try:
            for month in range(1, 13):
                days_in_month = calendar.monthrange(year, month)[1] + 1
                for day in range(1, days_in_month):
                    if fast_and_feast[month][day] is 3:
                        f.setForeground(QtGui.QBrush(QtGui.QColor(RED)))
                        f.setBackground(QtGui.QBrush(QtGui.QColor(GREY)))
                    elif fast_and_feast[month][day] is 2:
                        f.setForeground(QtGui.QBrush(QtGui.QColor(WHITE)))
                        f.setBackground(QtGui.QBrush(QtGui.QColor(GREY)))
                    elif fast_and_feast[month][day] is 1:
                        f.setForeground(QtGui.QBrush(QtGui.QColor(RED)))
                        f.setBackground(QtGui.QBrush(QtGui.QColor(WHITE)))
                    elif fast_and_feast[month][day] is 0:
                        f.setForeground(QtGui.QBrush(QtGui.QColor(BLACK)))
                        f.setBackground(QtGui.QBrush(QtGui.QColor(WHITE)))
                    self.julianCalendarWidget.setDateTextFormat(QtCore.QDate(year, month, day), f)
        except KeyError:
            pass

    def calendar_constructor(self, day, month, year):
        calendar = AncientCalendar(day, month, year, calendar=self.calendar_system)
        gr_date = calendar.getGrigorianDate(verbose='on')
        ju_date = calendar.getJulianDate(verbose='on')
        weekday = calendar.getWeekday(verbose='on')
        tone = calendar.getTone()
        weekdayname = calendar.getWeekdayname().format(red="<span class='red'>",
                                                       bold="<span class='bold'>",
                                                       end='</span>',
                                                       tw="<span class='twelve'>ӱ</span>",
                                                       pl="<span class='polyeleos'>Ӱ</span>",
                                                       gl="<span class='glorium'>Ӵ</span>",
                                                       sx="<span class='six'>Ӵ</span>",
                                                       redgui='')

        saints = calendar.getSaint().format(red="<span class='red'>",
                                            bold="<span class='bold'>",
                                            end="</span>",
                                            tw="<span class='twelve'>ӱ</span>",
                                            pl="<span class='polyeleos'>Ӱ</span>",
                                            gl="<span class='glorium'>Ӵ</span>",
                                            sx="<span class='six'>Ӵ</span>")
        fast = calendar.getFast()
        bows = calendar.getBow()

        css = os.path.join(DIR, 'css/calendar.css')

        out = """
              <html>
                  <head>
                     <link rel="stylesheet" media="all" type="text/css" href="{css}" />
                  </head>
                <body>
                  <div>
                    <p>
                      {gr_date}<br>
                      {ju_date}
                    </p>
                  </div>
                  <div>
                    <p>
                      {weekday}<br>
                      {tone}
                    </p>
                  </div>
                  <div>
                    <p class='weekdayname'>{weekdayname}</p>
                  </div>
                  <div>
                    <p>{saints}</p>
                  </div>
                  <div>
                    <p>
                      {fast}<br>
                      {bows}
                    </p>
                  </div>
                </body>
              </html>
              """

        out = out.format(css=css,
                         gr_date=gr_date,
                         ju_date=ju_date,
                         weekdayname=weekdayname,
                         weekday=weekday,
                         tone=tone,
                         saints=saints,
                         fast=fast,
                         bows=bows)

        return QtCore.QString(out.decode('utf8'))

    def output(self):
        if self.calendar_system == 'gregorian':
            _gr_day = int(self.gregorianCalendarWidget.selectedDate().day())
            _gr_month = int(self.gregorianCalendarWidget.selectedDate().month())
            _gr_year = int(self.gregorianCalendarWidget.selectedDate().year())
            _calendar = self.calendar_constructor(_gr_day, _gr_month, _gr_year)
            return self.textWidget.setHtml(_calendar)
        elif self.calendar_system == 'julian':
            _ju_day = int(self.julianCalendarWidget.selectedDate().day())
            _ju_month = int(self.julianCalendarWidget.selectedDate().month())
            _ju_year = int(self.julianCalendarWidget.selectedDate().year())
            _calendar = self.calendar_constructor(_ju_day, _ju_month, _ju_year)
            return self.textWidget.setHtml(_calendar)

    def default_output(self):
        date = QtCore.QDate.currentDate()
        day = int(date.day())
        month = int(date.month())
        year = int(date.year())
        calendar = self.calendar_constructor(day, month, year)
        return calendar

    def clearSearchForm(self):
        self.searchForm.clear()

    def searchFormEnter(self):
        text = self.searchForm.text()
        text = str(text.toUtf8())
        result = search_saints.search_saints(text, mode='html')
        css = os.path.join(DIR, u'css/calendar.css')

        result = QtCore.QString(result.format(red=u"<span class='red'>",
                                              bold=u"<span class='bold'>",
                                              end=u'</span>',
                                              tw=u"<span class='twelve'>ӱ</span>",
                                              pl=u"<span class='polyeleos'>Ӱ</span>",
                                              gl=u"<span class='glorium'>Ӵ</span>",
                                              sx=u"<span class='six'>Ӵ</span>",
                                              redgui=u''))



        out = u"""
              <html>
                  <head>
                     <link rel="stylesheet" media="all" type="text/css" href='{css}' />
                  </head>
                <body>
                  {result}
                </body>
              </html>
              """

        out = out.format(result=result, css=css)
        self.textWidget.setText(QtCore.QString(out))

class GregorianCalendarWidget(QtGui.QCalendarWidget):
    def __init__(self, parent=None):
        QtGui.QCalendarWidget.__init__(self, parent)
        self.setMinimumDate(QtCore.QDate(1900, 1, 1))
        self.setMaximumDate(QtCore.QDate(2099, 12, 31))
        self.setGridVisible(False)
        self.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.setVerticalHeaderFormat(0)


class JulianCalendarWidget(QJulianCalendarWidget):
    def __init__(self, parent=None):
        QtGui.QCalendarWidget.__init__(self, parent)
        self.setMinimumDate(QtCore.QDate(1900, 1, 1))
        self.setMaximumDate(QtCore.QDate(2099, 12, 31))
        self.setGridVisible(False)
        self.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.setVerticalHeaderFormat(0)


class SearchForm(QtGui.QLineEdit):
    def __init__(self):
        QtGui.QLineEdit.__init__(self)

        self.button = QtGui.QToolButton(self)
        self.button.setIcon(QtGui.QIcon(os.path.join(DIR, 'images/close.png')))
        self.button.setStyleSheet('border: 0px; padding: 0px;')
        self.button.setCursor(QtCore.Qt.ArrowCursor)

        frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        buttonSize = self.button.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' % (buttonSize.width() + frameWidth + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(), buttonSize.width() + frameWidth*2 + 2),
                            max(self.minimumSizeHint().height(), buttonSize.height() + frameWidth*2 + 2))

    def resizeEvent(self, event):
        buttonSize = self.button.sizeHint()
        frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        self.button.move(self.rect().right() - frameWidth - buttonSize.width(),
                         (self.rect().bottom() - buttonSize.height() + 1)/2)
        super(SearchForm, self).resizeEvent(event)


class HolydateGui(AncientCalendar):
    def getFeastAndFastStatus(self):
        """Get daily feast and fest status for gui-calendar."""

        saint = menology.menology[self.month][self.day]['saint']
        string = self.getWeekdayname()
        self.getFast()
        weekday = self.getWeekday(verbose='off')

        gl = '{gl}'
        pl = '{pl}'
        tw = '{tw}'
        redgui = '{redgui}'

        #Sunday.
        if weekday in [0] and self.fast in [6, 7, 8, 9, 10, 11, 12, 13]:
            index = 1  # Feast.
        elif weekday in [0] and self.fast in [0, 1, 2, 3, 4, 5, 14]:
            index = 3  # Feast and fast.
        #Feast.
        elif gl in string and self.fast in [6, 7, 8, 9, 10, 11, 12, 13]:
            index = 1
        elif pl in string and self.fast in [6, 7, 8, 9, 10, 11, 12, 13]:
            index = 1
        elif tw in string and self.fast in [6, 7, 8, 9, 10, 11, 12, 13]:
            index = 1
        elif saint in [2, 3, 4, 5, 6, 7] and self.fast in [6, 7, 8, 9, 10, 11, 12, 13]:
            index = 1
        #Feast and fast.
        elif gl in string and self.fast in [0, 1, 2, 3, 4, 5, 14]:
            index = 3
        elif pl in string and self.fast in [0, 1, 2, 3, 4, 5, 14]:
            index = 3
        elif tw in string and self.fast in [0, 1, 2, 3, 4, 5, 14]:
            index = 3
        elif saint in [2, 3, 4, 5, 6, 7] and self.fast in [0, 1, 2, 3, 4, 5, 14]:
            index = 3
        #Fast.
        elif saint in [0, 1] and self.fast in [0, 1, 2, 3, 4, 5, 14]:
            index = 2
        #Easter.
        elif redgui in string:
            index = 1  # Feast.
        else:
            index = 0  # Ordinary day.
        return index


class AboutDialog(QtGui.QMessageBox):
    def __init__(self):
        QtGui.QMessageBox.__init__(self)

        self.setStyleSheet(qdarkstyle.load_stylesheet(pyside=False))

        text = u"""
            <h3>holydate-gui</h3>
            <h4>Версия 0.1а1</h4>
            <p><a href='http://www.vechnoe.info/holydate'>http://www.vechnoe.info/holydate</a></p>

            <p><b>Древлеправославный старообрядческий календарь.</b>
            Содержит дни недели, гласы, посты, праздники,
            приходные и исxодные поклоны на каждый день всего года.
            В основу календаря положен старообрядческий Часослов,
            добавлены святые из календаря РПСЦ.</p>

            <p><b>holydate-gui</b> — GUI интерфейс к python-билиотеке <b>holydate:</b>
            <a href='https://pypi.python.org/pypi/holydate'>https://pypi.python.org/pypi/holydate</a>

            <h4>Лицензия</h4>
            <p>Copyright &copy; 2014 Максим Чернятевич.</p>
            <p><b>holydate-gui</b> распространяется на условиях лицензии GNU GPLv3.
            <a href='https://www.gnu.org/copyleft/gpl.html'>https://www.gnu.org/copyleft/gpl.html</a>
            </p>

            <h4>Сообщения об ошибках и пожелания отправляйте на почту:</h4>
            <p><a href='mailto:vechnoe.info@gmail.com'>vechnoe.info@gmail.com</a></p>
            """

        self.setWindowIcon(QtGui.QIcon(LOGO_SVG))
        self.setIconPixmap(QtGui.QPixmap(LOGO))
        self.setWindowTitle(QtCore.QString(u'О программе holydate-gui'))
        self.setText(QtCore.QString(text))


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(app.exec_())
