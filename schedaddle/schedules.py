from datetime import datetime, date, timedelta

# Constants
KNOWN_INTERVALS ={
    'hourly':       ( 0,  0,  0,  1,  0,  0,  0),
    'daily':        ( 0,  0,  1,  0,  0,  0,  0),
    'weekly':       ( 0,  0,  7,  0,  0,  0,  0),
    'biweekly':     ( 0,  0, 14,  0,  0,  0,  0),
    'monthly':      ( 0,  1,  0,  0,  0,  0,  0),
    'bimonthly':    ( 0,  2,  0,  0,  0,  0,  0),
    'quarterly':    ( 0,  3,  0,  0,  0,  0,  0),
    'semiannually': ( 0,  6,  0,  0,  0,  0,  0),
    'annually':     ( 1,  0,  0,  0,  0,  0,  0),
    'biannually':   ( 2,  0,  0,  0,  0,  0,  0)
}
__DEFAULT_DATE_BEGINNING = (0, 1, 1, 0, 0, 0, 0)
__DEFAULT_DATE_END       = (0, 1, 1, 23, 59, 59, 999999)

def next(start_date, interval, latest=None):
    """
    Get the next date/time tuple on a schedule.

    Keyword arguments:
       start_date -- the date that the schedule began/begins
       
       interval -- can be a string or a tuple.
          If a string - valid values are defined in KNOWN_INTERVALS
          
          If a tuple - (year, month, day, hour, minute, second, microsecond)

       latest -- the most recent date that the schedule ran (optional, if not
       provided, start_date will be treated as the latest)

    Returns a 7 value tuple (year, month, day, hour, minute, second, microsecond)

    Example:

       >>> import schedaddle
       >>> schedaddle.next((2010, 1, 31), 'monthly')
       (2010, 2, 28, 0, 0, 0, 0)
   
       >>> import schedaddle
       >>> schedaddle.next((2010, 1, 31), 'monthly', latest=(2010, 3, 15))
       (2010, 3, 31, 0, 0, 0, 0)

    """
    start_date = __to_datetime_tuple(start_date)

    if latest:
        latest = __to_datetime_tuple(latest, True)
        if latest < start_date:
            return start_date

    years, months, days, hours, minutes, seconds, microseconds = \
         __interval_values(interval)
    
    multiplier = __next_multiplier(
        start_date, years, months, days, hours, minutes, seconds, microseconds,
        latest)

    return __apply_interval(start_date, years, months, days, hours, minutes,
                            seconds, microseconds, multiplier)

def next_m(schedules, latest=None):
    """
    Get the next identifiable date/time tuple resulting from an iterable of
    schedules.

    Keyword arguments:
       schedules -- an iterable of schedules
          a single schedule is a three value tuple consisting of (identifier,
          start_date, interval)

       latest -- the most recent date that the schedule ran (optional, if not
       provided, start_date will be treated as the latest for each schedule)

    Returns a two value tuple consisting of the identifier of the matching schedule,
    and the 7 value date/time tuple.
    (identifier, (year, month, day, hour, minute, second, microsecond))

    Example:

       >>> import schedaddle
       >>> schedaddle.next_m([
       ... ('first', (2010, 1, 31), 'monthly'),
       ... ('second', (2010, 1, 31), 'weekly')])
       ('second', (2010, 2, 7, 0, 0, 0, 0))

       >>> import schedaddle
       >>> schedaddle.next_m([
       ... ('first', (2010, 1, 31), (0, 1, 0, 0, 0, 0, 0)),
       ... ('second', (2010, 1, 31, 12, 30), 'weekly')],
       ... latest=(2010, 2, 21))
       ('first', (2010, 2, 28, 0, 0, 0, 0))

    """
    recent_schedule = None
    for schedule in schedules:
        test_schedule = (schedule[0], next(schedule[1], schedule[2], latest),)
        if recent_schedule is None or test_schedule[1] < recent_schedule[1]:
            recent_schedule = test_schedule
    return recent_schedule

def upcoming(start_date, interval, latest=None, end_date=None, max_dates=None):
    """
    Get a generator that produces upcoming date/time tuples on a schedule.

    Keyword arguments:
       start_date -- the date that the schedule begain/begins

       interval -- can be a string or a tuple.
          If a string - valid values are defined in KNOWN_INTERVALS 

          If a tuple - (year, month, day, hour, minute, second, microsecond)

       latest -- the most recent date that the schedule ran (optional, 
       if not provided, start_date will be treated as the latest)

       end_date -- the last possible date in the generator (optional)

       max_dates -- the maximum number of dates the generator should
       return (optional)
   
    Returns a generator that yields 7 value date/time tuples
    (year, month, day, hour, minute, second, microsecond)

    Notes:
       If end_date or max_dates is not provided, there will be no end to the amount
       of dates generated, and so it should then not be used in scenarios requiring
       a finite number of results, such as list comprehention.
   
    Example:

       >>> import schedaddle
       >>> g = schedaddle.upcoming((2010, 1, 31, 12, 15), 'weekly', max_dates=3)
       >>> l = [s for s in g]
       >>> l
       [(2010, 2, 7, 12, 15, 0, 0), (2010, 2, 14, 12, 15, 0, 0), (2010, 2, 21, 12, 15, 0, 0)]

    """
    start_date = __to_datetime_tuple(start_date)
    if latest:
        latest = __to_datetime_tuple(latest, True)
    if end_date: end_date = __to_datetime_tuple(end_date, True)

    years, months, days, hours, minutes, seconds, microseconds = \
         __interval_values(interval)
    if latest and latest < start_date:
        multiplier = 0
    else:
        multiplier = __next_multiplier(start_date, years, months, days, hours,
                                       minutes, seconds, microseconds, latest)

    counter = 0
    # while we have not exceeded the maximum number of dates
    while not max_dates or counter <  max_dates:
        nextdt = __apply_interval(start_date, years, months, days, hours,
                                  minutes, seconds, microseconds, multiplier)
        # if we are in date bounds
        if not end_date or nextdt <= end_date:
            yield nextdt
            counter += 1
            multiplier += 1
        else:
            # end_date break condition
            break;

def upcoming_m(schedules, latest=None, end_date=None, max_dates=None):
    """
    Get a generator that produces upcoming, identifiable date/time tuples resulting
    from an iterable of schedules.

    Generate upcoming dates from an iterable of schedules.

    Keyword arguments:
       schedules -- an iterable of schedules
          a single schedule is a tuple consisting of (identifier, start_date,
          interval)

       latest -- the most recent date that the schedule ran (optional, if not
       provided, start_date will be treated as the latest for each schedule)

       end_date -- the last possible date in the generator (optional)

       max_dates -- the maximum number of dates the generator should
       return (optional)

    Returns a generator that yields two value date/time tuples consisting of the
    identifier of the matching schedule and the 7 value date/time tuple.
    (identifier, (year, month, day, hour, minute, second, microsecond))

    Notes:
       If end_date or max_dates is not provided, there will be no end to the amount
       of dates generated, and so it should then not be used in scenarios requiring
       a finite number of results, such as list comprehention.
   
    Example:

       >>> import schedaddle
       >>> schedule1 = ('first',  (2010, 1, 5),  'weekly')
       >>> schedule2 = ('second', (2007, 12, 31), 'monthly')
       >>> g = schedaddle.upcoming_m(
       ... (schedule1, schedule2),
       ... latest=(2010, 1, 12))
       >>> g.next()
       ('first', (2010, 1, 19, 0, 0, 0, 0))
       >>> g.next()
       ('first', (2010, 1, 26, 0, 0, 0, 0))
       >>> g.next()
       ('second', (2010, 1, 31, 0, 0, 0, 0))
    
    """
    if end_date: end_date = __to_datetime_tuple(end_date, True)
    
    generators = [(i[0], upcoming(i[1], i[2], latest)) for i in schedules]

    cg = []
    for g in generators:
        cg.append( [g[1], g[0], g[1].next() ] )
    counter=0
    while not max_dates or counter < max_dates:
        lg = None
        for g in cg:
            if lg is None or g[2] < lg[2]:
                lg = g
        if not end_date or lg[2] <= end_date:
            yield (lg[1], lg[2])
            lg[2] = lg[0].next()
            counter+=1
        else:
            break

def __next_multiplier(start_date, years, months, days, hours, minutes, seconds,
                      microseconds, latest=None):
    """
    Get a multiplier appropriate for obtaining the next datetime after the
    latest (or after start_date if latest is not provided).

    Keyword arguments:
       start_date -- the date that the schedule began/begins

       years -- the number of years to add
       
       months -- the number of months to add
       
       days -- the number of days to add
       
       hours -- the number of hours to add
       
       minutes -- the number of minutes to add
       
       seconds -- the number of seconds to add
       
       microseconds -- the number of microseconds to add
       
       latest -- the most recent datetime or date that the schedule ran (optional 
       if not provided, start_date will be treated as the latest)

    """
    if latest and latest < start_date:
        return 0
    elif not latest or latest == start_date:
        return 1
    else:
        multiplier = 0
        nextd = start_date
        while nextd <= latest:
            multiplier+= 1
            nextd = __apply_interval(start_date, years, months, days, hours,
                                     minutes, seconds, microseconds, multiplier)
        return multiplier

def __to_datetime_tuple(d, eod=False):
    """
    Normalize a date of any usable format into a datetime tuple
    
    Keyword arguments:
       d -- datetime, date, tuple of 0 to 7 values (year, month, day, hour, minute,
       second, microsecond)

       eod -- End Of Day indicator
          If False, fills in undefined time values with zeros
          
          If True, fills undefined time values with highest values available in
          order to reach the maximum point of the day

    """
    if eod: default_date = __DEFAULT_DATE_END
    else: default_date = __DEFAULT_DATE_BEGINNING

    if type(d) == datetime:
            return (d.year, d.month, d.day,
            d.hour, d.minute,d.second, d.microsecond)
    if type(d) == date: return (d.year, d.month, d.day) + default_date[3:]
    else:
        if len(d) >= 7: return tuple(d[:7])
        else: return tuple(d + default_date[len(d):])

def __interval_values(interval):
    """
    Normalize tuple interval values from a known interval term or tuple in
      (years, months, days, hours, minutes, seconds, microseconds) format.

    Keyword arguments:
       interval -- the interval - can either be a string or a tuple.
          If a string - valid values are defined in KNOWN_INTERVALS 

          If a tuple - (year, month, day, hour, minute, second, microsecond)

    """
    if type(interval) == tuple:
        if len(interval) >= 7: return interval[:7]
        else: return interval + (0,0,0,0,0,0,0)[len(interval):]

    try:
        return KNOWN_INTERVALS[interval]
    except KeyError:
        raise Exception('Unknown interval "%s"' % interval)

def __apply_interval(date, years, months, days, hours, minutes, seconds,
                     microseconds, multiplier=1):
    """
    Apply an interval to a date.

    Keyword arguments:
       date -- the original date
       
       years -- the number of years to add
       
       months -- the number of months to add
       
       days -- the number of days to add
       
       hours -- the number of hours to add
       
       minutes -- the number of mintues to add
       
       seconds -- the number of seconds to add
       
       microseconds -- the number of microseconds to add
       
       multiplier -- the number of times to multiply each interval value
       (default=1)

    """
    if multiplier == 0:
        return date

    # set the actual values according to the multipler
    y, m, d, hh, mm, ss, ms = (
        years * multiplier, months * multiplier, days * multiplier,
        hours * multiplier, minutes * multiplier, seconds * multiplier,
        microseconds * multiplier
    )

    try:
        new_date = datetime(*date)
        if ms != 0 or ss != 0 or mm != 0 or hh != 0 or d != 0:
            new_date = new_date + timedelta(days=d,hours=hh,minutes=mm,
                                            seconds=ss,microseconds=ms)
        if m != 0:
            new_date = datetime(*(new_date.year+(new_date.month+m-1)/12,
                                  ((new_date.month+m-1)%12)+1,new_date.day,
                                  new_date.hour, new_date.minute,
                                  new_date.second, new_date.microsecond))
        return (new_date.year + y, new_date.month, new_date.day,
                new_date.hour, new_date.minute, new_date.second,
                new_date.microsecond)
    except ValueError:
        # if there is a ValueError, it is most likely (hopefully) because the
        # date is invalid. specifically, we are hoping that the day of the month
        # exceeds the number of days in the month.  We will fix this by
        # recursively decrementing the date by one day. Since the values already
        # have the current multiplier applied, use a multiplier of 1
        return __apply_interval(date, y, m, d-1, hh, mm, ss, ms, 1)
