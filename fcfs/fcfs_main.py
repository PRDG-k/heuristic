if __name__ == '__main__':
    import os
    import argparse
    from fcfs_module import *

    import argparse
    parser = argparse.ArgumentParser(description='스크립트에 전달되는 파라미터 처리')
    parser.add_argument('shave', type=int, default=3462, help='Max peak shaving')
    parser.add_argument('--k', type=float, default=1, help='ratio')
    parser.add_argument('--s', type=str, help='seed number')
    args = parser.parse_args()

    current_directory = os.getcwd()
    parent_directory = os.path.dirname(current_directory)
    parent_directory = os.path.dirname(parent_directory)

    # 버스 운행 정보 불러오기
    import_directory = parent_directory + "/Data/l1/out/" + args.s
    file_name = "/schedule_range.txt"

    schedule = {}

    with open(import_directory + file_name, 'r') as file:
        for line in file:
            parts = line.strip().split(' ')

            key = parts[0]
            items = parts[1:]
            # schedule[key] = items
            schedule[key] = sorted(items, key=lambda x: int(x))

    # 충전소 데이터 불러오기
    import_directory = parent_directory + "/Data/l2/out/"
    file_name = "/prob_info.txt"

    prob_info = {}
    column = ['status', 'obj_value', 'period', 'unit',
            'station', 'port', 'bandwidth', 'power', 'RORC']
    with open(import_directory + file_name, 'r') as file:
        index = 0
        for line in file:
            parts = line.strip().split()

            key = column[index]
            prob_info[key] = eval(parts[0])

            index = index + 1
    
    NT = int(prob_info['period'])
    T = range(1, NT+1)

    on_station = on_station_list(schedule, NT)

    for t in T:
        calculate_demand
    
    