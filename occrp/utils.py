from datetime import datetime

from datetime_distance import DateTimeComparator

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
    for slot in datefield.__slots__:
        if getattr(datefield, slot):
            guts[slot] = getattr(datefield, slot)
    
    if accuracy >= 3:
        guts['day'] = 1
    if accuracy == 4:
        guts['month'] = 1
    
    datefield = datetime(**guts)

    return datefield, accuracy
