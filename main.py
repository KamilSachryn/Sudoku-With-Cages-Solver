import multiprocessing
import psutil
import math
import time


cutoff_count = 0
cores_to_use = psutil.cpu_count()
cutoff_depth = math.log(cores_to_use, 2)

def print_grid(arr):
    for i in range(9):
        for j in range(9):
            print(arr[i][j],end=" ")
        print("")

def find_empty_location(arr, l):
    for row in range(9):
        for col in range(9):
            if(arr[row][col]== 0):
                l[0]= row
                l[1]= col
                return True
    return False

def used_in_row(arr, row, num):
    for i in range(9):
        if(arr[row][i] == num):
            return True
    return False


def used_in_col(arr, col, num):
    for i in range(9):
        if(arr[i][col] == num):
            return True
    return False


def used_in_box(arr, row, col, num):
    for i in range(3):
        for j in range(3):
            if(arr[i + row][j + col] == num):
                return True
    return False

def used_in_cage(arr, row, col, num, cages):

    if cages[row][col] == 0:
        return False
    for i in range(9):
        for j in range(9):
            if cages[i][j] == cages[row][col] and arr[i][j] == num:
                return True
    return False

def adj_used_orthogonally(arr, row, col, num):
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            if bool(i == 0) ^ bool(j == 0):
                if -1 < row + i < 9 and -1 < col + j < 9:
                    curr = arr[row+i][col+j]
                    if curr != 0 and (curr == num + 1 or curr == num - 1):
                        return True
    return False

def check_location_is_safe(arr, row, col, num, cages):
    return not used_in_row(arr, row, num) and not\
        used_in_col(arr, col, num) and not \
        used_in_box(arr, row - row % 3,col - col % 3, num) and not \
        adj_used_orthogonally(arr, row, col, num) #and not \
        #used_in_cage(arr, row,col,num, cages)

def solve_sudoku(arr, cages, level, cutoff_count, id):

    if level == cutoff_depth:
        cutoff_count += 1
        if(cutoff_count % cores_to_use != id):
            return False


    l =[0, 0]
    if(not find_empty_location(arr, l)):
        return True

    row = l[0]
    col = l[1]

    for num in range(1, 10):
        if(check_location_is_safe(arr, row, col, num, cages)):
            arr[row][col]= num
            if(solve_sudoku(arr, cages, level + 1, cutoff_count, id)):
                if level == 0:
                    print_grid(arr)
                return True
            arr[row][col] = 0
    return False

def set_affinity_and_run(arr, cages, level, cutoff_count, id):
    psutil.Process().cpu_affinity([id])
    solve_sudoku(arr, cages, level, cutoff_count, id)

if __name__=="__main__":

    startTime = time.time()
    grid =[[0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0],
           [0,0,0,2,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0]]


    cages =[[1,1,1, 4,4,4 ,6,6,6],
            [1,0,2, 4,5,4, 6,7,6],
            [1,1,2, 4,5,6, 6,7,7],

            [1,1,2, 4,5,5, 6,0,7],
            [2,2,2, 4,4,5, 5,8,7],
            [2,0,2, 2,9,0, 9,8,7],

            [3,3,3, 3,9,9, 9,8,8],
            [3,0,3, 0,9,0, 9,8,8],
            [3,0,3, 9,9,0, 8,8,8]]


    #solve_sudoku(grid, cages, 0,0,0)

    threads = list()
    for i in range(cores_to_use):
        threads.append(multiprocessing.Process(target=set_affinity_and_run, args=(grid, cages, 0,0,i)))

    for i in threads:
        i.start()

    for i in threads:
        i.join()
