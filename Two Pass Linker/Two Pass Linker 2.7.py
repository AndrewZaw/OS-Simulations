def TwoPassLinker(text):
    
    # modifies text input to a workable format
    array = text.split()
    for i in range(len(array)):
        if array[i].isdigit():
            array[i] = int(array[i])

    modules = array[0]
    currentIndex = 1
    definitions = {}
    programText = []
    offset = 0
    # first pass
    for i in range(modules):
    
        # definition line
        n = array[currentIndex]
        currentIndex += 1
        for j in range(n):
            
            # Error
            if array[currentIndex] in definitions:
                print("ERROR: Symbol {} multiply defined.".format(array[currentIndex]))
                
            definitions[array[currentIndex]] = array[currentIndex+1] + offset
            currentIndex += 2

        # use line
        n = array[currentIndex]
        currentIndex += 1 + 2*n

        # program text
        n = array[currentIndex]
        offset += n
        currentIndex += 1
        temp = []
        for j in range(n):
            temp.append(array[currentIndex:currentIndex+2])
            currentIndex += 2
        programText.append(temp)
        
    currentIndex = 1
    offset = 0
    usedSymbols = []
    secondPassCounter = 0
    # second pass
    for i in range(modules):
        
        # definition line
        n = array[currentIndex]
        currentIndex += 1 + 2*n

        # use line
        n = array[currentIndex]
        currentIndex += 1
        changedElements = [False] * (len(programText[i]))
        for j in range(n):
            num = programText[i][array[currentIndex+1]][1]
            lastThree = num % 1000
            symbol = array[currentIndex]
            defined = True
            
            # Error
            if symbol not in definitions:
                replace = 111
                defined = False
            else:
                usedSymbols.append(symbol)
                replace = definitions[symbol]

            replaceIndex = array[currentIndex+1]
            while(lastThree != 777):
                if changedElements[replaceIndex] is not False:
                    if changedElements[replaceIndex] == 777:
                        num = num - lastThree + 777
                        lastThree = 777
                        break;
                    print("ERROR: Multiple Symbols used at Memory Map line {}".format(replaceIndex+offset))
            
                changedElements[replaceIndex] = True
                if not defined:
                    print("ERROR: Symbol {} used at Memory Map line {} but not defined.".format(symbol,replaceIndex+offset))
                num = num - lastThree + replace
                programText[i][replaceIndex][1] = num
                replaceIndex = lastThree
                num = programText[i][lastThree][1]
                lastThree = num % 1000
                
            if changedElements[replaceIndex] is not False:
                print("ERROR: Multiple Symbols used at Memory Map line {}".format(replaceIndex+offset))
            changedElements[replaceIndex] = 777
            num = num - lastThree + replace
            programText[i][replaceIndex][1] = num
            if not defined:
                    print("ERROR: Symbol {} used at Memory Map line {} but not defined.".format(symbol,replaceIndex+offset)) #problem here
            currentIndex += 2
            
            
        # definition line
        n = array[currentIndex]
        currentIndex += 1 + n*2
        for j in range(n):
            letter = programText[i][j][0]
            address = programText[i][j][1]
            if letter == "R":
                programText[i][j][1] += offset
                if programText[i][j][1] % 1000 > len(programText[i])-1:
                    print("ERROR: Relative Address {} used at Memory Map line {} exceeds size of the machine.".format(address,secondPassCounter))
                    programText[i][j][1] -= address % 1000
                    
            elif letter == "A":
                if address % 1000 > 299:
                    print("ERROR: Absolute Address {} used at Memory Map line {} exceeds size of the machine.".format(address,secondPassCounter))
                    programText[i][j][1] -= address % 1000
                    programText[i][j][1] += 299
            secondPassCounter += 1
        offset += n

    # Printing everything
    print("\nSymbol Table:")
    printDictionary(definitions)
    print("\nMemory Map:")
    printMemoryMap(programText)
    print("\n")
    for key,value in definitions.items():
        if key not in usedSymbols:
            print("WARNING: {} symbol defined but not used.".format(key))
        
    return

# Takes User Input
def takeInput():
    print("Type input below.\n"
          "Press Ctrl + D to enter input.")
    text = []
    try:
        while True:
            text.append(raw_input())
    except EOFError:
        pass
    text = " ".join(text)
    return text

# Prints a Dictionary
def printDictionary(dictionary):
    for key,value in dictionary.items():
        print ("{}: {}".format(key,value))

# Prints the Memory Map
def printMemoryMap(map1):
    counter = 0
    for module in map1:
        for pair in module:
            print("{}: {}".format(counter,pair[1]))
            counter += 1    

text = takeInput()
TwoPassLinker(text)
