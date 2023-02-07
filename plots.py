import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import json


# plt.rcParams["figure.figsize"] = [7.50, 3.50]
# plt.rcParams["figure.autolayout"] = True

path = '/home/dwdd/thesis/output/20230207_161447'

# fig, axs = plt.subplots(6)
# fig.suptitle('Vertically stacked subplots')

vmstat_headers = ['Run', 'r', 'b', 'swpd', 'free', 'buff', 'cache', 'si', 'so', 'bi', 'bo', 'in', 'cs', 'us', 'sy', 'id', 'wa', 'st', 'CET']
vmstat_df = pd.read_csv(f'{path}/vmstat.csv', verbose=True, names=vmstat_headers)
vmstat_df['CET'] = pd.to_datetime(vmstat_df['CET'])
vmstat_df['seconds'] = vmstat_df['CET'].dt.strftime("%M:%S")
vmstat_df.set_index('seconds')
# vmstat_df.plot()
vmstat_df.plot(kind='line', x='seconds', y='r')
# vmstat_df.plot(ax=axs[0])
plt.xlabel('time')
plt.ylabel('y')
plt.title('vmstat -t -w 1')
plt.xticks(fontsize=9, rotation=90)

mpstat_headers = ['Run', 'Time', 'CPU', '"%"usr', '"%"nice', '"%"sys', '"%"iowait', '"%"irq', '"%"soft', '"%"steal', '"%"guest', '"%"gnice', '"%"idle']
mpstat_df = pd.read_csv(f'{path}/mpstat.csv', verbose=True, names=mpstat_headers)
mpstat_df['Time'] = pd.to_datetime(mpstat_df['Time'])
mpstat_df['seconds'] = mpstat_df['Time'].dt.strftime("%M:%S")
mpstat_df.set_index('seconds')
# mpstat_df.plot()
mpstat_df.plot(kind='line', x='seconds', y='"%"usr')
# mpstat_df.plot(ax=axs[1])
plt.xlabel('time')
plt.ylabel('y')
plt.title('mpstat -P ALL 1')
plt.xticks(fontsize=9, rotation=90)

pidstat_headers = ['Run', 'Time', 'UID', 'PID', '"%"usr', '"%"system', '"%"guest', '"%"wait', '"%"CPU', 'CPU', 'Command']
pidstat_df = pd.read_csv(f'{path}/pidstat.csv', verbose=True, names=pidstat_headers)
pidstat_df['Time'] = pd.to_datetime(pidstat_df['Time'])
pidstat_df['seconds'] = pidstat_df['Time'].dt.strftime("%M:%S")
pidstat_df.set_index('seconds').drop(columns=['PID', 'UID'])
# pidstat_df.plot()
pidstat_df.plot(kind='line', x='seconds', y='"%"usr')
# pidstat_df.plot(ax=axs[2])
plt.xlabel('time')
plt.ylabel('y')
plt.title('pidstat 1 | grep thesis_app')
plt.xticks(fontsize=9, rotation=90)

iostat_d_headers = ['Run', 'Date', 'Time', 'Device', 'tps', 'kB_read/s', 'kB_wrtn/s', 'kB_dscd/s', 'kB_read', 'kB_wrtn', 'kB_dscd']
iostat_d_df = pd.read_csv(f'{path}/iostat_d.csv', verbose=True, names=iostat_d_headers)
iostat_d_df['Time'] = pd.to_datetime(iostat_d_df['Time'])
iostat_d_df['seconds'] = iostat_d_df['Time'].dt.strftime("%M:%S")
iostat_d_df.set_index('Time')
# iostat_d_df.plot()
iostat_d_df.plot(kind='line', x='seconds', y=['kB_wrtn/s', 'tps'])
# iostat_d_df.plot(ax=axs[3])
plt.xlabel('time')
plt.ylabel('y')
plt.title('iostat -td -p sda 1')
plt.xticks(fontsize=9, rotation=90)

iostat_xd_headers = ['Run', 'Date', 'Time', 'Device', 'r/s', 'rkB/s', 'rrqm/s', '"%"rrqm', 'r_await', 'rareq-sz', 'w/s', 'wkB/s', 'wrqm/s', '"%"wrqm',\
                    'w_await', 'wareq-sz', 'd/s', 'dkB/s', 'drqm/s', '"%"drqm', 'd_await', 'dareq-sz', 'f/s', 'f_await', 'aqu-sz', '"%"util']
iostat_xd_df = pd.read_csv(f'{path}/iostat_xd.csv', verbose=True, names=iostat_xd_headers)
iostat_xd_df['Time'] = pd.to_datetime(iostat_xd_df['Time'])
iostat_xd_df['seconds'] = iostat_xd_df['Time'].dt.strftime("%M:%S")
iostat_xd_df.set_index('seconds')
# iostat_xd_df.plot()
iostat_xd_df.plot(kind='line', x='seconds', y='w/s')
# iostat_xd_df.plot(ax=axs[4])
plt.xlabel('time')
plt.ylabel('y')
plt.title('iostat -txd -p sda 1')
plt.xticks(fontsize=9, rotation=90)

runtime_headers = ['Run', 'Memory time', 'Disk time', 'Calc time', 'Tot time']
runtime_df = pd.read_csv(f'{path}/runtimes.csv', verbose=True, names=runtime_headers)
runtime_df.set_index('Run')
# runtime_df.plot()
runtime_df.plot(kind='line', x='Run', y='Tot time')
# runtime_df.plot(ax=axs[5])
plt.xlabel('run iteration')
plt.ylabel('runtime')
plt.title('thesis_app runtimes')


plt.show()

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