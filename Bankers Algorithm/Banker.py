from __future__ import print_function
from __future__ import division
import copy
import sys

# class to store all data
class Data:
    taskArray = []
    def __init__(self,numOfTasks,typesAmount,units):
        self.numOfTasks = numOfTasks
        self.typesAmount = typesAmount
        self.units = units
    def __repr__(self):
        return str("Units: {0} \n{1}".format(self.units, self.taskArray))

# class to store each cycle
class Cycle:
    def __init__(self, activity, taskNumber, delay, type, amount):
        self.activity = activity
        self.taskNumber = taskNumber
        self.delay = delay
        self.type = type
        self.amount = amount
    def __repr__(self):
        return str("{0} {1} {2} {3} {4}".format(self.activity, self.taskNumber, self.delay, self.type, self.amount))

# class to store each task
class Task:
    def __init__(self, taskNumber, currentClaim, maxClaim, cycleArray):
        self.currentClaim = currentClaim
        self.maxClaim = maxClaim
        self.cycleArray = cycleArray
        self.endTime = 0
        self.waitTime = 0
        self.aborted = False
        self.taskNumber = taskNumber
        self.originalIndex = None
        self.maxRequest = None
        self.processed = False

    def __repr__(self):
        if self.aborted == True:
            return str(("[Task {0} ABORTED, Max:{1} Current:{2} CycleArray:{3}]".format(self.taskNumber, self.maxClaim, self.currentClaim, self.cycleArray)))
        return str("[Task {0}, Max:{1} Current:{2} CycleArray:{3}]".format(self.taskNumber, self.maxClaim, self.currentClaim, self.cycleArray))

# checks if the tasks are deadlocked by checking to see if all most recent cycles for each task are doable or not
def checkDeadlock(totalUnits,tasks):
    for task in tasks:
        if task.aborted == False and len(task.cycleArray) > 0:
            index = task.cycleArray[0].type-1
            if totalUnits[index] >= task.cycleArray[0].amount or task.cycleArray[0].activity != "request":
                return False
    return True

# checks if the tasks are all completed
def checkDone(tasks):
    for task in tasks:
        if task.aborted == False:
            if len(task.cycleArray) > 0:
                return False
    return True

# calculates maximum possible request given a task array
def calculateMaxRequest(taskArray):
    for task in taskArray:
        task.maxRequest = ([x - y for x, y in zip(task.maxClaim, task.currentClaim)])
    return taskArray

# check if the requested operation is safe by simulating the data, first executing the request of the cycle
# then assuming all tasks have given the maximum request, it then attempts to resolve all these requests
# if all the requests cannot be resolved, it returns False
def checkSafe(data, cycleRequest):
    data = copy.deepcopy(data)
    taskArray = data.taskArray
    taskArray[cycleRequest.taskNumber-1].currentClaim[cycleRequest.type-1] += cycleRequest.amount
    data.units[cycleRequest.type-1] -= cycleRequest.amount
    taskArray = calculateMaxRequest(taskArray)
    taskArray = [task for task in taskArray if (task.aborted == False and len(task.cycleArray) > 0)]
    while True:
        if (all(task.processed == True for task in taskArray)):
            return True
        found = False
        for task in taskArray:
            if task.processed == False:
                if (all(i >= 0 for i in [x-y for (x,y) in zip(data.units, task.maxRequest)])):
                    found = True
                    data.units = [x+y for (x,y) in zip(data.units,task.currentClaim)]
                    task.processed = True
                    break
        if found == False:
            return False

# reads file and returns a data Object
def readFile(fileName):
    f = open(fileName,"r")
    text = f.read()
    text = text.split()
    for i in range(len(text)):
        if text[i].isdigit():
            text[i] = int(text[i])
    units = []
    for i in range(2,2+text[1]):
        units.append(text[i])
    returnObj = Data(text[0],text[1],units)
    idx = 2+text[1]
    cycleArray = []
    while (idx < len(text)-1):
        obj = Cycle(text[idx],text[idx+1],text[idx+2],text[idx+3],text[idx+4])
        idx += 5
        cycleArray.append(obj)
    tasksArray = []
    for i in range(returnObj.numOfTasks):
        array = []
        for cycle in cycleArray:
            if cycle.taskNumber == i+1:
                array.append(cycle)
        maxClaim = []
        newArray = []
        for cycle in array:
            if cycle.activity == "initiate":
                maxClaim.append(cycle.amount)
            else:
                newArray.append(cycle)
        array = newArray
        obj = Task(i+1, [0]*len(maxClaim),maxClaim,array)
        tasksArray.append(obj)
    returnObj.taskArray = tasksArray
    f.close()
    return returnObj

# prints data correctly
def printData(algo,data):
    print(algo)
    totalTime = 0
    totalWaitTime = 0
    allAborted = True
    for task in data.taskArray:
        if task.aborted:
            print("Task{0}   Aborted".format(task.taskNumber))
        else:
            allAborted = False
            print("Task{0}   {1}   {2}   {3}%".format(task.taskNumber, task.endTime, task.waitTime, (task.waitTime / task.endTime) * 100))
            totalTime += task.endTime
            totalWaitTime += task.waitTime
    if allAborted:
        print("Total   0   0   0%")
    else:
        print("Total   {0}   {1}   {2}%".format(totalTime, totalWaitTime, (totalWaitTime / totalTime) * 100))

# First In First Out
def fifo(data):
    currentTime = data.typesAmount
    taskArray = data.taskArray
    totalUnits = data.units
    # processes cycles until all tasks are done or aborted
    while (True):
        blockedTasks = []
        releasedUnits = [0] * len(totalUnits)
        tempTaskArray = []
        # processes each task and retrieves the most recent cycle for each task
        # depending on what the cycle is and the numbers related to it, it may:
        # fulfill the request
        # block the request
        # delay the action
        # release resources
        # terminate the task
        for task in taskArray:
            if task.aborted:
                continue
            if len(task.cycleArray) > 0:
                cycle = task.cycleArray[0]
                claimIndex = cycle.type-1
                if cycle.activity == "request":
                    # processes delay
                    if cycle.delay > 0:
                        cycle.delay -= 1
                        tempTaskArray.append(task)
                    else:
                        # if task request cannot be fulfilled
                        if totalUnits[claimIndex] < cycle.amount:
                            task.waitTime += 1
                            blockedTasks.append(task)
                        # processes request
                        else:
                            totalUnits[claimIndex] -= cycle.amount
                            task.currentClaim[claimIndex] += cycle.amount
                            task.cycleArray.pop(0)
                            tempTaskArray.append(task)
                elif cycle.activity == "release":
                    # processes delay
                    if cycle.delay > 0:
                        cycle.delay -= 1
                        tempTaskArray.append(task)
                    # releases resources
                    else:
                        releasedUnits[claimIndex] += cycle.amount
                        task.currentClaim[claimIndex] -= cycle.amount
                        task.cycleArray.pop(0)
                        tempTaskArray.append(task)
                elif cycle.activity == "terminate":
                    # processes delay
                    if cycle.delay > 0:
                        cycle.delay -= 1
                        tempTaskArray.append(task)
                    else:
                        task.endTime = currentTime
                        task.cycleArray.pop(0)
                        tempTaskArray.append(task)
        # only adds the released resources after all tasks have processed this cycle
        totalUnits = [x + y for x, y in zip(totalUnits, releasedUnits)]
        taskArray = blockedTasks + tempTaskArray
        currentTime += 1
        # checks if all tasks are done
        if checkDone(taskArray):
            break
        # checks if deadlock has occurred by using the checkDeadlock method
        if checkDeadlock(totalUnits,taskArray):
            # sorting is purely to make sure that it terminates tasks in order of lowest task to highest task
            for i in range(len(taskArray)):
                task.originalIndex = i
            taskArray.sort(key = lambda task: task.taskNumber)
            # this aborts tasks until the system is no longer deadlocked
            for task in taskArray:
                if len(task.cycleArray) == 0:
                    continue
                if task.aborted == False:
                    task.aborted = True
                    totalUnits = [x+y for x,y in zip(totalUnits,task.currentClaim)]
                    if checkDeadlock(totalUnits,taskArray):
                        continue
                    else:
                        break
            for task in taskArray:
                if len(task.cycleArray) == 0:
                    continue
                if task.aborted == False:
                    task.waitTime += 1
            currentTime += 1
            taskArray.sort(key = lambda task:task.originalIndex)
    printData("FIFO",data)
    return data

# Bankers
def bankers(data):
    currentTime = data.typesAmount
    taskArray = data.taskArray
    # aborts any tasks that maxClaim > totalUnits
    for task in taskArray:
        if not(all(i >= 0 for i in [x-y+z for (x,y,z) in zip(data.units, task.maxClaim, task.currentClaim)])):
            print("Task {0} claimed more resources than there are present. Aborted by Bankers.".format(task.taskNumber))
            task.aborted = True
    # processes cycles until all tasks are done or aborted
    while (True):
        #print(data)
        blockedTasks = []
        releasedUnits = [0] * len(data.units)
        tempTaskArray = []
        # processes each task and retrieves the most recent cycle for each task
        # depending on what the cycle is and the numbers related to it, it may:
        # fulfill the request
        # block the request
        # delay the action
        # release resources
        # terminate the task
        # abort the task
        for task in taskArray:
            if task.aborted:
                continue
            if len(task.cycleArray) > 0:
                cycle = task.cycleArray[0]
                claimIndex = cycle.type - 1
                if cycle.activity == "request":
                    # processes delay
                    if cycle.delay > 0:
                        cycle.delay -= 1
                        tempTaskArray.append(task)
                    else:
                        # if task requests more than max claim, abort it
                        if cycle.amount > (task.maxClaim[claimIndex] - task.currentClaim[claimIndex]):
                            print("During cycle {0}-{1} of Bankers, Task {2} exceeded max claim of resource {3} and was aborted.".format(currentTime, currentTime+1, task.taskNumber, cycle.type))
                            task.aborted = True
                            releasedUnits = [x + y for x, y in zip(task.currentClaim, releasedUnits)]
                            tempTaskArray.append(task)
                        # if is not safe to give task the resources then wait
                        elif not checkSafe(data,cycle):
                            task.waitTime += 1
                            blockedTasks.append(task)
                        # processes request
                        else:
                            data.units[claimIndex] -= cycle.amount
                            task.currentClaim[claimIndex] += cycle.amount
                            task.cycleArray.pop(0)
                            tempTaskArray.append(task)
                elif cycle.activity == "release":
                    # processes delay
                    if cycle.delay > 0:
                        cycle.delay -= 1
                        tempTaskArray.append(task)
                    # releases resources
                    else:
                        releasedUnits[claimIndex] += cycle.amount
                        task.currentClaim[claimIndex] -= cycle.amount
                        task.cycleArray.pop(0)
                        tempTaskArray.append(task)
                elif cycle.activity == "terminate":
                    # processes delay
                    if cycle.delay > 0:
                        cycle.delay -= 1
                        tempTaskArray.append(task)
                    else:
                        task.endTime = currentTime
                        task.cycleArray.pop(0)
                        tempTaskArray.append(task)
        # only adds the released resources after all tasks have processed this cycle
        data.units = [x + y for x, y in zip(data.units, releasedUnits)]
        taskArray = blockedTasks + tempTaskArray
        currentTime += 1
        # checks if all tasks are done
        if checkDone(taskArray):
            break
    printData("BANKERS", data)
    return data

# driver code
text = sys.argv[1]
print("\n")
data = readFile(text)
fifo(data)
print("\n")
data = readFile(text)
bankers(data)

