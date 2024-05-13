if __name__ == '__main__':
    from module import *
    import warnings
    warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)  # 경고 억제

    import argparse
    parser = argparse.ArgumentParser(description='스크립트에 전달되는 파라미터 처리')
    parser.add_argument('shave', type=int, default=3462, help='Max peak shaving')
    parser.add_argument('--k', type=float, default=1, help='ratio')
    parser.add_argument('--s', type=int, help='seed number')
    args = parser.parse_args()

    current_directory = os.getcwd()
    parent_directory = os.path.dirname(current_directory)
    parent_directory = os.path.dirname(parent_directory)

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

    # import 경로
    import_directory = parent_directory + "/Data/l1/out/final/5min_30bus/"

    # Range 운행 정보 불러오기, 모든 운행시점이 포함되어 있음
    file_name = 'schedule_range.txt'
    file_directory = import_directory + file_name
    schedule = open_schedule_range(file_directory)

    # 가격 데이터 불러오기
    file_name = "ePrice.csv"
    import_directory = parent_directory + "/Data/l2/out/sum/" + file_name

    e_price = pd.read_csv(import_directory)

    file_name = "sPrice.csv"
    import_directory = parent_directory + "/Data/l2/out/sum/" + file_name

    s_price = pd.read_csv(import_directory)

    # """head"""
    head = extract_head(schedule)

    # """body"""
    dummy = optimal_solution
    body = []
    for i in range(150):
        body.append(dummy[:288])
        dummy = dummy[288:]

    # """cond"""
    # cond를 주기 동안의 최소치로 잡아야 할 듯?
    cond = []
    for i in range(150):
        cond.append(body[i].iloc[0]["SOC"])

    import copy

    # 원본 손상 방지
    head_copy = copy.deepcopy(head)

    import time

    # 코드 작동 시간 측정
    start_time = time.time()  # 시작 시간

    mean_distance_list = create_mean_distance_list(head_copy)

    # 코사인 유사도 계산
    mean_distance_cosine_similarity = []
    for i in range(150):
        temp = []
        for j in range(150):
            similarity = cosine_similarity(mean_distance_list[i], mean_distance_list[j])
            # print("두 벡터 간의 코사인 유사도:", similarity)
            temp.append(similarity)
        mean_distance_cosine_similarity.append(temp)

    matrix_mdcs = np.array(mean_distance_cosine_similarity).reshape(150,150)

    #유사도에 따라서 군집 형성
    from scipy.cluster.hierarchy import linkage, fcluster

    # 계층적 클러스터링 수행
    Z = linkage(matrix_mdcs, method='ward')  # ward 연결법 사용

    threshold = 0.7  # 클러스터링 임계값 설정
    clusters = fcluster(Z, threshold, criterion='distance')

    #클러스터에 해당하는 솔루션 할당하기
    # seedNum = str(43)
    import_directory = parent_directory + "/Data/l1/out/" + args.s

    # Range 운행 불러오기
    file_name = "/schedule_range.txt"
    new_schedule = open_schedule_range(import_directory + file_name)

    # 타겟 데이터 head 추출
    new_data_head = extract_head(new_schedule)

    # 타겟 head의 mdl 생성
    new_mean_distance_list = create_mean_distance_list(new_data_head)

    # 새로운 데이터와 기존 데이터 간의 유사도 계산
    compared_similarity = calculate_similarity(new_mean_distance_list, mean_distance_list,"cosine")

    # 솔루션 재구성
    mean_distance_candidates = extract_candidates(compared_similarity)

    # 인덱스 가져오기
    bus_list = list(new_schedule.keys())
    index = 0
    consumption = 0.25
    initial_solution = pd.DataFrame(columns=['bus', 'period', 'charge', 'discharge', 'consumption'])

    for _candid in mean_distance_candidates:

        bus_name = bus_list[index//5]
        current_head = new_data_head[index]
        current_period = period_check(current_head)

        index = index + 1

        # 일단은 무조건 후보들 중 첫번째 사용하기로...
        pointer = _candid[0]
        pointing_head = head[pointer]
        pointing_body = body[pointer]
        pointing_period = period_check(pointing_head)

        # patch에서 그대로 가져와도 되는 스케줄 먼저 생성...시점을 0으로 고정 ~> 스케줄을 이미 다 불러왔기 때문에 필요 없을 듯
        T = [t for t in range(1,288+1)]
        A = [int(t) - 288 * current_period for t in current_head]
        B = [int(t) - 288 * pointing_period for t in pointing_head]
        
        a_period = list(set(A))
        b_period = list(set(B) - set(A))
        a_comp_period = list(set(A)-set(B))
        c_period = list(set(T) - set(a_period) - set(b_period))

        # if (len(a_comp_period) != len(b_comp_period)):
        #     print(f"a-: {len(a_comp_period)}")
        #     print(f"b-: {len(b_period)}")
        #     print("")
        
        sol_operation = {
            'bus': [bus_name for _ in a_period]+
                    [bus_name for _ in b_period]+
                    [bus_name for _ in c_period],
            'period': [t + current_period * 288 for t in a_period]+
                            [t + current_period * 288 for t in b_period]+
                            [t + current_period * 288 for t in c_period],
            'charge':   [0 for _ in a_period]+
                            [pointing_body.iloc[t-1]['charge'] for t in a_comp_period]+
                            [pointing_body.iloc[t-1]['charge'] for t in c_period],         # 리스트 인덱스는 0부터 시작하니까 하나 빼줘야 함
            'discharge': [0 for _ in a_period]+
                            [pointing_body.iloc[t-1]['discharge'] for t in a_comp_period]+
                            [pointing_body.iloc[t-1]['discharge'] for t in c_period],
            'consumption':
                            [consumption for _ in a_period]+
                            [0 for _ in b_period]+
                            [0 for _ in c_period]
            }
        _df = pd.DataFrame(sol_operation)
        initial_solution = pd.concat([initial_solution, _df], axis=0)

    initial_solution['period'] = initial_solution['period'].astype(int)
        
    initial_solution['port_count'] = initial_solution.apply(count_using_port, axis =1)
    initial_solution['charger_count'] = initial_solution.apply(count_using_charger, axis = 1)
    initial_solution['operation'] = initial_solution.apply(reform_schedule, axis = 1)

    initial_solution = initial_solution.sort_values(by = ['bus', 'period'])

    heuristic_solution = initial_solution.copy()


    ### 피크 시간대 충전 불가
    # 피크 컬럼 추가
    heuristic_solution['peak'] = heuristic_solution.apply(check_peak, axis=1)

    # 피크시간 충전 불가
    heuristic_solution['charge'] = heuristic_solution.apply(peak_no_charge, axis= 1)

    # charge, port 값 복구
    heuristic_solution['port_count'] = heuristic_solution.apply(unseize_port, axis = 1)
    heuristic_solution['charger_count'] = heuristic_solution.apply(unseize_charger, axis=1)


    ### level 조정
    heuristic_solution['SOC'] = releveling(heuristic_solution)


    ### rorc 제약
    heuristic_solution = rorc_restraint(heuristic_solution)
    # charge, port 값 복구
    heuristic_solution['port_count'] = heuristic_solution.apply(unseize_port, axis = 1)
    heuristic_solution['charger_count'] = heuristic_solution.apply(unseize_charger, axis=1)

    ### 피크 방전량 제약
    
    # max_discharge = 3462
    # k = 1
    heuristic_solution = peak_discharge_restraint(heuristic_solution, args.shave, args.k)

    ### level 조정
    heuristic_solution['SOC'] = releveling(heuristic_solution)

    ### rorc 2
    heuristic_solution = rorc_restraint_peak_include(heuristic_solution)

    ### leveling 2
    heuristic_solution['SOC'] = releveling(heuristic_solution)

    ### 포트 제약
    port_count = heuristic_solution.groupby('period').sum()[['port_count']]
    charger_count = heuristic_solution.groupby('period').sum()[['charger_count']]
    _p =charger_count[charger_count['charger_count'] > 30]
    _c =port_count[port_count['port_count'] > 60]

    if _p.empty & _c.empty:
        print(f"\nPassed port resource constraint")

    penalty_amount = calc_penalty(heuristic_solution)
    # penalty_cost = 232.5 * penalty_amount
    penalty_cost = 121 * penalty_amount

    df1 = heuristic_solution.groupby('period').sum()[['charge']]
    df3 = heuristic_solution.groupby('period').sum()[['discharge']]

    # new_sol obj
    sell = 0
    buy = 0

    for i in range(1440):
        sell += df3.iloc[i]['discharge'] * s_price.iloc[i]['price']
        buy += df1.iloc[i]['charge'] * e_price.iloc[i]['price']

    cost = buy - sell + penalty_cost

    shaving_amount = calc_shaving(heuristic_solution)

    print(f"Obj. {cost}")
    print(f"Shaved. {shaving_amount}")

    end_time = time.time()  # 종료 시간
    elapsed_time = end_time - start_time  # 작동 시간 계산
    print(f"\n코드 작동 시간: {elapsed_time:.4f}초")

    # output
    optimal_solution.to_csv('optimalSol.csv')
    initial_solution.to_csv('initialSol.csv')
    heuristic_solution.to_csv('heuristicSol.csv')

    
