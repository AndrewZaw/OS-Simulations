# Scheduling
*Operating Systems Spring 2019*

This python program takes in a sample process collection and outputs the simulated process scheduling.

It supports First Come First Served, Round Robin, Shortest Job First and Uniprocessor.

## Usage

Ensure that all input files (1-7) are in the same directory as the Scheduling.py file.

Ensure random-numbers.txt is in the same directory as the Scheduling.py file. 

The proper notation to run the file is:

```
>python <--verbose> <input-filename> <algorithm>
```
The possible algorithms are:
fcfs
rr
uni
sjf

Respectively, these are First Come First Served, Round Robin, Uniprocessor and Shortest Job First.

Thus to run input-4 with the Round Robin algorithm you would execute one of the following:

>python --verbose input-4 rr
>python input-4 rr

To run input-3 with the Shortest Job First algorithm you would execute one of the following:

>python --verbose input-3 sjf
>python input-3 sjf

In both cases, the latter would give the non-verbose printout. 

## Built with

Python 2.7



