#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 17:19:16 2022

@author: kateburns
"""

# allow same patient by adding another node before patient with cap
# NEED TO MAKE SURE LIST OF DOUBLE DOES NOT REPEAT

#change patient_Id to patient_demographic_ID
#think of way to get rid of patient names

#removes duplicates from controls and pateints but does not remove cross duplicates


import networkx as nx # Import NetworkX tool kit 
import time
import csv

#start timer
start_time = time.time()

#initiate graph
G = nx.DiGraph()

#Patients_Info = open("PMP_Patients.csv")

#/////////////////////////////////////////////////
#assign all things patients
#initiate patients IDs, cases and scores

Patients_Info = open("PMP_Patients.csv")
csvreader = csv.reader(Patients_Info, delimiter=',')

next(csvreader)

list_patients_IDs = []
list_patients_cases = []
list_patients_scores = []

for row in csvreader:
    patients_IDs = row[0]
    patients_cases = row[1]
    patients_scores = row[2]
    
    list_patients_IDs.append(int(patients_IDs))
    list_patients_cases.append(int(patients_cases))
    list_patients_scores.append(float(patients_scores))
    
Patients_Info.close()
  
#initiate patient names (only used within code)
n_patients = len(list_patients_IDs)

list_patients_names = []
i = 1
while i < n_patients + 1:
    list_patients_names.append('t'+str(i))
    i = i + 1
    
##########################################
#assign all things controls
#initiate controls IDs, cases and score

Controls_Info = open("PMP_Controls.csv")
csvreader = csv.reader(Controls_Info, delimiter=',')

next(csvreader)

list_controls_IDs = []
list_controls_cases = []
list_controls_scores = []

for row in csvreader:
    controls_IDs = row[0]
    controls_cases = row[1]
    controls_scores = row[2]
    
    list_controls_IDs.append(int(controls_IDs))
    list_controls_cases.append(int(controls_cases))
    list_controls_scores.append(float(controls_scores))
    
Controls_Info.close()
    
#initiate controls names (only used within code)
n_controls = len(list_controls_IDs)
list_controls_names = []
j = 1
while j < n_controls + 1:
    list_controls_names.append('c'+str(j))
    j = j + 1

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
#add source and sink nodes - subtract any repeated patients
G.add_node("source", demand= - 1 * (n_patients - len(Repeat_patient_IDs))* num_match)
G.add_node("sink", demand = (n_patients - len(Repeat_patient_IDs)) * num_match)

#########################add edges source to patients 
# if we don't care about repeated patients
#i = 1
#while i < n_patients + 1:
 #   G.add_edge("source", list_patients_names[i-1], weight=0, capacity=num_match)
  #  i = i + 1

#add edge source to double_p or patient
#-----may need to add another if statement  
list_double_t_nodes=  []
list_double_t_nodes_names = []
i = 1
while i < n_patients + 1:
    if list_patients_IDs[i-1] in Repeat_patient_IDs:
        node_using = "double_t_" + str(list_patients_IDs[i-1])
        name_using = list_patients_names[i-1]
        list_double_t_nodes_names.append(name_using)
        list_double_t_nodes.append(node_using)
        G.add_edge("source", node_using, weight = 0, capacity = num_match)
        i = i + 1
    else:
        G.add_edge("source", list_patients_names[i-1], weight = 0, capacity = num_match)
        i = i + 1

#add edge double_p to patient
i = 1
while i < len(list_double_t_nodes_names) + 1:
    G.add_edge(list_double_t_nodes[i-1], list_double_t_nodes_names[i-1], weight = 0, capacity = num_match)
    i = i + 1    
    
#######################add edges patients to controls
#accounts for repeated patient and control IDs
#-----needs to be redone so that it isn't just looking at current ID
i = 1 #keeps track of patients
j = 1 #keeps track of controls
while i < n_patients + 1:
    if j < n_controls + 1 and list_patients_IDs[i-1] != list_controls_IDs[j-1]:
        G.add_edge(list_patients_names[i -1], list_controls_names[j-1], weight=abs(list_patients_scores[i-1] - list_controls_scores[j-1]), capacity=1)
        j = j + 1
    elif j > n_controls:
        j = 1
        i = i + 1
    else:
        j = j + 1
        
#for patient in list_patients_names:
 #   for control in list_controls_names:
  #     if patient == control:
   #         continue
    #    else:
     #       G.add_edge(patient, control, weight )
        
######################add edge control to sink or double
list_double_c_nodes = []
j = 1
while j < n_controls + 1:
    if list_controls_IDs[j-1] in Repeat_control_IDs:
        node_using = "double_c_" + str(list_controls_IDs[j-1])
        list_double_c_nodes.append(node_using)
        G.add_edge(list_controls_names[j-1],node_using, weight = 0, capacity = 1)
        j = j + 1
    else:  
        G.add_edge(list_controls_names[j-1], "sink", weight = 0, capacity=1)
        j = j + 1
    
##################### add edge from double to sink
#remove suplicate double nodes
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

