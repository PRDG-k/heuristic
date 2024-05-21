import os
import pandas as pd

current_directory = os.getcwd()
parent_directory = os.path.dirname(current_directory)

def import_args():
    args = {}
    with open("args.txt", 'r') as file:
        for line in file:
            parts = line.strip().split(' ')

            key = parts[0]
            items = parts[1]
            args[key] = items

    return args

def import_bus_schedule(seed):
    # 버스 운행 정보 불러오기
    import_directory = parent_directory + "/Data/l1/out/" + seed
    file_name = "/schedule_range.txt"

    schedule = {}
    charge_finished = {}

    with open(import_directory + file_name, 'r') as file:
        for line in file:
            parts = line.strip().split(' ')

            key = parts[0]
            items = parts[1:]
            # schedule[key] = items
            schedule[key] = sorted(items, key=lambda x: int(x))
            
            charge_finished[key] = {False}
    
    return schedule, charge_finished

def check_bus_type(n):
    capa = {'day_bus' : 250,
            'n_bus' : 350}
    if n[0] == "1":
        return capa['day_bus']
    else:
        return capa['n_bus']

def init_tzero(bus_list):
    solution = {}
    solution['bus'] = [n for n in bus_list]
    solution['period'] = [0 for _ in bus_list]
    solution['charge'] = [0 for _ in bus_list]
    solution['discharge'] = [0 for _ in bus_list]
    solution['consumption'] = [0 for _ in bus_list]
    solution['SOC'] = [check_bus_type(n) for n in bus_list]
    solution = pd.DataFrame(solution)

    return solution

# 충전소 데이터 불러오기
# import_directory = parent_directory + "/Data/l2/out/"
# file_name = "prob_info.csv"
# prob_info = pd.read_csv(import_directory + file_name)


def import_price():
    # 가격 데이터 불러오기
    file_name = "ePrice.csv"
    import_directory = parent_directory + "/Data/l2/out/sum/" + file_name

    e_price = pd.read_csv(import_directory)

    file_name = "sPrice.csv"
    import_directory = parent_directory + "/Data/l2/out/sum/" + file_name

    s_price = pd.read_csv(import_directory)

    return e_price, s_price