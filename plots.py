import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import json


plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

path = '/home/dwdd/thesis/output/20230207_135212'

vmstat_headers = ['Run', 'r', 'b', 'swpd', 'free', 'buff', 'cache', 'si', 'so', 'bi', 'bo', 'in', 'cs', 'us', 'sy', 'id', 'wa', 'st', 'CET']
vmstat_df = pd.read_csv(f'{path}/vmstat.csv', verbose=True, names=vmstat_headers)
vmstat_df.set_index('CET').plot()
plt.xlabel('time')
plt.ylabel('y')
plt.title('vmstat -t -w 1')

mpstat_headers = ['Run', 'Time', 'CPU', '"%"usr', '"%"nice', '"%"sys', '"%"iowait', '"%"irq', '"%"soft', '"%"steal', '"%"guest', '"%"gnice', '"%"idle']
mpstat_df = pd.read_csv(f'{path}/mpstat.csv', verbose=True, names=mpstat_headers)
mpstat_df.set_index('Time').plot()
plt.xlabel('time')
plt.ylabel('y')
plt.title('mpstat -P ALL 1')

pidstat_headers = ['Run', 'Time', 'UID', 'PID', '"%"usr', '"%"system', '"%"guest', '"%"wait', '"%"CPU', 'CPU', 'Command']
pidstat_df = pd.read_csv(f'{path}/pidstat.csv', verbose=True, names=pidstat_headers)
pidstat_df.set_index('Time').drop(columns=['PID', 'UID']).plot()
plt.xlabel('time')
plt.ylabel('y')
plt.title('pidstat 1 | grep thesis_app')

iostat_d_headers = ['Run', 'Date', 'Time', 'Device', 'tps', 'kB_read/s', 'kB_wrtn/s', 'kB_dscd/s', 'kB_read', 'kB_wrtn', 'kB_dscd']
iostat_d_df = pd.read_csv(f'{path}/iostat_d.csv', verbose=True, names=iostat_d_headers)
iostat_d_df.set_index('Time').drop(columns=['Date']).plot()
plt.xlabel('time')
plt.ylabel('y')
plt.title('iostat -td -p sda 1')

iostat_xd_headers = ['Run', 'Date', 'Time', 'Device', 'r/s', 'rkB/s', 'rrqm/s', '"%"rrqm', 'r_await', 'rareq-sz', 'w/s', 'wkB/s', 'wrqm/s', '"%"wrqm',\
                    'wareq-sz', 'd/s', 'dkB/s', 'drqm/s', '"%"drqm', 'd_await', 'dareq-sz', 'f/s', 'f_await', 'aqu-sz', '"%"util']
iostat_xd_df = pd.read_csv(f'{path}/iostat_xd.csv', verbose=True, names=iostat_xd_headers)
iostat_xd_df.set_index('Time').drop(columns=['Date']).plot()
plt.xlabel('time')
plt.ylabel('y')
plt.title('iostat -txd -p sda 1')

runtime_headers = ['Run', 'Memory time', 'Disk time', 'Calc time', 'Tot time']
runtime_df = pd.read_csv(f'{path}/runtimes.csv', verbose=True, names=runtime_headers)
runtime_df.set_index('Run').plot()
plt.xlabel('run iteration')
plt.ylabel('runtime')
plt.title('thesis_app runtimes')

# print(df.dtypes)
# df['Time']= pd.to_datetime(df['Time']).dt.time
# df['CPU']= df['CPU'].astype('int32')
# df['"%"usr']= df['"%"usr'].astype('float')
# df['"%"nice']= df['"%"nice'].astype('float')
# df['"%"sys']= df['"%"sys'].astype('float')
# df['"%"iowait']= df['"%"iowait'].astype('float')
# df['"%"irq']= df['"%"irq'].astype('float')
# df['"%"soft']= df['"%"soft'].astype('float')
# df['"%"steal']= df['"%"steal'].astype('float')
# df['"%"guest']= df['"%"guest'].astype('float')
# df['"%"gnice']= df['"%"gnice'].astype('float')
# df['"%"idle']= df['"%"idle'].astype('float')



plt.show()



# dictionary = json.load(open('file.json', 'r'))
# xAxis = [key for key, value in dictionary.items()]
# yAxis = [value for key, value in dictionary.items()]
# plt.grid(True)

# ## LINE GRAPH ##
# plt.plot(xAxis,yAxis, color='maroon', marker='o')
# plt.xlabel('variable')
# plt.ylabel('value')

# ## BAR GRAPH ##
# fig = plt.figure()
# plt.bar(xAxis,yAxis, color='maroon')
# plt.xlabel('variable')
# plt.ylabel('value')

# plt.show()