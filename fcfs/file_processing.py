import os
import pandas as pd
from fcfs_module import peak
import time

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
    capa = {'day_bus' : 200,
            'n_bus' : 300}
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

def calc_shaving(df):
    amount = 0
    for row in df.itertuples():
        if row.period in peak:
            amount += row.discharge
            amount -= row.charge
    return amount

def calc_penalty(df):
    require_energy = 0
    capa = {'day_bus' : 250,
            'n_bus' : 350}
    
    df['departure'] = df['consumption'].shift(1) != df['consumption']

    # 값이 바뀌는 순간을 가지는 행만 선택
    change_points = df[df['departure']]
    change_points = change_points[::2]

    for row in change_points.itertuples():
        if row.bus[0] == '1':
            if row.SOC < capa['day_bus'] * 0.7:
                require_energy += (capa['day_bus'] * 0.7 - row.SOC)
            else:
                pass
            
        else:
            if row.SOC < capa['n_bus'] * 0.7:
                require_energy += (capa['n_bus'] * 0.7 - row.SOC)
            else:
                pass
    return require_energy

def export_result(_solution, _time, _count):
    e_price, s_price = import_price()

    df1 = _solution.groupby('period').sum()[['charge']]
    df3 = _solution.groupby('period').sum()[['discharge']]

    # new_sol obj
    sell = 0
    buy = 0
    # penalty_cost = 232.5 * penalty_amount
    penalty_amount = calc_penalty(_solution)
    penalty_cost = 121 * penalty_amount

    for i in range(1440):
        sell += df3.iloc[i]['discharge'] * s_price.iloc[i]['price']
        buy += df1.iloc[i]['charge'] * e_price.iloc[i]['price']

    cost = buy - sell + penalty_cost

    shaving_amount = calc_shaving(_solution)

    file_name = "FCFS_RESULT.txt"

    with open(file_name, 'w', encoding="utf-8") as file:
        file.write(f"Objective Function Value: {cost}\n")
        file.write(f"Solving Time: {_time}\n")
        file.write(f"Peak Shaving: {shaving_amount}\n")
        file.write(f"Iteration Count: {_count}\n")


def record_time(st):
    nt = time.time()
    print(f"\n코드 작동 시간: {nt - st:.4f}초")

    return nt