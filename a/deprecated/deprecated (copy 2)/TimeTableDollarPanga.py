def createTimeTable():
    import timing
    periods = timing.makePeriods()

    import room
    allRooms = room.readAllRooms().Name

    days = list()
    for i in timing.daysOfWeek():
        for j in range(0, len(allRooms)):
            days.append(i)

    rooms = list()
    for i in range(0,len(timing.daysOfWeek())):
        rooms.extend(allRooms)

    import pandas as pd
    dataF = pd.DataFrame(index = [days,rooms],columns = ['P%s'%(i) for i in range(1,len(periods)+1)])
    dataF = dataF.rename_axis(['Days','Rooms'], axis = 'index')
    initializeCells(dataF)
    dataF.to_csv('TimeTable.csv')

def readTimeTable(fileName='TimeTable.csv'):
    import pandas as pd
    data = pd.read_csv(fileName)
    data = data.set_index(['Days','Rooms'])
    return data


def theDefaultEmptyChar():
    return '#'

def initializeCells(timeTableFrame):
    'timeTableFrame whose cells are to be initialized'
    import timing
    import room
    for p in list(timeTableFrame.columns):
            for d in timing.daysOfWeek():
                for r in room.readAllRooms().Name:
                    timeTableFrame.loc[(d,r),p] = theDefaultEmptyChar()

def generateTimeTable(className,duration):
    'class whose timetable is to be generated'
    
    import pandas as pd
    timeTable = readTimeTable()
    import semester
    courseTable = semester.readClass(className)

    subjects = list()

    print(courseTable)
    for i in courseTable.index:
        tempSubject = courseTable.loc[i,'Subjects']
        creditMin = courseTable.loc[i,'CM']
        while(creditMin != 0):
            if(creditMin == duration):
                subjects.append([tempSubject,duration])
                creditMin -= duration
            elif(creditMin > duration):
                if((creditMin-duration) >= duration):
                    subjects.append([tempSubject,duration])
                    creditMin -= duration
                else:
                    subjects.append([tempSubject,creditMin])
                    creditMin -= creditMin
            else:
                subjects.append([tempSubject, creditMin])
                creditMin -= creditMin
    print(subjects)
    input('wait..')
    
    timeList = list()
    with open('timeHeader.txt') as f:
        data = f.read()
        timeList = eval(data)
        timeList.insert(0,'')
    import random
    random.shuffle(subjects)
    import timing
    import room
    fetchRoom = None
    for r in room.readAllRooms().Name:
        for p in timeTable.columns:
                if(fetchRoom == True):
                     input('Fetching room..')
                     print(timeTable.loc[(d,r),p])
                     input()
                     timeTable.loc[(d,r),p] = '$'
                     fetchRoom = False
                for d in timing.daysOfWeek():
                    if((len(subjects)!=0)):
                        
                        if((timeTable.loc[(d,r),p] == theDefaultEmptyChar())): 
                            temp = subjects.pop()
                            if(temp[1] == duration):
                                timeTable.loc[(d,r),p] = [
                                    className,temp[0],'Teacher',timeList[int(p[-1])]]
                            elif(temp[1] < duration):
                                print('actual : ',timeList[int(p[-1])])
                                print('Duration : ',temp[1])
                                s = timeList[int(p[-1])].split('-')[0]
                                
                                e = timing.toHour(timing.toMin(s) + temp[1])
                                print('Now Start :',s)
                                print('Now End : ',e)
                                timeTable.loc[(d,r),p] = [
                                    className,temp[0],'Teacher',('%s-%s'%(s,e))]
                            else:
                                print('actual : ',timeList[int(p[-1])])
                                print('Duration : ',temp[1])
                                s = timeList[int(p[-1])].split('-')[0]
                                e = timing.toHour(timing.toMin(s) + temp[1]) 
                                print('Now Start :',s)
                                print('Now End : ',e)
                                timeTable.loc[(d,r),p] = [
                                    className,temp[0],'Teacher',('%s-%s'%(s,e))]
                                fetchRoom = True
                                
    if(len(subjects)!=0):
        print('Not enough rooms...')
    timeTable.to_csv('TimeTable.csv')
    timeTable.to_html('TimeTable.html')





