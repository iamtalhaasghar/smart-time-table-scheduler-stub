def createTimeTable():
    
    import Timing
    periods = Timing.makePeriods()

    import room
    import lab

    allRooms = room.readAllRooms()
    allRooms = [ i[0] for i in allRooms]
    allLabs = lab.readAllLabs()
    allLabs = [ i[0] for i in allLabs]
    
    combinedRoom = list()
    combinedRoom.extend(allRooms)
    combinedRoom.extend(allLabs)
    
    days = list()
    for i in Timing.daysOfWeek():
        for j in range(0, len(combinedRoom)):
            days.append(i)

    room = list()
    for i in range(0,len(Timing.daysOfWeek())):
        room.extend(combinedRoom)

    import pandas as pd
    dataF = pd.DataFrame(index = [days,room],
                         columns = ['P%s'%(i) for i in range(1,len(periods)+1)])
    dataF = dataF.rename_axis(['Days','Rooms'], axis = 'index')
    dataF = dataF.fillna(theDefaultEmptyChar())
    
    import Filer
    folder = Filer.createTimeTableFolder()
    dataF.to_csv('%s/%sFormat.csv'%(folder, Filer.TIME_TABLE_FILE_NAME))
    dataF.to_csv('%s/%s.csv'%(folder, Filer.TIME_TABLE_FILE_NAME))

def readTimeTable():
    import Filer
    fileName = '%s/%s.csv' % (Filer.TIME_TABLE_FOLDER, Filer.TIME_TABLE_FILE_NAME)
    import pandas as pd
    data = pd.read_csv(fileName)
    data = data.set_index(['Days','Rooms'])
    return data


def theDefaultEmptyChar():
    return '-'
def theDefaultLabChars():
    return 'LAB'
def theConsecutivePeriodChar():
    return '*'

def readTimeHeaders():
    import os
    import Filer
    p = '%s/%s' % (Filer.DATA_FOLDER, Filer.TIME_HEADER_FILE_NAME)
    if(not os.path.exists(p)):
        print('Path %s does not exists.'%(p))
        input('TODO: Exception')
    timeList = list()
    with open(p,'r') as f:
        data = f.read()
        timeList = eval(data)
        timeList.insert(0,'')
    return timeList

def makeConsecutivePeriods(timeTable,className,subjectCode,subject
                             ,day, room, period,startTime,endTime):
    import Timing
    timeList = readTimeHeaders()
    periodList = list(timeTable.columns)
    currentEndTime = Timing.toMin(timeList[int(period[1:])].split('-')[1])
    if(currentEndTime < Timing.toMin(endTime)):
        nextPeriod = (periodList.index(period)) + 1

        if(nextPeriod >= len(timeTable.columns)):
            return False
        nextPeriodName = periodList[nextPeriod]

        import TimeTable
        if(timeTable.loc[(day,room),nextPeriodName] != TimeTable.theDefaultEmptyChar()):
            return False

        # Clash Resolve
        import Duplicates
        import teacher
        teacherName = teacher.findTeacherOfSubject(subjectCode,className)
        if((Duplicates.doesClassClashExist(timeTable, day, period, className)) or
            (Duplicates.doesTeacherClashExist(timeTable, day,period, teacherName))):
                 return False

        if(makeConsecutivePeriods(
            timeTable, className, subjectCode, subject, day, room,
            nextPeriodName,startTime,endTime)):
                import teacher
                teacherName = teacher.findTeacherOfSubject(subjectCode,className)
                timeTable.loc[(day,room), nextPeriodName] = str(
                    [className,'%s%s'%(theConsecutivePeriodChar(),subject),
                     teacherName,'%s-%s'%(startTime,endTime)])
        else:
            return False
    return True

def allotLab(timeTable,className,subject,duration):
    
    import lab
    import Timing
    import teacher
    timeList = readTimeHeaders()
    uniEndTime = Timing.toMin(timeList[-1].split('-')[1])

    labName = lab.findLabOfSubject(subject[0],className)

    for l in [i[0] for i in lab.readAllLabs()]:
        for p in timeTable.columns:
            for d in Timing.daysOfWeek():
                
                if(labName == l and (timeTable.loc[(d,l),p] == theDefaultEmptyChar())):
                    teacherName = teacher.findTeacherOfSubject(subject[0],className)
                    # Clash Resolves
                    import Duplicates
                    if((Duplicates.doesClassClashExist(timeTable, d, p, className)) or
                       (Duplicates.doesTeacherClashExist(timeTable, d,p, teacherName))):
                            continue
                    #---------------
                    s = timeList[int(p[1:])].split('-')[0]
                    e = Timing.toMin(s) + subject[2]
                    if(e > uniEndTime):
                        continue
                    
                    e = Timing.toHour(e)
                    if(subject[2] <= duration):
                        timeTable.loc[(d,l),p] = [
                            className,subject[1],teacherName,('%s-%s'%(s,e))]
                        return True
                    else:
                        if(makeConsecutivePeriods(
                            timeTable,className,subject[0],subject[1],d,l,p,s,e)):
                            timeTable.loc[(d,l),p] = [
                                className,'%s%s'%(theConsecutivePeriodChar(),subject[1]),
                                teacherName,('%s-%s'%(s,e))]
                        else:
                            continue
                        return True
    return False
                
def generateTimeTable(department, degree, className):
    'class whose timetable is to be generated'

    import Filer
    duration = int(Filer.readGeneralSettingsFile('PeriodDuration'))
    import pandas as pd
    import Semester
    import teacher
    timeTable = readTimeTable()
    courseTable = Semester.readClass(department, degree, className)

    subjects = list()   # [courseCode, courseName, duration]

    for i in courseTable.index:
        tempSubject = courseTable.loc[i,'Subjects']
        creditMin = courseTable.loc[i,'CM']
        if(tempSubject.endswith(theDefaultLabChars())):
            subjects.append([i,tempSubject,creditMin])
            continue
        while(creditMin != 0):
            if(creditMin == duration):
                subjects.append([i,tempSubject,duration])
                creditMin -= duration
            elif(creditMin > duration):
                if((creditMin-duration) >= duration):
                    subjects.append([i,tempSubject,duration])
                    creditMin -= duration
                else:
                    subjects.append([i,tempSubject,creditMin])
                    creditMin -= creditMin
            else:
                subjects.append([i,tempSubject, creditMin])
                creditMin -= creditMin
                
    import Timing
    timeList = readTimeHeaders()
    uniEndTime = Timing.toMin(timeList[-1].split('-')[1])
    import random
    random.shuffle(subjects)
    import room
    
    for r in [i[0] for i in room.readAllRooms()]:
        if(r.split()[0] != department):
            continue
        for p in timeTable.columns:
                for d in Timing.daysOfWeek():
                    if((len(subjects)!=0)):
                        temp = subjects[-1]
                        if(temp[1].endswith(theDefaultLabChars())):
                            if(allotLab(timeTable,className,temp,duration)):
                                temp = subjects.pop()
                            else:
                                print('Not enough labs...')
                                return
                            continue
                        teacherName = teacher.findTeacherOfSubject(temp[0],className)
                        if((timeTable.loc[(d,r),p] == theDefaultEmptyChar())):
                            # Clash Resolves
                            import Duplicates
                            if((Duplicates.doesClassClashExist(timeTable, d, p, className)) or
                               (Duplicates.doesTeacherClashExist(timeTable, d,p, teacherName))):
                                    continue
                            #---------------
                            
                            s = timeList[int(p[1:])].split('-')[0]
                            e = Timing.toMin(s) + temp[2]
                            if(e > uniEndTime):
                                continue
                            e = Timing.toHour(e)
                            
                            if(temp[2] <= duration):
                                timeTable.loc[(d,r),p] = [
                                    className,temp[1],teacherName,('%s-%s'%(s,e))]
                            else:
                                if(makeConsecutivePeriods(
                                    timeTable,className,temp[0],temp[1],d,r,p,s,e)):
                                    timeTable.loc[(d,r),p] = [
                                        className,'%s%s'%(theConsecutivePeriodChar(),temp[1]),
                                        teacherName,('%s-%s'%(s,e))]
                                else:
                                    continue
                            temp = subjects.pop()
                                 
                                
    if(len(subjects)!=0):
        print('Not enough rooms...')
        
    import Filer
    timeTable.to_csv('%s/%s.csv'%(Filer.TIME_TABLE_FOLDER, Filer.TIME_TABLE_FILE_NAME))
    timeTable.to_html('%s/%s.html'%(Filer.TIME_TABLE_FOLDER, Filer.TIME_TABLE_FILE_NAME))

def generateCompleteTimeTable():
    import Filer
    createTimeTable()
    departs = list(Filer.listAllDepartments())
    for d in departs:    
        programs = list(Filer.programsOfDepartment(d))
        for p in programs:
            classes = list(Filer.classesOfProgram(d, p))
            for c in classes:
                print('Generating Time Table of : Depart: %s Program: %s Class: %s'% (p,d,c))
                generateTimeTable(d, p, c.split('.')[0])
                print('Done!! for %s'% c)




def seemsToBeConsecutive(timeTable, d,r,p):

    if(timeTable.loc[(d,r),p] == theDefaultEmptyChar()):
        return False

    data = eval(timeTable.loc[(d,r),p])
    if theConsecutivePeriodChar() in data[1]:
        return True

    return False        




    
    
