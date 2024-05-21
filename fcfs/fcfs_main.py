if __name__ == '__main__':
    import os
    import pandas as pd
    import argparse
    from fcfs_module import *

    current_directory = os.getcwd()
    parent_directory = os.path.dirname(current_directory)
    # parent_directory = os.path.dirname(parent_directory)
    
    args = {}
    with open("fcfs/args.txt", 'r') as file:
        for line in file:
            parts = line.strip().split(' ')

            key = parts[0]
            items = parts[1]
            args[key] = items


    # 버스 운행 정보 불러오기
    import_directory = parent_directory + "/Data/l1/out/" + args["s"]
    file_name = "/schedule_range.txt"

    schedule = {}
    solution = {}
    charge_finished = {}

    with open(import_directory + file_name, 'r') as file:
        for line in file:
            parts = line.strip().split(' ')

            key = parts[0]
            items = parts[1:]
            # schedule[key] = items
            schedule[key] = sorted(items, key=lambda x: int(x))
            
            charge_finished[key] = {False}
    
    bus_list = list(schedule.keys())
    solution['bus'] = [n for n in bus_list]
    solution['period'] = [0 for _ in bus_list]
    solution['charge'] = [0 for _ in bus_list]
    solution['discharge'] = [0 for _ in bus_list]
    solution['consumption'] = [0 for _ in bus_list]
    solution['SOC'] = [check_bus_type(n) for n in bus_list]
    solution = pd.DataFrame(solution)

    # 충전소 데이터 불러오기
    # import_directory = parent_directory + "/Data/l2/out/"
    # file_name = "prob_info.csv"
    # prob_info = pd.read_csv(import_directory + file_name)
    
    # NT = int(prob_info['period'])
    NT = int(1440)
    T = range(1, NT+1)

    on_station = on_station_list(schedule, NT)
    on_charging = []
    
    consumption = 0.25
    charge = 0.4166667

    import time

    # 코드 작동 시간 측정
    start_time = time.time()  # 시작 시간

    for t in T:
        print(f"TNOW: {t}")
        
        for bus in on_station:
            L = on_station[bus]

            if charge_finished[bus] == True:
                continue

            try:
                filt= (solution['bus'] == bus) & (solution['period'] == t-1)
                _soc = solution.loc[filt, 'SOC'].values

                if L[0] != t:
                    _sol = bus_departure(on_charging, bus, t, _soc)
                else:
                    _sol = bus_charging(on_charging, bus, t, _soc)
                    del L[0]
                
                solution = pd.concat([solution, pd.DataFrame(_sol)], ignore_index=True)

            except IndexError:
                print(f"\nPERIOD: {t}")
                print(f"---BUS: {bus} finished---")
                charge_finished[key] = True
                
    
    end_time = time.time()  # 종료 시간
    elapsed_time = end_time - start_time  # 작동 시간 계산
    print(f"\n코드 작동 시간: {elapsed_time:.4f}초")

    solution = solution.sort_values(by=['bus', 'period'])
    solution.to_csv("fcfs_solution.csv")