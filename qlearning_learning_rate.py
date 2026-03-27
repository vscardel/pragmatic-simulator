import pandas
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from io import StringIO
from metrics import ms_to_hours, format_hours_minutes

def ms_to_years(time_ms: int):
    return time_ms/31540000000

def ms_to_months(time_ms: int):
    return time_ms/2628000000

results_file = "results-qlearning-learning-3years-4months.csv"
sensors_config_file = "sensors_config.json"

sensors_config_df = pandas.read_json(sensors_config_file)
sensors_op_range_df = pandas.read_json(StringIO(sensors_config_df["operating_range"].to_json()), orient='index')

cr_range_sum = 0
for cr_range in sensors_op_range_df["critical"]:
    cr_range_sum += cr_range[1] - cr_range[0]
    
max_qtable_necessary_size = cr_range_sum * 5


df = pandas.read_csv(results_file)

time_column = df["time"]
total_reward_column = df["total_reward"]
total_positive_reward_qty_column = df["total_positive_reward_qty"]
qlearning_epsilon_column = df["qlearning_epsilon"]
qtable_size = df["qtable_size"]
measured_state = df["measured_state"]
unnecessary_maintenances = df['unnecessary_maintenances']
time_with_available_teams = df["time_with_available_teams"]
necessary_upkeep_broker_messages = df["necessary_upkeep_broker_messages"]

x = time_column[2:].map(lambda x: ms_to_years(x)).to_numpy()
y = np.zeros(len(x))
y_smoothed = np.zeros(len(x))
y2 = np.zeros(len(x))
y2_smoothed = np.zeros(len(x))
y3 = qlearning_epsilon_column[2:]
y4 = np.zeros(len(x))
y5 = time_with_available_teams[2:].map(lambda x: ms_to_months(x))
y5_smoothed = np.zeros(len(x))
y6 = necessary_upkeep_broker_messages[2:]
y6_smoothed = np.zeros(len(x))


window_size = 1000
smoothed_total_reward_column = df["total_reward"].rolling(window=window_size, center=True).mean()
smoothed_total_positive_reward_qty_column = df["total_positive_reward_qty"].rolling(
    window=window_size, center=True).mean()
smoothed_qtable_size = df["qtable_size"].rolling(window=window_size, center=True).mean()
smoothed_measured_state = df["measured_state"].rolling(window=window_size, center=True).mean()
smoothed_unnecessary_maintenances = df["unnecessary_maintenances"].rolling(
    window=window_size, center=True).mean()

for i in range(len(total_reward_column[2:])):
    y[i] = total_reward_column[i+2] - total_reward_column[i+1]
    y_smoothed[i] = smoothed_total_reward_column[i+2] - \
        smoothed_total_reward_column[i+1]
    
    y2[i] = smoothed_unnecessary_maintenances[i+2] - smoothed_unnecessary_maintenances[i+1]
    
    y4[i] = qtable_size[i]


fig, ((ax1,ax2),(ax3,ax4)) = plt.subplots(2,2)

ax1.set_title("Total recompensa por hora")
ax1.plot(x,y)
ax1.set_xlabel("Tempo (Anos)")
ax1.set_ylabel("Soma Recompensa")
# ax1.plot(x,y_smoothed)

ax2.set_title("Média de manutenções desnecessárias")
ax2.plot(x,y2)
ax2.set_xlabel("Tempo (Anos)")
ax2.set_ylabel("Manutenções")

ax3.set_title("Q-Learning Epsilon (ε)")
ax3.plot(x,y3)
ax3.set_xlabel("Tempo (Anos)")
ax3.set_ylabel("Epsilon (ε)")

ax4.set_title("Tamanho Q-Table")
ax4.plot(x,y4)
ax4.set_xlabel("Tempo (Anos)")
ax4.set_ylabel("Estados explorados")

# ax5.set_title("Tempo com equipes disponíveis")
# ax5.plot(x,y5)
# ax5.set_xlabel("Tempo (Anos)")
# ax5.set_ylabel("Tempo (Meses)")

# ax6.set_title("Mensagens de manutenção necessárias")
# ax6.plot(x,y6)
# ax6.set_xlabel("Tempo (Anos)")
# ax6.set_ylabel("Mensagens")

plt.show()
