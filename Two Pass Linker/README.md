# Two-Pass-Linker
*Operating Systems Spring 2019*

This python program takes in an input and returns the Symbol Table and Memory Map. 

It resolves the following errors in the following ways:

* If a symbol is multiply defined, print an error message and use the value given in the last definition.
* If a symbol is used but not defined, print an error message and use the value 111.
* If a symbol is defined but not used, print a warning message.
* If an absolute address exceeds the size of the machine, print an error message and use the largest legal value.
* If multiple symbols are listed as used in the same instruction, print an error message and ignore all but the last usage given.
* If a type R address in the list of Text entries exceeds the size of the module, treat the address as 0 (and relocate it since it is of type R).

## Usage

```
> python Two Pass Linker 2.7
```


## Input-Output Example

```
4
1   xy 2
2   xy 4 z 2
5   R 1004  I 5678  E 2777  R 8002  E 7777
0
1   z 3
6   R 8001  E 1777  E 1001  E 3002  R 1002  A 1010
0
1   z 1
2   R 5001  E 4777
1   z 2
1   xy 2
3   A 8000  E 1777  E 2001
```

returns 

```
Symbol Table
xy=2
z=15

Memory Map
0:  1004
1:  5678
2:  2015
3:  8002
4:  7002
5:  8006
6:  1015
7:  1015
8:  3015
9:  1007
10: 1010
11: 5012
12: 4015
13: 8000
14: 1002
15: 2002
```

## Built with

Python 2.7
