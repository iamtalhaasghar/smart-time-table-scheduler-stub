def duplicatesInDay(timeTable):
    'Returns list of all lectures of a day irrespective of class and room'
    import timing
    import TimeTable
    for d in timing.daysOfWeek():
        dayData = timeTable.loc[d]
        periodList = list()
        for room in dayData.index:
            for period in dayData.columns:
                if(dayData[period][room] == TimeTable.theDefaultEmptyChar()
                   or dayData[period][room] == "['$', '$', '$', '$']"):
                    # Be carefull to check csv file for the value of dollars
                    continue
                data = extractPeriodDetail(timeTable, d,room,period)
                if(periodList.count(data) >= 1):
                    print('Duplicate : %s'%(data))
                    if(not removeDuplicateSubjectsOfDay(timeTable,d,room,period)):
                        continue
                    duplicatesInDay(timeTable)
                    timeTable.to_html('Duplicate.html')
                    return
                else:
                    periodList.append(data)
    timeTable.to_csv('TimeTable.csv')
    return

def calculateDuration(timeTable, day,room, period):
    import timing
    temp = eval(timeTable.loc[(day,room),period])
    time = temp[3].split('-')
    duration = (timing.toMin(time[1]) - timing.toMin(time[0]))
    return duration


def trySwap(timeTable,day,room,period,nextDay):
    import TimeTable
    oldDayData = timeTable.loc[day]
    nextDayData = timeTable.loc[nextDay]
    oldDayPeriodList = list()
    nextDayPeriodList = list()
    for r in oldDayData.index:
        for p in oldDayData.columns:
            if(oldDayData[p][r] != TimeTable.theDefaultEmptyChar()):
                oldDayPeriodList.append(extractPeriodDetail(timeTable,day,r,p))            
    for r in nextDayData.index:
        for p in nextDayData.columns:
            if(nextDayData[p][r] != TimeTable.theDefaultEmptyChar()):
                nextDayPeriodList.append(extractPeriodDetail(timeTable,nextDay,r,p))
    
    '''      # Debugging      
    for t in oldDayPeriodList:
        print(t)
    print('Next Day')
    for t in nextDayPeriodList:
        print(t)
    '''     
    
    
    if(nextDayPeriodList.count(extractPeriodDetail(timeTable,day,room,period)) == 0):
        for temp in nextDayPeriodList:
            
            ''' # Debugging
            print('temp: ',eval(temp)[0])
            print('old: ',eval(oldDayData[period][room])[0])
            print('class match:',(eval(temp)[0] == eval(oldDayData[period][room])[0]))
            print('count : ',oldDayPeriodList.count(temp) == 0)
            '''
            if((eval(temp)[3] == calculateDuration(timeTable, day,room,period)) and
               (eval(temp)[0] == eval(oldDayData[period][room])[0]) and
               oldDayPeriodList.count(temp) == 0):
                for r in nextDayData.index:
                    for p in nextDayData.columns:
                        if(extractPeriodDetail(timeTable,nextDay,r,p) == temp):
                            input('Doing swapping...')
                            data1 = eval(timeTable.loc[(day,room),period])
                            data2 = eval(timeTable.loc[(nextDay,r),p])
                            small1 = data1[:3].copy()
                            small2 = data2[:3].copy()
                            small2.extend(data1[3:].copy())
                            small1.extend(data2[3:].copy())
                            timeTable.loc[(day,room),period] = str(small2)
                            timeTable.loc[(nextDay,r),p] = str(small1)
                            print('Swapped %s with %s' %(small1, small2))
                            timeTable.to_html('Duplicate.html')
                            return True
    return False

def removeDuplicateSubjectsOfDay(timeTable,day,room,period):

    import timing
    for d in timing.daysOfWeek():
        if (d == day):
            continue
        if(trySwap(timeTable, day,room,period, d)):
            return True
    return False
   
def extractPeriodDetail(timeTable,day,room,period):
    import TimeTable
    if(timeTable.loc[(day,room),period] == TimeTable.theDefaultEmptyChar()):
        return TimeTable.theDefaultEmptyChar()
    elif(timeTable.loc[(day,room),period] == "['$', '$', '$', '$']"):
        return "['$', '$', '$', '$']"
    import timing
    temp = eval(timeTable.loc[(day,room),period])
    temp[3] = calculateDuration(timeTable, day,room, period)
    data = str(temp)
    return data
