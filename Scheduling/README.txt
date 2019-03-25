Instructions to compile Lab2:

Ensure that you are using Python 2.7.5 (the version on the CIMS server)

Ensure that all input files (1-7) are in the same directory as the Scheduling.py file.

Ensure random-numbers.txt is in the same directory as the Scheduling.py file. 

The proper notation to run the file is:

>python <--verbose> <input-filename> <algorithm>

The possible algorithms are:
fcfs
rr
uni
sjf

respectively, these are First Come First Served, Round Robin, Uniprocessor and Shortest Job First.

Thus to run input-4 with the Round Robin algorithm you would execute one of the following:

>python --verbose input-4 rr
>python input-4 rr

To run input-3 with the Shortest Job First algorithm you would execute one of the following:

>python --verbose input-3 sjf
>python input-3 sjf

In both cases, the latter would give the non-verbose printout. 

