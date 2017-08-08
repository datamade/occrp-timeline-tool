from datetime import datetime

from datetime_distance import DateTimeComparator

from .database import db

def parseDateAccuracy(datefield):
    datefield = DateTimeComparator().parse_resolution(datefield, dayfirst=True)[0]
    
    accuracy = 4

    if datefield.month and datefield.day and datefield.hour:
        accuracy = 1
    elif datefield.month and datefield.day:
        accuracy = 2
    elif datefield.month:
        accuracy = 3
    
    guts = {}
    date_parts = [
        'year',
        'month',
        'day',
        'hour',
        'minute',
        'second'
    ]
    for part in date_parts:
        if getattr(datefield, part):
            guts[part] = getattr(datefield, part)
    
    if accuracy >= 3:
        guts['day'] = 1
    if accuracy == 4:
        guts['month'] = 1
    
    datefield = datetime(**guts)

    return datefield, accuracy


def get_or_create(model, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return (instance, False)
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return (instance, True)