import math
import random
import pandas as pd
import numpy as np
from Cointegration import cointegration
from ArctanTransform import arctan_trans
from AttributionSelecttion import select_attribute
from Effective import time_one
from EquilibriumIndex import equilibrium_index_DI, equilibrium_index_TED
from EquilibriumParameter import feature_distribution, equilibrium_state_parameter_set
from StateParameter import state_parameter_set
import matplotlib.pyplot as plt
from LTraining import L_parameters
from ToCsv import dataToCsv
from correlation import attribution_correlation, regression_models
import time

data_attribute_raw = pd.read_csv("covid/attributes.csv")

data_attribute = np.array(data_attribute_raw) # panel data


no_region = len(data_attribute[:, 0])
name_region = data_attribute[:, 0]

############################################
# daily data

date_daily_raw = pd.read_csv("covid19/daily.csv") # row date, column regin
date = pd.read_csv("covid19/date.csv") # from 25/1/2020


#date_case = np.array(date_daily_raw[1:,:])
no_date = len(date_daily_raw[1:, 0])

#daily_state = list(map(list, zip(*date_case)))



############################################
# for choosing attributes
############################################
time_record = []
#start_time = time.time()
# attribute = [2,8,11,12,14,15]
# attribute = [1,2,4,5]
#attribute = [8]#, 11, 12, 14, 15]
# attribute = [2]
num_attribution = np.shape(data_attribute[:,2:16])[1]
attribute = select_attribute(num_attribution, data_attribute[:,2:16], daily_state, 0, h=100) # h is the length of training day


no_attribute = len(attribute)
data_attribute = data_attribute[:, attribute]





################################################
######### test     #############################
################################################
start_time = time.time()

# state paramater
spss = []
for i in range(no_date+1):
    sps = state_parameter_set(date_daily_raw[i,1:])
    sps = sps.astype(float)
    spss.append(sps)

# test correlates
x_c = data_attribute

y_c = spss[0] # 0 is the first day.
correlates = attribution_correlation(3, x_c, y_c) # 3 is ols

# equilibrium state raw
choice = 1
x=0
#r = 10 # the number for rolling windows
s = no_date
esps=[]
esps_raw = 0
for n in range(s):
    d = date[n]
    for i in range(no_attribute):
        ad = data_attribute.loc[data_attribute.iloc[:,'Date']==d,1:] # first column is the name of region
        a = feature_distribution(data_attribute[:, i], correlates[i])
        x += a
    esps_r += equilibrium_state_parameter_set(x, no_attribute)
    esps_r = esps_r / 2
    esps.append(esps_r)


#esps = ((x / no_attribute + 1) + 1) / no_region
#esps_raw = equilibrium_state_parameter_set(x,no_attribute)

# training
n = 10
x = 0
input_s = spss[x:x + n]
input_e = esps[x:x + n]

while cointegration(input_e,input_s):
    esps_output = []
    #input = spss[x:x + n]


    for i in range(len(input_s)):
        L = L_parameters(input_s, input_e)

    esps_0 =  (input_e[x+n] + L)/2
    for j in range(n-x):
        esps_output.append(esps_0)
    input_e = esps_output

esps = input_e[x + n]


    # esps for test
    #dt = date[x + n + 1]
    #for i in range(no_attribute):
    #    ad = data_attribute.loc[data_attribute.iloc[:, 'Date'] == dt, 1:]  # first column is the name of region
    #    a = feature_distribution(data_attribute[:, i], correlates[i])
    #    x += a
    #esps = (equilibrium_state_parameter_set(x, no_attribute) + L) / 2




'''
ES= np.array(esps)
ES= ES.T
np.array(ES)
save = pd.DataFrame(ES, columns=['ES'])
save.to_csv('ES.csv', index=False, header=False)
'''

# equilibrium index
EI_DI = equilibrium_index_DI(spss[0],esps) # 0 is the first day. 1 is second day

EI_TED = equilibrium_index_TED(spss[0],esps)

'''
ES_EI_DI= np.array(EI_DI)
ES_EI_DI= ES_EI_DI.T
np.array(ES_EI_DI)
save = pd.DataFrame(ES_EI_DI, columns=['EI_DI'])
save.to_csv('EI_DI.csv', index=False, header=False)

ES_EI_TED= np.array(EI_TED)
ES_EI_TED= ES_EI_TED.T
np.array(ES_EI_TED)
save = pd.DataFrame(ES_EI_TED, columns=['EI_TED'])
save.to_csv('EI_TED.csv', index=False, header=False)
'''
end_time = time.time()  # 1657267201.6171696

time1 = end_time - start_time
time_record.append(time1)
time_record = np.array(time_record)
time_record = time_record.T

np.array(time_record)
save = pd.DataFrame(time_record, columns=['time'])
save.to_csv('time.csv', index=False, header=False)