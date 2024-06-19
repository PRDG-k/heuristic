import os
import pandas as pd

if os.getcwd() == "heuristic":
    current_directory = os.getcwd()
    parent_directory = os.path.dirname(current_directory)
else:
    current_directory = os.getcwd()
    parent_directory = os.path.dirname(current_directory)
    parent_directory = os.path.dirname(parent_directory)


def import_opt_sol():
    # 최적해 정보 불러오기
    import_directory = parent_directory + "/Data/l2/out/"
    folder_directory = "multiobj/"
    file_name = "scheduling_multiobj.csv"
    type_spec = {'charge': 'float',
                'discharge': 'float',
                'period': 'int'}
    
    file_directory = import_directory + folder_directory + file_name

    #period~>288마다 하루, 1440시 지나면 다른 버스 period 시작
    optimal_solution = pd.read_csv(file_directory,dtype=type_spec)

    return optimal_solution

def import_args():
    args = {}
    with open("args.txt", 'r') as file:
        for line in file:
            parts = line.strip().split(' ')

            key = parts[0]
            items = parts[1]
            args[key] = items
    
    return args

def open_schedule_se(file_directory):
    schedule = {}

    with open(file_directory, 'r') as file:
        for line in file:
            parts = line.strip().split(',')

            key = parts[0]
            items = parts[1:]
            # schedule[key] = items
            schedule[key] = sorted(items[::2], key=lambda x: int(x))
    return schedule

def extract_head(schedule):
    head = []
    for bus, sch in schedule.items():
        temp = []
        i = 1
        for d in sch:
            if 288 * (i-1) <= int(d) & int(d) <= 288 * i:
                temp.append(d)
            else:
                i = i + 1
                head.append(temp)
                temp = []
                temp.append(d)
        if len(temp) != 0:
            head.append(temp)
            
    return head


def import_price():
    # 가격 데이터 불러오기
    file_name = "ePrice.csv"
    import_directory = parent_directory + "/Data/l2/out/sum/" + file_name

    e_price = pd.read_csv(import_directory)

    file_name = "sPrice.csv"
    import_directory = parent_directory + "/Data/l2/out/sum/" + file_name

    s_price = pd.read_csv(import_directory)

    return e_price, s_price

def open_schedule_range(file_directory):
    
    schedule = {}

    with open(file_directory, 'r') as file:
        for line in file:
            parts = line.strip().split(" ")
             
            key = parts[0]
            items = parts[1:]
            schedule[key] = sorted(items, key=lambda x: int(x))
            
    return schedule
