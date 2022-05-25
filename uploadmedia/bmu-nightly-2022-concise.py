#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
import numpy as np
import matplotlib
import matplotlib.dates
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import time
from copy import deepcopy


# In[2]:

data_location = sys.argv[1]

data_dir = data_location
image_dir = '/var/www/static'
html_path = ''
html_file = '/var/www/static/bmu_stats.html'

scaffold = open(html_file,'w')
print('<html>', file=scaffold)
print('<h1>BMU utilization over time</h1>', file=scaffold)
print(f'<h4>As of {time.strftime("%b %d %Y %H:%M:%S", time.localtime())}</h4>', file=scaffold)

df = {}
for f in 'botgarden ucjeps pahma cinefiles'.split(' '):
    filename = f'{data_dir}/{f}.bmu.stats.csv'
    dfx = pd.read_csv(filename,sep='\t')
    # convert datestring to dates
    dfx['date'] = pd.to_datetime(dfx['date'], format='%Y-%m-%d-%H-%M-%S', errors='coerce')
    if dfx['date'].notnull().all():
        print('error')
    # oh sheesh, 'count' should of course be an int!
    dfx['count'] = pd.to_numeric(dfx['count'])
    #df.loc[df['rows'] == 0,'rows'] = np.nan
    df[f] = dfx
#df


# In[3]:


# plot plot plot
plt.clf()
import matplotlib.dates as mdates

#years = mdates.YearLocator()   # every year
#months = mdates.MonthLocator()  # every month

fig_width = 10
fig_height = 6


# In[38]:


charts = [
    ('by day', 'D', 'Day', 'blue'),
    ('by week', 'W', 'Week', 'green'),
    ('by month', 'M', 'Month', 'darkorange')
    ]

for key in 'botgarden cinefiles pahma ucjeps'.split(' '):
    group_df = deepcopy(df[key])

    print(f'<h3>{key}</h3>', file=scaffold)
    print(f'<h4><a href="{key}.nightly.report.txt">nightly report</a></h4>', file=scaffold)

    try:
        print(min(group_df['date']), max(group_df['date']))
    except:
        continue

    recent = 60
    fig, ax = plt.subplots(figsize=(fig_width,fig_height))

    recent_days = group_df.resample(rule='D', on='date')['count'].sum()[-recent:]
    recent_days.plot(kind='bar', color = "purple")

    plt.grid(True)
    plt.title(f'{key} media uploaded in last {recent} days')
    plt.xlabel("Day")
    plt.ylabel('Number of files')
    fig.autofmt_xdate()
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
    ax.set_xticks(np.arange(0, len(recent_days)+1, 4))
    imagefile = f'%s-bmu-media-recent' % key
    plt.savefig(f'{image_dir}/{imagefile}')
    #plt.show()
    print(f'<a href="{html_path}/{imagefile}.png"><image width="600px" src="{html_path}/{imagefile}.png"></a>', file=scaffold)

    for c in charts:
        try:
            fig, ax = plt.subplots(figsize=(fig_width,fig_height))
            by_time_unit = group_df.resample(rule=c[1], on='date')['count'].sum()
            by_time_unit.plot(kind='bar', color = c[3])
            plt.grid(True)
            plt.title(f'{key} media uploaded {c[0]}')
            plt.xlabel(c[2])
            #dFmt = mdates.DateFormatter('%Y-%m-%d')
            #ax.xaxis.set_major_formatter(dFmt)
            plt.ylabel('Number of files')
            plt.yscale('log')

            fig.autofmt_xdate()
            ax.set_xticks(np.arange(0, len(by_time_unit)+1, int(len(by_time_unit)/15)))

            imagefile = f'%s-bmu-media-%s' % (key, c[0].replace(' ','-'))
            plt.savefig(f'{image_dir}/{imagefile}')
            #plt.show()
            print(f'<a href="{html_path}/{imagefile}.png"><image width="600px" src="{html_path}/{imagefile}.png"></a>', file=scaffold)
        except:
            pass

print('</html>', file=scaffold)
