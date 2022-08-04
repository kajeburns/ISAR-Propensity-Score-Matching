#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 22:54:01 2022

@author: kateburns
"""

# redo all for loops no patient/control names

import networkx as nx # Import NetworkX tool kit 
import time
import csv

#start timer
start_time = time.time()

#initiate graph
G = nx.DiGraph()

Patients_Info = open("PMP_Patients.csv")

#/////////////////////////////////////////////////
#assign all things patients
#initiate patients IDs, cases and scores

Patients_Info = open("PMP_Patients.csv")
csvreader = csv.reader(Patients_Info, delimiter=',')

next(csvreader)

for row in csvreader:
    patients_IDs = row[0]
    patients_cases = row[1]
    patients_scores = row[2]
    
    patients_IDs_dict = {}
    IDs = row[0]
    cases = row[1]
    scores = row[2]
    
    patientdict = {IDs:cases for IDs, cases in row}  
    
Patients_Info.close()

##########################################
#assign all things controls
#initiate controls IDs, cases and score

Controls_Info = open("PMP_Controls.csv")
csvreader = csv.reader(Controls_Info, delimiter=',')

next(csvreader)


for row in csvreader:
    IDs = row[0]
    cases = row[1]
    scores = row[2]
    
    controldict = {IDs:cases for IDs, cases in row}
    
Controls_Info.close()

#///////////////////////////////////////////////////////
# find if repeated
def Repeat(x):
    _size = len(x)
    repeated = []
    for i in range(_size):
        k = i + 1
        for j in range(k, _size):
            if x[i] == x[j] and x[i] not in repeated:
                repeated.append(x[i])
    return repeated

######## make list of patients and control IDs that repeat
Repeat_patient_IDs = []
Repeat_patient_IDs = Repeat(list_patients_IDs)

Repeat_control_IDs = []
Repeat_control_IDs = Repeat(list_controls_IDs)

########make a list
#//////////////////////////////////////////////////////
#ask how many patients they would like the match
num_match = input("How many controls would you like to match each patient? ")
num_match = int(num_match)

#//////////////////////////////////////////////////////
#build model
#add source and sink nodes
G.add_node("source", demand= - n_patients * num_match)
G.add_node("sink", demand = n_patients * num_match)

#########################add edges source to patients 
for x in list_patients_IDs:
    if x in Repeat_patient_IDs:
        node_using = "double_" + str(x)
        G.add_edge("source", node_using, weight = 0, capacity = num_match)
    else:
        G.add_edge("source", x, weight = 0, capacity = num_match)
    
#######################add edges patients to controls
#accounts for repeated patient and control IDs
i = 1
j = 1
while i < n_patients + 1:
    if j < n_controls + 1 and list_patients_IDs[i-1] != list_controls_IDs[j-1]:
        G.add_edge(list_patients_names[i -1], list_controls_names[j-1], weight=abs(list_patients_scores[i-1] - list_controls_scores[j-1]), capacity=1)
        j = j + 1
    elif j > n_controls:
        j = 1
        i = i + 1
    else:
        j = j + 1
        
######################add edge control to sink or double
list_double_c_nodes = []
j = 1
while j < n_controls + 1:
    if list_controls_IDs[j-1] in Repeat_control_IDs:
        node_using = "double_" + str(list_controls_IDs[j-1])
        list_double_c_nodes.append(node_using)
        G.add_edge(list_controls_names[j-1],node_using, weight = 0, capacity = 1)
        j = j + 1
    else:  
        G.add_edge(list_controls_names[j-1], "sink", weight = 0, capacity=1)
        j = j + 1
    
##################### add edge from double to sink
#might be messed
list_double_c_nodes = list(dict.fromkeys(list_double_c_nodes))
j = 1
while j < len(list_double_c_nodes):
    G.add_edge(list_double_c_nodes[j-1],"sink", weight = 0, capacity = 1)
    j = j + 1

#//////////////////////////////////////////////////////////
#solve problem
optimalRouteDict = nx.min_cost_flow(G)
optimalCost = nx.cost_of_flow(G, optimalRouteDict, weight='weight')

#print(optimalRoute)
print("Optimal Cost is " + str(optimalCost))
#//////////////////////////////////////////////////////////
# get actual information output matches out of optimalRouteDict
            
output_t = []
output_c =[]

for p_id, p_info in optimalRouteDict.items():
    if p_id[0] == 't':
        for key in p_info:
            if p_info[key] == 1:
                output_t.append(p_id)
                output_c.append(key)

output_t_IDs = []
output_t_cases =[]
            
for x in output_t:
    y = int(x[1:])
    output_t_IDs.append(str(list_patients_IDs[y-1]))
    output_t_cases.append(str(list_patients_cases[y-1]))

output_c_IDs = []
output_c_cases = []    

for x in output_c:
    y = int(x[1:])
    output_c_IDs.append(str(list_controls_IDs[y-1]))
    output_c_cases.append(str(list_controls_cases[y-1]))
       
output_t.insert(0, 'patient_case')
output_t_IDs.insert(0, 'P_Demographic_ID')
output_t_cases.insert(0, 'P_Case_ID')
output_c.insert(0, 'control_case')
output_c_IDs.insert(0, 'C_Demographic_ID')
output_c_cases.insert(0, 'C_Case_ID')

#////////////////////////////////////////////////////////
#send to csv
f = open('PMP_Matches.csv','w',newline="")
writer = csv.writer(f)

for i in range (len(output_c)):
    writer.writerow([output_t_IDs[i], output_t_cases[i], output_c_IDs[i], output_c_cases[i]])
f.close()

#////////////////////////////////////////////////////////
#print run time
run_time = time.time() - start_time
print("Run time is " + str(run_time) + " seconds")
