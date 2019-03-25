from __future__ import print_function
from __future__ import division
import sys

class Process:
    def __init__(self):
        self.A = None
        self.B = None
        self.C = None
        self.IO = None
        self.cycles = []
        self.originalIndex = None
        self.entryCycle = None # used in Round Robin only
        self.cpuLeft = 0 # used in Round Robin only
        
    def __repr__(self):
        return str("{0} {1} {2} {3}".format(self.A,self.B,self.C,self.IO))
    
    def finishingTime(self):
        for i in range(len(self.cycles)):
            if self.cycles[i].status == "terminated":
                return i-1
        return len(self.cycles)-1
    
    def turnaroundTime(self):
        return self.finishingTime() - self.A

    def ioTime(self):
        return sum(cycle.status == "blocked" for cycle in self.cycles)

    def waitingTime(self):
        return sum(cycle.status == "ready" for cycle in self.cycles)

class Cycle:
    def __init__(self, status, num):
        self.status = status # this will be either unstarted, running, blocked or terminated
        self.num = num
    def __repr__(self):
        return str("{0} {1}".format(self.status, self.num))

# reads file and returns an Array of Process Objects
def readFile(fileName):
    f = open(fileName,"r")
    text = f.read()
    text = text.split()
    for i in range(len(text)):
        if text[i].isdigit():
            text[i] = int(text[i])
    returnArray = []
    index = 1
    for i in range(text[0]):
        obj = Process()
        obj.A = text[index]
        obj.B = text[index+1]
        obj.C = text[index+2]
        obj.IO = text[index+3]
        returnArray.append(obj)
        index += 4
    return returnArray

# generate random number
# fileObj should always be the already opened "random-numbers".txt
def randomOS(fileObj, u, timeLeft):
    num = fileObj.readline()
    x = int(num)
    t = 1 + (x % u)
    return t    

def cpuUtilization(processArray):
    used = 0
    for i in range(len(processArray[0].cycles)):
        for process in processArray:
            if process.cycles[i].status == "running":
                used += 1
                continue
    return used/(len(processArray[0].cycles)-1)
    
def ioUtilization(processArray):
    used = 0
    for i in range(len(processArray[0].cycles)):
        for process in processArray:
            if process.cycles[i].status == "blocked":
                used += 1
                continue
    return used/(len(processArray[0].cycles)-1)
    
def averageTurnaroundTime(processArray):
    return sum(process.turnaroundTime() for process in processArray)/len(processArray)

def averageWaitingTime(processArray):
    return sum(process.waitingTime() for process in processArray)/len(processArray)

def printOutput(processArray, originalProcessArray, algorithm,verbose):
    if verbose:
        print("\nThis detailed printout gives the state and remaining burst for each process\n")
        for i in range(len(processArray[0].cycles)):
            print("Before cycle {0}: ".format(i), end='')
            for process in processArray:
                print(str(process.cycles[i]) + " ", end='')
            print("\n", end='')
    print("The scheduling algorithm used was {0}\n".format(algorithm))
    for i in range(len(processArray)):
        process = processArray[i]
        print("Process {0}:".format(i))
        print("(A,B,C,IO) = {0}".format(originalProcessArray[i]))
        print("Finishing time: {0}".format(process.finishingTime()))
        print("Turnaround time: {0}".format(process.turnaroundTime()))
        print("I/O time: {0}".format(process.ioTime()))
        print("Waiting time: {0}\n".format(process.waitingTime()))
    print("Summary Data:")
    print("Finishing time: {0}".format(len(processArray[0].cycles)-1))
    print("CPU Utilization: {0}".format(cpuUtilization(processArray)))
    print("I/O Utilization: {0}".format(ioUtilization(processArray)))
    print("Throughput: {0} per hundred cycles".format(len(processArray)/(len(processArray[0].cycles)-1)*100))
    print("Average turnaround time: {0}".format(averageTurnaroundTime(processArray)))
    print("Average waiting time: {0}".format(averageWaitingTime(processArray)))

def fcfs(randomNumbers, processArray, verbose):
    originalProcessArray = [str(i) for i in processArray]
    processArray.sort(key=lambda x: x.A)
    sortedProcessArray = [str(i) for i in processArray]
    for i in range(len(processArray)):
        processArray[i].originalIndex = i
    queue = []
    currentCycle = 0
    while currentCycle == 0 or (queue != [] or not all(process.cycles[-1].status == "terminated" for process in processArray)):
        newProcessArray = []
        processArray.sort(key=lambda x: x.originalIndex)
        # goes through processes not in queue
        for process in processArray:

            # process not yet started
            if process.A >= currentCycle:
                cycle = Cycle("unstarted", 0)
                process.cycles.append(cycle)
                newProcessArray.append(process)
                continue
            
            previousCycle = process.cycles[-1]

            # process not yet started, but ready now
            if previousCycle.status == "unstarted":
                queue.append(process)
            
            # process already finished
            elif previousCycle.status == "terminated" or process.C == 0:
                cycle = Cycle("terminated", 0)
                process.cycles.append(cycle)
                newProcessArray.append(process)
            
            # process is in IO process
            elif previousCycle.status == "blocked":
                # process is on last cycle of IO process
                if previousCycle.num == 1:
                    queue.append(process)
                else:
                    cycle = Cycle("blocked", previousCycle.num-1)
                    process.cycles.append(cycle)
                    newProcessArray.append(process)
        processArray = newProcessArray

        # goes through queue 
        busy = False
        newQueue = []
        ioNum = 0
        cpuNum = 0
        for process in queue:

            previousCycle = process.cycles[-1]
            
            # process in middle of running
            if previousCycle.status == "running":
                # process is on last cycle of CPU process
                if previousCycle.num == 1 or process.C == 1:
                    process.C -= 1
                    if process.C == 0:
                        cycle = Cycle("terminated", 0)
                    else:
                        if ioNum == 0:
                            ioNum = randomOS(randomNumbers, process.IO, process.C)
                        cycle = Cycle("blocked", ioNum) # needs random
                    process.cycles.append(cycle)
                    processArray.append(process)
                else:
                    process.C -= 1
                    busy = True
                    cycle = Cycle("running", previousCycle.num-1)
                    process.cycles.append(cycle)
                    newQueue.append(process)
                continue

            if busy:
                cycle = Cycle("ready", 0)
                process.cycles.append(cycle)
                newQueue.append(process)
            else:
                if cpuNum == 0:
                    cpuNum = randomOS(randomNumbers, process.B, process.C)
                busy = True
                cycle = Cycle("running", cpuNum) # needs random
                process.cycles.append(cycle)
                newQueue.append(process)
        queue = newQueue
        currentCycle += 1

    # deletes extra line (used to make sure all processes have terminated)
    for process in processArray:
        del process.cycles[-1]

    processArray.sort(key=lambda x: x.originalIndex)

    # print output
    print("The original input was: {0}  {1}".format(len(processArray),str('  '.join(originalProcessArray))))
    print("The sorted input is: {0}  {1}".format(len(processArray),str('  '.join(sortedProcessArray))))
    printOutput(processArray, sortedProcessArray, "First Come First Served", verbose)

def roundRobin(randomNumbers, processArray, verbose, quantum):
    originalProcessArray = [str(i) for i in processArray]
    processArray.sort(key=lambda x: x.A)
    sortedProcessArray = [str(i) for i in processArray]
    for i in range(len(processArray)):
        processArray[i].originalIndex = i
    queue = []
    currentCycle = 0
    while currentCycle == 0 or (
            queue != [] or not all(process.cycles[-1].status == "terminated" for process in processArray)):
        newProcessArray = []
        processArray.sort(key=lambda x: x.originalIndex)
        # goes through processes not in queue
        for process in processArray:

            # process not yet started
            if process.A >= currentCycle:
                cycle = Cycle("unstarted", 0)
                process.cycles.append(cycle)
                newProcessArray.append(process)
                continue

            previousCycle = process.cycles[-1]

            # process not yet started, but ready now
            if previousCycle.status == "unstarted":
                process.entryCycle = currentCycle
                queue.append(process)

            # process already finished
            elif previousCycle.status == "terminated" or process.C == 0:
                cycle = Cycle("terminated", 0)
                process.cycles.append(cycle)
                newProcessArray.append(process)

            # process is in IO process
            elif previousCycle.status == "blocked":
                # process is on last cycle of IO process
                if previousCycle.num == 1:
                    process.entryCycle = currentCycle
                    queue.append(process)
                else:
                    cycle = Cycle("blocked", previousCycle.num - 1)
                    process.cycles.append(cycle)
                    newProcessArray.append(process)
        processArray = newProcessArray

        # goes through queue
        busy = False
        newQueue = []
        ioNum = 0
        cpuNum = 0
        if queue != []:
            queue.sort(key=lambda x: (x.entryCycle, x.originalIndex))
        for process in queue:

            previousCycle = process.cycles[-1]

            # process in middle of running
            if previousCycle.status == "running":
                # process is on last cycle of CPU process
                if previousCycle.num == 1 or process.C == 1:
                    process.C -= 1
                    if process.C == 0:
                        cycle = Cycle("terminated", 0)
                    # CPU burst preempted
                    elif process.cpuLeft > 0:
                        if len(queue) == 1:
                            if process.cpuLeft > quantum:
                                process.cpuLeft -= quantum
                                cpuNum = quantum
                            else:
                                cpuNum = process.cpuLeft
                                process.cpuLeft = 0
                            cycle = Cycle("running", cpuNum)
                            busy = True
                            process.cycles.append(cycle)
                            process.entryCycle = currentCycle
                            newQueue.append(process)
                            continue
                        else:
                            cycle = Cycle("ready", 0)
                            process.cycles.append(cycle)
                            process.entryCycle = currentCycle
                            newQueue.append(process)
                            continue
                    else:
                        if ioNum == 0:
                            ioNum = randomOS(randomNumbers, process.IO, process.C)
                        cycle = Cycle("blocked", ioNum)  # needs random
                    process.cycles.append(cycle)
                    processArray.append(process)
                else:
                    process.C -= 1
                    busy = True
                    cycle = Cycle("running", previousCycle.num - 1)
                    process.cycles.append(cycle)
                    newQueue.append(process)
                continue

            if busy:
                cycle = Cycle("ready", 0)
                process.cycles.append(cycle)
                newQueue.append(process)
            else:
                if process.cpuLeft > 0:
                    if process.cpuLeft > quantum:
                        process.cpuLeft -= quantum
                        cpuNum = quantum
                    else:
                        cpuNum = process.cpuLeft
                        process.cpuLeft = 0
                elif cpuNum == 0:
                    cpuNum = randomOS(randomNumbers, process.B, process.C)
                    if cpuNum > quantum:
                        process.cpuLeft = cpuNum - quantum
                        cpuNum = quantum
                busy = True
                cycle = Cycle("running", cpuNum)  # needs random
                process.cycles.append(cycle)
                newQueue.append(process)
        queue = newQueue
        currentCycle += 1
    # deletes extra line (used to make sure all processes have terminated)
    for process in processArray:
        del process.cycles[-1]

    processArray.sort(key=lambda x: x.originalIndex)

    # print output
    print("The original input was: {0}  {1}".format(len(processArray), str('  '.join(originalProcessArray))))
    print("The sorted input is: {0}  {1}".format(len(processArray), str('  '.join(sortedProcessArray))))
    printOutput(processArray, sortedProcessArray, "Round Robin", verbose)

def uni(randomNumbers, processArray, verbose):
    originalProcessArray = [str(i) for i in processArray]
    processArray.sort(key=lambda x: x.A)
    sortedProcessArray = [str(i) for i in processArray]
    for i in range(len(processArray)):
        processArray[i].originalIndex = i

    queue = []
    currentCycle = 0
    while currentCycle == 0 or (
            queue != [] or not all(process.cycles[-1].status == "terminated" for process in processArray)):
        newProcessArray = []
        # goes through processes not in queue
        for process in processArray:

            # process not yet started
            if process.A >= currentCycle:
                cycle = Cycle("unstarted", 0)
                process.cycles.append(cycle)
                newProcessArray.append(process)
                continue

            previousCycle = process.cycles[-1]

            # process not yet started, but ready now
            if previousCycle.status == "unstarted":
                queue.append(process)

            # process already finished
            if previousCycle.status == "terminated":
                cycle = Cycle("terminated", 0)
                process.cycles.append(cycle)
                newProcessArray.append(process)

        processArray = newProcessArray

        # goes through queue
        busy = False
        newQueue = []
        for process in queue:
            previousCycle = process.cycles[-1]

            if previousCycle.status == "running":
                # process is done computing
                if process.C == 1:
                    process.C -= 1
                    cycle = Cycle("terminated", 0)
                    process.cycles.append(cycle)
                    processArray.append(process)
                    continue
                busy = True
                process.C -= 1
                if previousCycle.num == 1:
                    ioNum = randomOS(randomNumbers, process.IO, process.C)
                    cycle = Cycle("blocked", ioNum)
                else:
                    cycle = Cycle("running", previousCycle.num-1)
                process.cycles.append(cycle)
                newQueue.append(process)
                continue

            elif previousCycle.status == "blocked":
                busy = True
                if previousCycle.num == 1:
                    cpuNum = randomOS(randomNumbers, process.B, process.C)
                    cycle = Cycle("running", cpuNum)
                else:
                    cycle = Cycle("blocked", previousCycle.num-1)
                process.cycles.append(cycle)
                newQueue.append(process)
                continue

            if busy:
                cycle = Cycle("ready", 0)
                process.cycles.append(cycle)
                newQueue.append(process)
            else:
                busy = True
                cpuNum = randomOS(randomNumbers, process.B, process.C)
                cycle = Cycle("running", cpuNum)
                process.cycles.append(cycle)
                newQueue.append(process)

        queue = newQueue
        currentCycle += 1

    # deletes extra line (used to make sure all processes have terminated)
    for process in processArray:
        del process.cycles[-1]

    processArray.sort(key=lambda x: x.originalIndex)

    # print output
    print("The original input was: {0}  {1}".format(len(processArray),str('  '.join(originalProcessArray))))
    print("The sorted input is: {0}  {1}".format(len(processArray),str('  '.join(sortedProcessArray))))
    printOutput(processArray, sortedProcessArray, "Uniprocessor", verbose)

def sjf(randomNumbers, processArray, verbose):
    originalProcessArray = [str(i) for i in processArray]
    processArray.sort(key=lambda x: x.A)
    sortedProcessArray = [str(i) for i in processArray]
    for i in range(len(processArray)):
        processArray[i].originalIndex = i

    queue = []
    currentCycle = 0
    busy = False
    runningProcess = None
    while currentCycle == 0 or (
            queue != [] or not all(process.cycles[-1].status == "terminated" for process in processArray)):
        newProcessArray = []
        # goes through processes not in queue
        for process in processArray:

            # process not yet started
            if process.A >= currentCycle:
                cycle = Cycle("unstarted", 0)
                process.cycles.append(cycle)
                newProcessArray.append(process)
                continue

            previousCycle = process.cycles[-1]

            # process not yet started, but ready now
            if previousCycle.status == "unstarted":
                queue.append(process)

            # process already finished
            elif previousCycle.status == "terminated" or process.C == 0:
                cycle = Cycle("terminated", 0)
                process.cycles.append(cycle)
                newProcessArray.append(process)

            # process is in IO process
            elif previousCycle.status == "blocked":
                # process is on last cycle of IO process
                if previousCycle.num == 1:
                    queue.append(process)
                else:
                    cycle = Cycle("blocked", previousCycle.num - 1)
                    process.cycles.append(cycle)
                    newProcessArray.append(process)
        processArray = newProcessArray

        # goes through queue
        newQueue = []
        ioNum = 0
        cpuNum = 0
        queue.sort(key=lambda x: x.originalIndex)
        queue.sort(key=lambda x: x.C)
        if runningProcess is not None:
            if runningProcess in queue:
                queue.remove(runningProcess)
                queue = [runningProcess] + queue
        for process in queue:

            previousCycle = process.cycles[-1]

            # process in middle of running
            if previousCycle.status == "running":
                # process is on last cycle of CPU process
                if previousCycle.num == 1 or process.C == 1:
                    process.C -= 1
                    busy = False
                    if process.C == 0:
                        cycle = Cycle("terminated", 0)
                    else:
                        if ioNum == 0:
                            ioNum = randomOS(randomNumbers, process.IO, process.C)
                        cycle = Cycle("blocked", ioNum)  # needs random
                    process.cycles.append(cycle)
                    processArray.append(process)
                else:
                    process.C -= 1
                    cycle = Cycle("running", previousCycle.num - 1)
                    process.cycles.append(cycle)
                    newQueue.append(process)
                    runningProcess = process
                continue

            if busy:
                cycle = Cycle("ready", 0)
                process.cycles.append(cycle)
                newQueue.append(process)
            else:
                if cpuNum == 0:
                    cpuNum = randomOS(randomNumbers, process.B, process.C)
                busy = True
                cycle = Cycle("running", cpuNum)  # needs random
                process.cycles.append(cycle)
                newQueue.append(process)
                runningProcess = process
        queue = newQueue
        currentCycle += 1

    # deletes extra line (used to make sure all processes have terminated)
    for process in processArray:
        del process.cycles[-1]

    processArray.sort(key=lambda x: x.originalIndex)

    # print output
    print("The original input was: {0}  {1}".format(len(processArray), str('  '.join(originalProcessArray))))
    print("The sorted input is: {0}  {1}".format(len(processArray), str('  '.join(sortedProcessArray))))
    printOutput(processArray, sortedProcessArray, "Shortest Job First", verbose)


arguments = sys.argv
if arguments[1] == "--verbose":
    verbose = True
    arrayArg = arguments[2]
    algo = arguments[3]
else:
    verbose = False
    arrayArg = arguments[1]
    algo = arguments[2]
array = readFile(arrayArg)
if algo == "fcfs":
    randomNumbers = open("random-numbers.txt", "r")
    fcfs(randomNumbers, array, verbose)
    randomNumbers.close()
elif algo == "rr":
    randomNumbers = open("random-numbers.txt", "r")
    roundRobin(randomNumbers, array,verbose, 2)
    randomNumbers.close()
elif algo == "uni":
    randomNumbers = open("random-numbers.txt", "r")
    uni(randomNumbers, array,verbose)
    randomNumbers.close()
elif algo == "sjf":
    randomNumbers = open("random-numbers.txt", "r")
    sjf(randomNumbers, array,verbose)
    randomNumbers.close()
else:
    print("Please enter a valid algorithm.")



