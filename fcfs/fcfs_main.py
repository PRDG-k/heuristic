if __name__ == '__main__':
    import pandas as pd
    from fcfs_module import *
    from file_processing import *

    args = import_args()
    schedule, charge_finished = import_bus_schedule(args['s'])
    bus_list = list(schedule.keys())
    # e_price, s_price = import_price()
    
    solution = init_tzero(bus_list)

    NT = int(1440)
    T = range(1, NT+1)

    on_station = on_station_list(schedule, NT)

    # # list of seize n
    # seize_list = []

    # # list of required n
    # wait_list = []
    

    import time

    # 코드 작동 시간 측정
    print("--FCFS Start--")
    start_time = time.time()  # 시작 시간

    iter_count = 0
    for t in T:
        for bus in on_station:
            # 차고지에 있는 시간 리스트
            L = on_station[bus]

            # if charge_finished[bus] == True:
            #     continue

            try:
                filt= (solution['bus'] == bus) & (solution['period'] == t-1)
                _soc = solution.loc[filt, 'SOC'].values

                if L[0] != t:
                    # driving
                    _sol = TEMPLATE(bus, t, _soc, 2)
                else:
                    if bus in seize_list:
                        _sol = in_list_decision(bus, t, _soc)
                    else:
                        _sol = not_in_list_decision(bus, t, _soc)
                    del L[0]
                
                iter_count += 1
                solution = pd.concat([solution, pd.DataFrame(_sol)], ignore_index=True)

            except IndexError:
                # if index error -> only driving schedule exist
                _sol = TEMPLATE(bus, t, _soc, 4)
                print(f"\nPERIOD: {t}")
                print(f"---BUS: {bus} finished---")
                charge_finished[bus] = True
                

            
    
    end_time = time.time()  # 종료 시간
    elapsed_time = end_time - start_time  # 작동 시간 계산
    print(f"--FCFS Finished--")
    print(f"\n코드 작동 시간: {elapsed_time:.4f}초")

    # Output
    solution = solution.sort_values(by=['bus', 'period'])
    solution.to_csv("fcfs_solution.csv")

    export_result(solution, elapsed_time, iter_count)

    