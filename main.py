import numpy as np
import random
import time
import math
import os
import tkinter as tk

def drawCanvas(canvas, matrix, size):
    
    for (x,y), value in np.ndenumerate(matrix):  
        if value == 4:
            # flat
            rect(canvas, size, (x, y), (x+1, y+1),'white')
        if value == 3:
            # hilly
            rect(canvas, size, (x, y), (x+1, y+1),'#A0A0A0')
        if value == 2:
            # forested
            rect(canvas, size, (x, y), (x+1, y+1),'green')
        if value == 1:
            # maze of caves
            rect(canvas, size, (x, y), (x+1, y+1),'#202020') 
        if value == 0:
            # searching
            rect(canvas, size, (x, y), (x+1, y+1),'blue')
        if value == -1:
            # target
            canvas.create_text((size*(2*x + 1)/2, size*(2*y + 1)/2), text='X',fill='red',font="Helvetica 10 bold")
    #tk.Button(self.root, text="Quit", command=quit).pack()   
    #self.root.protocol("WM_DELETE_WINDOW", self.on_closing)   
    #self.root.mainloop()

def updateCellInCanvas(canvas, size, value, y, x):
    time.sleep(0.5)
    if value == 4:
        # flat
        rect(canvas, size, (x, y), (x+1, y+1),'white')
    if value == 3:
        # hilly
        rect(canvas, size, (x, y), (x+1, y+1),'#A0A0A0')
    if value == 2:
        # forested
        rect(canvas, size, (x, y), (x+1, y+1),'green')
    if value == 1:
        # maze of caves
        rect(canvas, size, (x, y), (x+1, y+1),'#202020')
    if value == 0:
        # searching
        rect(canvas, size, (x, y), (x+1, y+1),'blue')
    if value == -1:
        # target
        canvas.create_text((size*(2*x + 1)/2, size*(2*y + 1)/2),text='X',fill='red',font="Helvetica " + str(size-2) + " bold")
    canvas.update_idletasks()
    canvas.update()
    time.sleep(0.05)
    #tk.Button(self.root, text="Quit", command=quit).pack()   
    #self.root.protocol("WM_DELETE_WINDOW", self.on_closing)   
    #self.root.mainloop()
   

def rect(canvas, size, a, b, color='black'):
    (x1, y1) = a
    (x2, y2) = b
    x1 *= size
    y1 *= size
    x2 *= size
    y2 *= size
    canvas.create_rectangle((x1, y1, x2, y2), fill=color)
    canvas.update_idletasks()


def populateCell(probFlat, probHill, probForest, probCave):
    probFalseFlat = 0.1
    probFalseHill = 0.3
    probFalseForest = 0.7
    probFalseCave = 0.9
    flatHillProb = (probFlat + probHill)
    flatHillForestProb = (flatHillProb + probForest)
    chooserandom = random.uniform(0, 1)
    if chooserandom < probFlat:
        return 4, probFalseFlat
    elif probFlat <= chooserandom and chooserandom < flatHillProb:
        return 3, probFalseHill
    elif flatHillProb <= chooserandom and chooserandom < flatHillForestProb:
        return 2, probFalseForest
    else:
        return 1, probFalseCave


def createGrid(dim):
    height = dim
    width = dim
    grid = np.zeros((height, width))
    falseNegMatrix = np.zeros((height, width))
    probFlat = 0.2
    probHill = 0.3
    probForest = 0.3
    probCave = 0.2
    for (x, y), value in np.ndenumerate(grid):
        grid[x][y], falseNegMatrix[x][y] = populateCell(probFlat, probHill, probForest, probCave)
    return grid, falseNegMatrix


def getTarget(grid):
    height, width = np.shape(grid)
    x = random.sample(range(width), 1).pop()
    y = random.sample(range(height), 1).pop()
    return x, y


def isFalseNegative(probFalse):
    if random.uniform(0, 1) < probFalse:
        return True
    else:
        return False


def manhattan(a, b):
    a_x, a_y = a;
    b_x, b_y = b;

    return math.fabs(a_x - b_x) + math.fabs(a_y - b_y)


def GetSurroundingContent(row, col, grid):
    rows, cols = np.shape(grid)
    neighboringCells = []

    if (row >= 1):
        # add north edge to the selected cell
        neighboringCells.append((row - 1, col))
    if (row < rows - 1):
        # add south edge to the selected cell
        neighboringCells.append((row + 1, col))
    if (col >= 1):
        # add west edge to the selected cell
        neighboringCells.append((row, col - 1))
    if (col < cols - 1):
        # add east edge to the selected cell
        neighboringCells.append((row, col + 1))

    return neighboringCells


def GetSurroundingSumOfType(type, row, col, grid):
    rows, cols = np.shape(grid)
    neighboringCells = []
    number = 0
    if (row >= 1 and grid[row - 1][col] == type):
        # add north edge to the selected cell
        neighboringCells.append((row - 1, col))
        number = number + 1
    if (row < rows - 1 and grid[row + 1][col] == type):
        # add south edge to the selected cell
        neighboringCells.append((row + 1, col))
        number = number + 1
    if (col >= 1 and grid[row][col - 1] == type):
        # add west edge to the selected cell
        neighboringCells.append((row, col - 1))
        number = number + 1
    if (col < cols - 1 and grid[row][col + 1] == type):
        # add east edge to the selected cell
        neighboringCells.append((row, col + 1))
        number = number + 1

    return neighboringCells, number


def ChooseNextCell(x, y, target_x, target_y, grid, beliefMatrix):
    # target_x, target_y is the absolute max belief cell (where we would go in one jump, if we could)
    # first pick neighbors with minimum cost
    neighborcells = GetSurroundingContent(x, y, grid)
    cost = []
    for cell in neighborcells:
        cost.append((cell, manhattan((target_x, target_y), cell)))

    min_cost_cell, min_cost = min(cost, key=lambda t: t[1])
    min_cost_list = [x for x in cost if x[1] == min_cost]
    # then select the cell(s) with max belief (out of the min cost cell(s))
    belief = []
    for item in min_cost_list:
        cell, cost = item
        i, j = cell
        belief.append((cell, beliefMatrix[i][j]))

    # Take one of the max belief cells (with min cost)
    max_belief_cell, max_belief = max(belief, key=lambda t: t[1])
    x, y = max_belief_cell

    return x, y


def MoveTarget(target_x, target_y, grid):
    neighbors = GetSurroundingContent(target_x, target_y, grid)
    cell1 = 0.25
    cell2 = 0.5
    cell3 = 0.75
    if (len(neighbors) == 4):
        chooserandom = random.uniform(0, 1)
    elif (len(neighbors) == 3):
        chooserandom = random.uniform(0, 0.75)
    elif (len(neighbors) == 2):
        chooserandom = random.uniform(0, 0.5)
    else:
        chooserandom = random.uniform(0, 0.25)

    if chooserandom < cell1:
        # return new target and type 1 and type 2
        x = neighbors[0][0]
        y = neighbors[0][1]

    elif cell1 <= chooserandom and chooserandom < cell2:
        # return new target and type 1 and type 2
        x = neighbors[1][0]
        y = neighbors[1][1]

    elif cell2 <= chooserandom and chooserandom < cell3:
        # return new target and type 1 and type 2
        x = neighbors[2][0]
        y = neighbors[2][1]

    else:
        # return new target and type 1 and type 2
        x = neighbors[3][0]
        y = neighbors[3][1]


    return x, y, grid[target_x][target_y], grid[x][y]


def UpdateBeliefMatrix(type1, type2, grid, beliefMatrix):
    height, width = np.shape(beliefMatrix)
    numberOfMovement = np.zeros((height, width))
    copyBeliefMatrix = np.copy(beliefMatrix)
    for i in range(width):
        for j in range(height):
            sumoftype = 0
            if (grid[i][j] == type1):
                neighbors, sumoftype = GetSurroundingSumOfType(type2, i, j, grid)
            elif (grid[i][j] == type2):
                neighbors, sumoftype = GetSurroundingSumOfType(type1, i, j, grid)
            numberOfMovement[i][j] = sumoftype

    for i in range(width):
        for j in range(height):
            if (numberOfMovement[i][j] > 0):
                if (grid[i][j] == type1):
                    neighbors, sumoftype = GetSurroundingSumOfType(type2, i, j, grid)
                    sumofprob = 0
                    for k in range(sumoftype):
                        nx = neighbors[k][0]
                        ny = neighbors[k][1]
                        probabilityOfPreviousCell = copyBeliefMatrix[nx][ny]
                        sumofprob = sumofprob + (probabilityOfPreviousCell * (1 / numberOfMovement[nx][ny]))

                elif (grid[i][j] == type2):
                    neighbors, sumoftype = GetSurroundingSumOfType(type1, i, j, grid)
                    sumofprob = 0
                    for k in range(sumoftype):
                        nx = neighbors[k][0]
                        ny = neighbors[k][1]
                        probabilityOfPreviousCell = copyBeliefMatrix[nx][ny]
                        sumofprob = sumofprob + (probabilityOfPreviousCell * (1 / numberOfMovement[nx][ny]))
                beliefMatrix[i][j] = sumofprob
                # else:
                # beliefMatrix[i][j]=0
    for i in range(width):
        for j in range(height):
            if (numberOfMovement[i][j] == 0):
                beliefMatrix[i][j] = 0
    #print(beliefMatrix)
    return beliefMatrix


def findTarget(grid, target_x, target_y, beliefMatrix, rule, falseNegMatrix, onlyMoveToNeighbor, isMovingTarget,canvasGenerated,cellsize):
    visited = 0
    # algorithm goes here
    #     probFalseFlat = 0.1
    #     probFalseHill = 0.3
    #     probFalseForest = 0.7
    #     probFalseCave = 0.9
    # choose random cell to search
    height, width = np.shape(grid)
    first = True
    if (first):
        x = random.sample(range(width), 1).pop()
        y = random.sample(range(height), 1).pop()
    first = False

    while True:

        falseNegative = isFalseNegative(falseNegMatrix[x][y])
        if (not falseNegative and (target_x == x and target_y == y)):
            return True, visited, target_x, target_y

        probFalseNeg = falseNegMatrix[x][y]
        beliefMatrix[x][y] = beliefMatrix[x][y] * (probFalseNeg)
        beta = 1 / np.sum(np.sum(beliefMatrix))
        beliefMatrix = beta * beliefMatrix

        if (isMovingTarget):
            #target move without any information about direction only the type given
            target_x, target_y, type1, type2 = MoveTarget(target_x, target_y, grid)
            beliefMatrix = UpdateBeliefMatrix(type1, type2, grid, beliefMatrix)
            updateCellInCanvas(canvasGenerated, cellsize, -1, target_x, target_y)

        if rule == 0:
            # random
            next_x = random.sample(range(width), 1).pop()
            next_y = random.sample(range(height), 1).pop()
        elif rule == 1:
            # rule 1
            xrange, yrange = np.where(beliefMatrix == beliefMatrix.max())  # select cells with maximum belief
            idx = random.sample(range(xrange.size), 1).pop()  # select one of the maximum belief cells at random
            next_x = xrange[idx]
            next_y = yrange[idx]
        else:
            #rule 2
            beliefMatrix = np.multiply(beliefMatrix, 1 - falseNegMatrix)
            xrange, yrange = np.where(beliefMatrix == beliefMatrix.max())  # select cells with maximum belief
            idx = random.sample(range(xrange.size), 1).pop()  # select one of the maximum belief cells at random
            next_x = xrange[idx]
            next_y = yrange[idx]
        if (onlyMoveToNeighbor):
            #part 1 question 4
            #only can move to neighbour cell
            next_x, next_y = ChooseNextCell(x, y, next_x, next_y, grid, beliefMatrix)
        updateCellInCanvas(canvasGenerated, cellsize, 0, next_x, next_y)
        x = next_x
        y = next_y
        visited += 1
    return False


if __name__ == '__main__':
    dim = int(input("What is the size of the grid? "))
    timesToRun = int(input("How many results should be generated? "))
    target = input("Stationary (S) or moving (M) target? ")
    if (target == 'S'):
        isMovingTarget = False  # PART 1
    else:
        isMovingTarget = True  # PART 2
    onlyMoveToNeighbor = False #default if PART 2
    if (target == 'S'):
        moveToNeighbor = input("Only move to neighbor (Y or N)? ")
        if (moveToNeighbor == 'Y'):
            onlyMoveToNeighbor = True  # PART 1 q4
        else:
            onlyMoveToNeighbor = False  # NOT PART 1 q4
    rulename = input("Rule1 or Rule2 or Random? ")
    if (timesToRun > 1):
        file = input("Custom file (Y or N)? ")
        if file == 'Y':
            filename = input("Enter output file name: ")
            filename = "results/" + filename
        else:
            filename = "results/results.csv"
        try:
            os.remove(filename)
        except OSError:
            pass
        with open(filename, "w") as resultsFile:
            resultsFile.write("Rule, Cell Type, Time (s), Number of Searches\n")
    i = 0
    while (i < timesToRun):
        print("-------Iteration #" + str(i + 1) + "---------")
        grid, falseNegMatrix = createGrid(dim)
        height, width = np.shape(grid)
        if(timesToRun == 1):
            cellsize = (int) (625/max((height, width)));
            master = tk.Tk();
            master.title("Map")
            canvasGenerated = tk.Canvas(master, width = width*cellsize, height = height*cellsize)
            canvasGenerated.grid(row=0, column=0)
            drawCanvas(canvasGenerated, np.transpose(grid), cellsize)
        beliefMatrix = np.ones((height, width)) * (1 / (height * width))
        cellsize = (int)(625 / max((height, width)));
        isRule1 = True
        if rulename == 'Rule1':
            rule = 1
        elif rulename == 'Random':
            rule = 0
        elif rulename == 'Rule2':
            rule = 2  # Rule 2
        else:
            print('Unknown rule. Error.')
            break
        target_x, target_y = getTarget(grid)
        print("Target location: (" + str(target_x) + ", " + str(target_y) + "), cell type: " + str(
            grid[target_x][target_y]))
        print("Finding...")
        start = time.time()
        success, visited, target_x, target_y = findTarget(grid, target_x, target_y, beliefMatrix, rule, falseNegMatrix,
                                                          onlyMoveToNeighbor, isMovingTarget,canvasGenerated,cellsize)
        if (success):
            end = time.time() - start
            s = rulename + ', ' + str(grid[target_x][target_y]) + ',' + str(end) + ',' + str(visited) + '\n'
            if(timesToRun > 1):
                with open(filename, "a") as resultsFile:
                    resultsFile.write(s)
            print("Target found at (" + str(target_x) + ", " + str(target_y) + "), cell type: " + str(
                grid[target_x][target_y]) + "\nTime: " + str(end) + " seconds\nVisited: " + str(visited))
            if(timesToRun == 1):
                updateCellInCanvas(canvasGenerated, cellsize, -1, target_x, target_y)
        else:
            print("Could not find target.")
        if (i + 1 == timesToRun):
            break
        i += 1
    if(timesToRun > 1):
        with open(filename, "a") as resultsFile:
            resultsFile.write("\n\n\nCell Type, Average Number of Searches, Standard Deviation (ctrl+shift+enter on formula bar for each cell to calculate)\n")
            resultsFile.write('Cave' + ',"=AVERAGEIFS($D$2:$D$' + str(1 + timesToRun) + ', $B$2:$B$' + str(
                1 + timesToRun) + ', 1")' + ',"=STDEV(IF($B$2:$B$' + str(1 + timesToRun) + '=1,$D$2:$D$' + str(
                1 + timesToRun) + '"))\n')
            resultsFile.write('Forest' + ',"=AVERAGEIFS($D$2:$D$' + str(1 + timesToRun) + ', $B$2:$B$' + str(
                1 + timesToRun) + ', 2")' + ',"=STDEV(IF($B$2:$B$' + str(1 + timesToRun) + '=2,$D$2:$D$' + str(
                1 + timesToRun) + '"))\n')
            resultsFile.write('Hill' + ',"=AVERAGEIFS($D$2:$D$' + str(1 + timesToRun) + ', $B$2:$B$' + str(
                1 + timesToRun) + ', 3")' + ',"=STDEV(IF($B$2:$B$' + str(1 + timesToRun) + '=3,$D$2:$D$' + str(
                1 + timesToRun) + '"))\n')
            resultsFile.write('Flat' + ',"=AVERAGEIFS($D$2:$D$' + str(1 + timesToRun) + ', $B$2:$B$' + str(
                1 + timesToRun) + ', 4")' + ',"=STDEV(IF($B$2:$B$' + str(1 + timesToRun) + '=4,$D$2:$D$' + str(
                1 + timesToRun) + '"))\n')
            resultsFile.write("\n\n\nTotal Weighted Average Searches\n=(0.2*$B$" + str(6 + timesToRun) + ") + (0.3*$B$" + str(7 + timesToRun) + ") + (0.3*$B$" + str(8 + timesToRun) + ") + (0.2*$B$" + str(9 + timesToRun) + ")")
        print(str(timesToRun) + " results generated to " + filename + ".")
    quitProgram = input("Press Enter to exit program.")
    if(timesToRun == 1):
        master.destroy()