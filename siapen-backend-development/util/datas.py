from workalendar.america import Brazil
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


def get_proximo_dia_util(data, dia):
    cal = Brazil() 
    cal.holidays(data.year)
    return cal.add_working_days(data, dia) 

def sum_years_date(date, time):
    return date + relativedelta(years=time)

def cast_datetime_date(date):
    return date.date()
