%Module qjuliancalendarwidget 1
%Import QtCore/QtCoremod.sip  
%Import QtGui/QtGuimod.sip


class QJulianCalendarWidget : public QWidget {

%TypeHeaderCode
#include "qjuliancalendarwidget.h" 
%End

public:
    QJulianCalendarWidget(QWidget *parent /TransferThis/ = 0); 

    enum VerticalHeaderFormat {
        NoVerticalHeader,
        ISOWeekNumbers
    };
    
    enum HorizontalHeaderFormat {
        NoHorizontalHeader,
        SingleLetterDayNames,
        ShortDayNames,
        LongDayNames
    };

    QDate selectedDate() const;

    int yearShown() const;
    int monthShown() const;
 
    QDate minimumDate() const;
    void setMinimumDate(const QDate &date);
 
    QDate maximumDate() const;
    void setMaximumDate(const QDate &date);
    
    Qt::DayOfWeek firstDayOfWeek() const;
    void setFirstDayOfWeek(Qt::DayOfWeek dayOfWeek);
    
    QTextCharFormat headerTextFormat() const;
    void setHeaderTextFormat(const QTextCharFormat &format);
 
    QTextCharFormat weekdayTextFormat(Qt::DayOfWeek dayOfWeek) const;
    void setWeekdayTextFormat(Qt::DayOfWeek dayOfWeek, const QTextCharFormat &format);
 
    QMap<QDate, QTextCharFormat> dateTextFormat() const;
    QTextCharFormat dateTextFormat(const QDate &date) const;
    void setDateTextFormat(const QDate &date, const QTextCharFormat &format);
 
    VerticalHeaderFormat verticalHeaderFormat() const;
    void setVerticalHeaderFormat(VerticalHeaderFormat NoVerticalHeader);
     
    HorizontalHeaderFormat horizontalHeaderFormat() const;
    void setHorizontalHeaderFormat(HorizontalHeaderFormat format);
};


