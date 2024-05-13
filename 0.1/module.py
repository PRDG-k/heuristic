import pandas as pd
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib import rc
rc("font", family='AppleGothic')


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

def create_mean_distance_list(label):
    mean_distance_list = []
    for i in range(150):
        _sum = 0
        for ele in label[i]:
            _sum = _sum + int(ele)
        _avg = _sum / len(label[i])
        _list = [int(x) - _avg for x in label[i]]
        mean_distance_list.append(_list)

    return mean_distance_list

import math

def cosine_similarity(vec1, vec2):
    dot_product = sum(x * y for x, y in zip(vec1, vec2))
    norm_vec1 = math.sqrt(sum(x ** 2 for x in vec1))
    norm_vec2 = math.sqrt(sum(y ** 2 for y in vec2))
    
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0 
    return dot_product / (norm_vec1 * norm_vec2)

def open_schedule_range(file_directory):
    schedule = {}

    with open(file_directory, 'r') as file:
        for line in file:
            parts = line.strip().split(" ")
             
            key = parts[0]
            items = parts[1:]
            schedule[key] = sorted(items, key=lambda x: int(x))
            
    return schedule

def extract_range(schedule):
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

def calculate_similarity(new, comparison, method):
    mdcs_list = []
    if method == "cosine":
        for i in range(len(new)):
            temp = []
            for j in range(len(comparison)):
                similarity = cosine_similarity(new[i], comparison[j])
                temp.append(similarity)
            mdcs_list.append(temp)
    return mdcs_list


# 후보들 중 하나 선택(유사도 95 이상)
def extract_candidates(compared_sim):
    candid_index_list = []
    for item in compared_sim:
        key = 0
        candidates = []
        for x in item:
            if x >= 0.95:
                candidates.append(key)
            key = key + 1
        
        if len(candidates) == 0:
            candidates.append(-1)
        
        candid_index_list.append(candidates)
    
    return candid_index_list

def period_check(sch):
    s = int(sch[0])
    return (s // 288)

def count_using_port(row):
    if (row['charge'] >= 0.41666) | (row['discharge'] >= 0.41666):
        return 2
    elif ((row['charge'] < 0.41666) & (row['charge'] > 0)) | ((row['discharge'] < 0.41666) & (row['discharge'] > 0)):
        return 1
    else:
        return 0

def count_using_charger(row):
    if row['port_count'] != 0:
        return 1
    else:
        return 0

def reform_schedule(row):
    if row['consumption'] == 0:
        return 'x'
    else:
        return 'o'
    
def check_peak(row):
    peak = ([i for i in range(97, 145)] + [i  for i in range(156, 265)] +
            [i + 288 for i in range(97, 145)] + [i + 288  for i in range(156, 265)] +
            [i + 288*2 for i in range(97, 145)] + [i + 288*2  for i in range(156, 265)] +
            [i + 288*3 for i in range(97, 145)] + [i + 288*3  for i in range(156, 265)] +
            [i + 288*4 for i in range(97, 145)] + [i + 288*4  for i in range(156, 265)])
    if row['period'] in peak:
        return True
    else:
        return False
    
def peak_no_charge(row):
    peak = ([i for i in range(97, 145)] + [i  for i in range(156, 265)] +
            [i + 288 for i in range(97, 145)] + [i + 288  for i in range(156, 265)] +
            [i + 288*2 for i in range(97, 145)] + [i + 288*2  for i in range(156, 265)] +
            [i + 288*3 for i in range(97, 145)] + [i + 288*3  for i in range(156, 265)] +
            [i + 288*4 for i in range(97, 145)] + [i + 288*4  for i in range(156, 265)])
    if row['period'] in peak:
        return 0
    else:
        return row['charge']
    
def unseize_port(row):
    if (row['charge'] == 0) & (row['discharge'] == 0):
        return 0
    else:
        return row['port_count']
    
def unseize_charger(row):
    if (row['charge'] == 0) & (row['discharge'] == 0):
        return 0
    else:
        return row['charger_count']
    
def sorting(df):
    return df.sort_values(by = ['bus', 'period'])

def releveling(df):
    grouped = df.groupby('bus')

    soc = []

    capa = {'day_bus' : 250,
            'n_bus' : 350}

    # 각 그룹을 반복하며 'level' 계산
    for bus, group in grouped:
        if bus[0] == '1':
            level = capa['day_bus'] - 50
        else:
            level = capa['n_bus'] - 50
        group = group.sort_values(by=["bus", 'period'])  # 'period' 기준으로 정렬
        
        # 'level'을 계산하면서 업데이트
        for row in group.itertuples():
            level = level + row.charge - row.discharge - row.consumption
            soc.append(level)  # 데이터프레임에 'level' 값 업데이트

    return soc

def peak_discharge_restraint(df, max_discharge, ratio):
    _diff  = 0
    required_discharge = max_discharge * ratio
    term_discharge = required_discharge/5
    _bandwidth = 0.416667

    # 'bus' 컬럼을 기준으로 그룹화
    days = [0, 288, 288*2, 288*3, 288*4, 288*5]

    # filt = df['peak'] == True
    # peak_group = df[filt]
    peak_group = df[df['peak']]

    for i in range(1,6):
        filt = (peak_group['period'] <= days[i]) & (peak_group['period'] > days[i-1])
        day_group = peak_group[filt]
        _diff = term_discharge - day_group['discharge'].sum()

        if _diff <0:
            continue

        # 필요한 충전 횟수 계산
        _count = math.ceil(_diff / _bandwidth)

        filt = (day_group['port_count'] == 0) & (day_group['consumption'] == 0)
        available_group = day_group[filt]

        if len(available_group) < _count:
            print(f"NOT ENOUGH RESOURCE TO DISCHARGE, NEED: {_count - len(available_group)}")

        _bus_list = set(available_group['bus'])
        day_bus_discharge = _count / len(_bus_list)
        
        for _n in _bus_list:
            filt = available_group['bus'] == _n
            available_bus = available_group[filt]
            
            day_bus_discharge = min(len(available_bus), day_bus_discharge)

        _dl = []
        _pl = []
        _cl = []

        # 할당
        for i in range(len(available_group)):
            if _count > 0:
                _dl.append(_bandwidth)
                _pl.append(2)
                _cl.append(1)
            else:
                _dl.append(0)
                _pl.append(0)
                _cl.append(0)
                
            _count -= 1

        available_group['discharge'] = _dl
        available_group['port_count'] = _pl
        available_group['charger_count'] = _cl

        new_frame = pd.concat([df, available_group])

        df = new_frame.drop_duplicates(subset=['bus', 'period'], keep='last')

        df = sorting(df)
    
    return df


def rorc_restraint(df):
    # 출력 옵션 설정 - 모든 행을 출력하도록 설정
    pd.set_option('display.max_rows', None)

    capa = {'day_bus' : 250,
            'n_bus' : 350}

    df['departure'] = df['operation'].shift(1) != df['operation']  # True: 값이 바뀜, False: 바뀌지 않음

    # 값이 바뀌는 순간을 가지는 행만 선택
    change_points = df[df['departure']]
    # change_points = change_points[::2]
    change_points = change_points[change_points['operation'] == 'o']

    lack_soc = pd.DataFrame(columns=df.columns)
    rows = []

    for row in change_points.itertuples():
        if row.bus[0] == '1':
            if row.SOC < capa['day_bus'] * 0.7:
                rows.append(row._asdict())
            else:
                pass
            
        else:
            if row.SOC < capa['n_bus'] * 0.7:
                rows.append(row._asdict())
            else:
                pass

    lack_soc = pd.concat([lack_soc,pd.DataFrame(rows)])
    _bus_list = set(lack_soc['bus'])
    _bandwidth = 0.416667

    for _n in _bus_list:
        filt = lack_soc['bus'] == _n
        _bus_soc = list(lack_soc.loc[filt, "SOC"])
        require_energy = 0
        
        for state in _bus_soc:
            if _n[0] == '1':
                require_energy += capa['day_bus'] * 0.7 - state
            else:
                require_energy += capa['day_bus'] * 0.7 - state

        # 필요한 period 수 계산
        _count = math.ceil(require_energy / _bandwidth)

        # filt = (df['bus'] == _n) & (df['peak'] == False) & (df['consumption'] == 0) & ((df['discharge'] > 0) | (df['charger_count'] == 0))
        # filt = (df['bus'] == _n) & (df['peak'] == False) & (df['consumption'] == 0) & (df['charger_count'] == 0)
        filt = (df['bus'] == _n) & (df['peak'] == False) & (df['consumption'] == 0) & (df['charge'] == 0)
        available_group = df[filt]

        if len(available_group) < _count:
            print(f"\nRequired energy: {require_energy}")
            print(f"{_n}, NOT ENOUGH PERIOD TO CHARGE, NEED: {_count - len(available_group)}")

            print('\n---LIST OF AVAILABLE PATCH---\n')
            print(available_group)
            print('\n\n')
            

        _ul = []
        _dl = []
        _pl = []
        _cl = []

        # 할당
        for i in range(len(available_group)):
            if _count > 0:
                _ul.append(_bandwidth)
                _dl.append(0)
                _pl.append(2)
                _cl.append(1)
                _count -= 1
            else:
                _ul.append(0)
                _dl.append(0)
                _pl.append(0)
                _cl.append(0)
                
        available_group['charge'] = _ul
        available_group['discharge'] = _dl
        available_group['port_count'] = _pl
        available_group['charger_count'] = _cl

        new_frame = pd.concat([df, available_group])

        df = new_frame.drop_duplicates(subset=['bus', 'period'], keep='last')

        df = sorting(df)

        pd.reset_option('display.max_rows')

    return df


def rorc_restraint_peak_include(df):
    pd.set_option('display.max_rows', None)
    capa = {'day_bus' : 250,
            'n_bus' : 350}

    df['departure'] = df['operation'].shift(1) != df['operation']  # True: 값이 바뀜, False: 바뀌지 않음

    # 값이 바뀌는 순간을 가지는 행만 선택
    change_points = df[df['departure']]
    change_points = change_points[::2]

    lack_soc = pd.DataFrame(columns=df.columns)
    rows = []

    for row in change_points.itertuples():
        if row.bus[0] == '1':
            if row.SOC < capa['day_bus'] * 0.7:
                rows.append(row._asdict())
            else:
                pass
            
        else:
            if row.SOC < capa['n_bus'] * 0.7:
                rows.append(row._asdict())
            else:
                pass

    lack_soc = pd.concat([lack_soc,pd.DataFrame(rows)])
    _bus_list = set(lack_soc['bus'])
    _bandwidth = 0.416667

    for _n in _bus_list:
        filt = lack_soc['bus'] == _n
        _bus_soc = list(lack_soc.loc[filt, "SOC"])
        require_energy = 0
        
        for state in _bus_soc:
            if _n[0] == '1':
                require_energy += capa['day_bus'] * 0.7 - state
            else:
                require_energy += capa['day_bus'] * 0.7 - state

        # 필요한 period 수 계산
        _count = math.ceil(require_energy / _bandwidth)

        # filt = (df['bus'] == _n) & (df['consumption'] == 0) & ((df['discharge'] > 0) |  (df['charger_count'] == 0))
        filt = (df['bus'] == _n) & (df['consumption'] == 0) & (df['charger_count'] == 0)
        available_group = df[filt]

        if len(available_group) < _count:
            print(f"\nRequired energy: {require_energy}")
            print(f"{_n}, NOT ENOUGH PERIOD TO CHARGE, NEED: {_count - len(available_group)}")
            
            print('\n---LIST OF AVAILABLE PATCH---\n')
            print(available_group)
            print('\n\n')
            

        _ul = []
        _dl = []
        _pl = []
        _cl = []

        # 할당
        for i in range(len(available_group)):
            if _count > 0:
                _ul.append(_bandwidth)
                _dl.append(0)
                _pl.append(2)
                _cl.append(1)
                _count -= 1
            else:
                _ul.append(0)
                _dl.append(0)
                _pl.append(0)
                _cl.append(0)
                
        available_group['charge'] = _ul
        available_group['discharge'] = _dl
        available_group['port_count'] = _pl
        available_group['charger_count'] = _cl

        new_frame = pd.concat([df, available_group])

        df = new_frame.drop_duplicates(subset=['bus', 'period'], keep='last')

        df = sorting(df)

        pd.reset_option('display.max_rows')

    return df


def rorc_restraint_hard_relax(df):
    # 출력 옵션 설정 - 모든 행을 출력하도록 설정
    pd.set_option('display.max_rows', None)

    capa = {'day_bus' : 250,
            'n_bus' : 350}

    df['departure'] = df['operation'].shift(1) != df['operation']  # True: 값이 바뀜, False: 바뀌지 않음

    # 값이 바뀌는 순간을 가지는 행만 선택
    change_points = df[df['departure']]
    change_points = change_points[::2]

    lack_soc = pd.DataFrame(columns=df.columns)
    rows = []

    for row in change_points.itertuples():
        if row.bus[0] == '1':
            if row.SOC < capa['day_bus'] * 0.7:
                rows.append(row._asdict())
            else:
                pass
            
        else:
            if row.SOC < capa['n_bus'] * 0.7:
                rows.append(row._asdict())
            else:
                pass

    lack_soc = pd.concat([lack_soc,pd.DataFrame(rows)])
    _bus_list = set(lack_soc['bus'])
    _bandwidth = 0.416667

    for _n in _bus_list:
        filt = lack_soc['bus'] == _n
        _bus_soc = list(lack_soc.loc[filt, "SOC"])
        require_energy = 0
        
        for state in _bus_soc:
            if _n[0] == '1':
                require_energy += capa['day_bus'] * 0.7 - state
            else:
                require_energy += capa['day_bus'] * 0.7 - state

        # 필요한 period 수 계산
        _count = math.ceil(require_energy / _bandwidth)

        # filt = (df['bus'] == _n) & (df['consumption'] == 0) & ((df['discharge'] > 0) |  (df['charger_count'] == 0))
        filt = (df['bus'] == _n) & (df['consumption'] == 0) & (df['charge'] == 0)
        available_group = df[filt]

        if len(available_group) < _count:
            print(f"\nRequired energy: {require_energy}")
            print(f"{_n}, NOT ENOUGH PERIOD TO CHARGE, NEED: {_count - len(available_group)}")
            print('\n---LIST OF AVAILABLE PATCH---\n')
            print(available_group)
            print('\n\n')
            

        _ul = []
        _dl = []
        _pl = []
        _cl = []

        # 할당
        for i in range(len(available_group)):
            if _count > 0:
                _ul.append(_bandwidth)
                _dl.append(0)
                _pl.append(2)
                _cl.append(1)
                _count -= 1
            else:
                _ul.append(0)
                _dl.append(_bandwidth)
                _pl.append(2)
                _cl.append(1)
                
        available_group['charge'] = _ul
        available_group['discharge'] = _dl
        available_group['port_count'] = _pl
        available_group['charger_count'] = _cl

        new_frame = pd.concat([df, available_group])

        df = new_frame.drop_duplicates(subset=['bus', 'period'], keep='last')

        df = sorting(df)

        pd.reset_option('display.max_rows')

    return df


def calc_penalty(df):
    require_energy = 0
    capa = {'day_bus' : 250,
            'n_bus' : 350}

    df['departure'] = df['operation'].shift(1) != df['operation']  # True: 값이 바뀜, False: 바뀌지 않음

    # 값이 바뀌는 순간을 가지는 행만 선택
    change_points = df[df['departure']]
    change_points = change_points[::2]

    lack_soc = pd.DataFrame(columns=df.columns)
    rows = []

    for row in change_points.itertuples():
        if row.bus[0] == '1':
            if row.SOC < capa['day_bus'] * 0.7:
                rows.append(row._asdict())
            else:
                pass
            
        else:
            if row.SOC < capa['n_bus'] * 0.7:
                rows.append(row._asdict())
            else:
                pass

    lack_soc = pd.concat([lack_soc,pd.DataFrame(rows)])
    _bus_list = set(lack_soc['bus'])

    for _n in _bus_list:
        filt = lack_soc['bus'] == _n
        _bus_soc = list(lack_soc.loc[filt, "SOC"])
        if _n[0] == '1':
            require_energy += capa['day_bus'] * 0.7 - _bus_soc[-1]
        else:
            require_energy += capa['n_bus'] * 0.7 - _bus_soc[-1]

    return require_energy


def calc_shaving(df):
    amount = 0
    for row in df.itertuples():
        if row.peak == True:
            amount += row.discharge
            amount -= row.charge
    return amount