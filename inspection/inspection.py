import os
import pandas as pd

parent_directory = ""
# current_directory = os.getcwd()
# parent_directory = os.path.dirname(current_directory) + "/"
solList = ["fcfs_solution.csv", "heuristicSol.csv"]

solution = pd.read_csv(parent_directory + solList[0], index_col=0)

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
        return False
    else:
        return True
    
solution['port_count'] = solution.apply(count_using_port, axis =1)
solution['charger_count'] = solution.apply(count_using_charger, axis = 1)
solution['operation'] = solution.apply(reform_schedule, axis = 1)
solution['departure'] = solution['operation'].shift(1) != solution['operation']  # True: 값이 바뀜, False: 바뀌지 않음

# 값이 바뀌는 순간을 가지는 행만 선택
departure_point = solution[solution['departure']]
departure_point = departure_point[departure_point['operation'] == True]

### 포트 제약
port_count = solution.groupby('period').sum()[['port_count']]
charger_count = solution.groupby('period').sum()[['charger_count']]
_p =charger_count[charger_count['charger_count'] > 30]
_c =port_count[port_count['port_count'] > 60]

if _p.empty & _c.empty:
    print(f"\nPassed port resource constraint")

count = 0
problem_point = []
for row in departure_point.itertuples():
    if row.bus[0] != "N":
        required = 250 * 0.7
    else:
        required = 350 * 0.7
    
    if row.SOC < required:
        count += 1
        problem_point.append(row)
    else:
        pass

problem_df = pd.DataFrame(problem_point)

if count != 0:
    print("Failed rorc constraint\n")
    print(problem_df)
else:
    print("Passed rorc constraint")

# 문제 지점 출력용
if len(problem_df) != 0:
    import matplotlib.pyplot as plt
    prob_bus = set(problem_df['bus'])

    for bus_name in prob_bus:
        _sol = solution[solution['bus'] == bus_name]
        _prob = problem_df[problem_df['bus'] == bus_name]

        plt.title(f"Bus: {bus_name} SOC change")
        plt.xlabel("Period")
        plt.ylabel("SOC(kwh)")

        plt.plot(_sol['period'], _sol['SOC'])
        plt.scatter(_prob['period'], _prob['SOC'], color='red')
        plt.savefig(f"{bus_name}_SOC_change")
        plt.close()