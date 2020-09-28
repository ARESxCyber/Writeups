# Minesweeper

> Category: Misc
> Description: ```I'm lucky to be surrounded by even-minded people from all around. Flag is not in the regular format.
Submit flag in darkCTF{flag} format.```

# Analysis

From the provided file we have an array of arrays (matrix) and the challenge name points us to `Minesweeper` (I'm going to assume you know what 
this game is, if not please check this out https://www.microsoft.com/en-us/p/minesweeper-free/9wzdncrdk4km?activetab=pivot:overviewtab ).


```
I'am lucky to be surrounded by even-minded people from all directions.
Flag is not in the regular format.
array = [[93, 91, 95,... 71], [83, 89, 73, ..., 69], ... ]
```

So, it's pretty obvious this is not a coincidence, also from the description you read that 'surrounded by even-minded people', this called my attention and my initial though was that this was the 'bomb' condition.

So, I would have to find all cells that are fully surrounded by even numbers? Those then would be converte to ascii and hopefully I get something.
This was the thought process, although you'd have to 'guess' the logic, it's kind of obvious in my opinion (save time, agree with me).


# Solve

I removed all text from minesweeper file and left only the `array = [` instruction, that way I can just load that to python (lazy I know, but works)


```python

with open('minesweeper', 'r') as fd:
    line = fd.readline()
    while line:        
        exec(line)
        line = fd.readline()

arr = []

for x in range(len(array)):    
    print('Processing row {}'.format(x))

    if x == 0 or x == len(array) - 1:
        print('Skipping row {}'.format(x))
        continue
    
    for y in range(len(array[x])):    
        print('Processing column {}'.format(y))

        if y == 0 or y == len(array[x]) - 1:
            print('Skipping cell {},{}'.format(x,y))
            continue
        
        up = x - 1
        down = x + 1
        left = y - 1
        right = y + 1

        if array[up][y] % 2 == 0 and array[down][y] % 2 == 0 and array[x][left] % 2 == 0 and array[x][right] % 2 == 0 \
            and array[up][left] % 2 == 0 and array[up][right] % 2 == 0 and array[down][left] % 2 == 0 and array[down][right] % 2 == 0:           
            # surrounded by even-minded cells, I must be relevant
            arr.append(array[x][y])

print(arr)
```

```
... # several debug lines ommitted
Processing column 39
Skipping cell 50,39
Processing row 51
Skipping row 51
FLaGISYOUHaVEOBSERVaTIONaNDPaTIENCE
```

From the found text the flag was `darkCTF{YOUHaVEOBSERVaTIONaNDPaTIENCE}`.
