import datetime

#context processors
def date_today():
    return dict(date_today=datetime.date.today())

#filters
def date_filter(dt):
    """returns date from datetime"""
    return dt.date()

def time_filter(dt):
    """returns time from datetime"""
    return dt.time()