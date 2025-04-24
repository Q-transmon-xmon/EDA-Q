import numpy as np
import networkx as nx
import math
import random
import pandas as pd
import numpy.matlib

CROSS_RATE = 0.85    # DNA crossover probability 
MUTATION_RATE = 0.15 # mutation probability

def get_distance(v1,v2):
    """
    Calculate the Manhattan distance between two points.
    """
    return abs(v1[0]-v2[0])+abs(v1[1]-v2[1])

def get_DNA_fitness(DNA,row,column,M):
    """
    Calculation of individual fitness.

    Args:
        DNA: individual.
        M: Coupling Degree Matrix.

    Return:
        not_1_total_edge_d_and_weight: individual fitness value.
    """
    Q_NUM=len(M)
    node_index = 0  #Starting point of standard serial number
    # Create a complete grid diagram
    G_complete = nx.grid_graph(dim=[row, column], periodic=False)
    DNA_set = set(tuple(pair) for pair in zip(DNA[0::2], DNA[1::2]))
    G_complete_set = set(list(G_complete.nodes()))
    unused_nodes_set = G_complete_set.difference(DNA_set)
    for i in unused_nodes_set:
        G_complete.remove_node(i)
    if nx.is_connected(G_complete) is not True:
        return 150000
    # Actual points and corresponding coordinates
    G=nx.Graph()
    q_pos=dict() # qubit-position
    pos_q=dict() # position-qubit
    for i in range(Q_NUM):
        q_pos[i]=[DNA[i*2],DNA[i*2+1]]
        pos_q[(DNA[i*2],DNA[i*2+1])]=i
        G.add_node(i)
    
    # Pruning(Adjacent and connected in the program)
    actual_edge1 = np.matlib.zeros((Q_NUM,Q_NUM))
    actual_edge1 = np.asarray(actual_edge1) # Actual edge matrix
    for i in range(len(M)):
        for j in range(len(M[i])):
            if j<i:
                v1=q_pos[i]
                v2=q_pos[j]
                if M[i][j] != 0 and get_distance(v1, v2) == 1:
                    actual_edge1[i][j]=1
                    actual_edge1[j][i]=1
                    G.add_edge(i, j)
    # Modify(For the case of disconnected or non shortest path)
    actual_edge2=actual_edge1.copy()
    for i in range(len(M)):
        for j in range(len(M[i])):
            if i > j and M[i][j] != 0:
                v1 = q_pos[i]
                v2 = q_pos[j]
                d_S=0
                if nx.has_path(G, i, j):
                    d_S=nx.shortest_path_length(G, source=i, target=j)
                if d_S!=get_distance(v1, v2):
                    # Need to add edges.
                    a_path=nx.shortest_path(G_complete,(v1[0],v1[1]),(v2[0],v2[1]))
                    for k in range(len(a_path)-1):
                        G.add_edge(pos_q[a_path[k]], pos_q[a_path[k+1]])
                        actual_edge2[pos_q[a_path[k]]][pos_q[a_path[k+1]]]=1
                        actual_edge2[pos_q[a_path[k+1]]][pos_q[a_path[k]]]=1
    not_1_total_edge_d_and_weight = 0 # sum(dij*Mij), dij>1
    if nx.is_connected(G) != True:
        return not_1_total_edge_d_and_weight+150000
    for i in range(len(M)):
        for j in range(len(M[i])):
            if i>j:
                #compute
                v1=[DNA[2*i],DNA[2*i+1]]
                v2=[DNA[2*j],DNA[2*j+1]]
                d=nx.shortest_path_length(G,source=i,target=j)
                if d>1:
                    not_1_total_edge_d_and_weight+=M[i][j]*d
    return not_1_total_edge_d_and_weight

def get_fitness(pop,M,standard_coordinate,row,column):
    """
    Calculation of fitness function.

    Args:
        pop: population.
        M: Coupling Degree Matrix.
        standard_coordinate: Standard coordinates list.

    Return:
        fit: population fitness value.
    """
    fit = np.zeros((len(pop),1))
    # Calculate the fitness of individual
    for i in range(len(fit)):
        temp_individual = np.zeros((len(pop[i])*2),dtype=int).tolist() # [ , , , ]
        for j in range(len(pop[i])):
            temp_individual[j*2]= standard_coordinate[int(pop[i][j])][0]
            temp_individual[j*2+1]= standard_coordinate[int(pop[i][j])][1]
        fit[i][0] = get_DNA_fitness(temp_individual,row,column,M)
    return fit

def tournament_select(pops,popsize,fits,tournament_size):
    """
    tournament select
    """
    new_pops =[]
    while len(new_pops)<len(pops):
        tournament_list = random.sample(range(0,popsize),tournament_size)
        tournament_fit = [fits[i] for i in tournament_list]
        tournament_df = pd.DataFrame([tournament_list,tournament_fit]).transpose().sort_values(by=1).reset_index(drop=True)
        pop = pops[int(tournament_df.iloc[0,0])]
        new_pops.append(pop)
    return new_pops

def crossover_GATS(popsize,parent1_pops,parent2_pops,ts_list,row,column):
    """
    crossover with tabu list.

    Args:
        popsize: population size.
        parent1_pops: Parent generation 1
        parent2_pops: Parent generation 2
        ts_list: tabu list.

    Return:
        child_pops: Crossovered population.
    """
    child_pops = []   
    for i in range(popsize):
        # print(i)
        flag = True
        while flag:
            child = [None]*len(parent1_pops[i])
            parent1 = parent1_pops[i].copy()
            parent2 = parent2_pops[i].copy()
            while parent1 == parent2:
                id = random.sample(range(0,popsize),1)[0]
                parent2 = parent2_pops[id].copy()
            # print(parent1)
            # print(parent2)
            if random.random() >= CROSS_RATE:
                x = random.sample(range(0,2),1)[0]
                if x == 0:
                    child = parent1.copy()    
                else:
                    child = parent2.copy()
                random.shuffle(child)           
            else:
                children = np.zeros((2,len(parent1_pops[0])),dtype=int)-np.ones((2,len(parent1_pops[0])),dtype=int).tolist()
                # (Position-based crossover,PBX)
                Position_based_number = random.sample(range(1,len(parent1)),1)[0]
                Position_based = random.sample(range(0,len(parent1)),Position_based_number)
                for j in range(len(Position_based)):
                    children[0][Position_based[j]] = parent1[Position_based[j]]   
                temp = list()
                for j in range(len(children[0])):
                    if children[0][j] != -1:
                        temp.append(children[0][j])
                # print("child1")
                # print(children[0])
                # insertparent2The number，Not withchild1Fixed conflicts
                cro_points = list()
                for j in range(len(children[0])):
                    if children[0][j] == -1:
                            cro_points.append(j)
                # print(len(cro_points))
                k = 0
                for j in range(len(parent2)):
                    if (parent2[j] not in temp) and (k != len(cro_points)-1):
                            children[0][cro_points[k]] = parent2[j]
                            k += 1
                # If there is still space after insertion
                for j in range(len(children[0])):
                    if children[0][j] == -1:
                        flag = True
                        while(flag):
                            temp_pos = random.sample(range(0,row*column),1)[0]
                            if temp_pos not in children[0]:
                                    children[0][j] = temp_pos
                                    flag = False
                # print(children[0])
                #child2
                for j in range(len(temp)):
                    if temp[j] in parent2:
                        children[1][parent2.index(temp[j])] = temp[j]
                # print("child2")
                # print(children[1])
                # insertparent1The number，Not withchild2Fixed conflicts
                cro_points_2 = list()
                for j in range(len(children[1])):
                    if children[1][j] == -1:
                            cro_points_2.append(j)
                # print(len(cro_points_2))
                k = 0
                for j in range(len(parent1)):
                    if (parent1[j] not in temp) and (k != len(cro_points_2)-1):
                            children[1][cro_points_2[k]] = parent1[j]
                            k += 1
                # If there is still space after insertion
                for j in range(len(children[1])):
                    if children[1][j] == -1:
                        flag = True
                        while(flag):
                            temp_pos = random.sample(range(0,row*column),1)[0]
                            if temp_pos not in children[1]:
                                children[1][j] = temp_pos
                                flag = False
                # print(children[1])   
                x = random.sample(range(0,2),1)[0]
                if x == 0:
                    child = children[0].copy()
                else:
                    child = children[1].copy()
                child = child.tolist()
            # TS    
            if (child not in ts_list) & (len(child) != 0):
                set_child=set(child)
                if (len(set_child)==len(child)):
                    child_pops.append(child)
                    flag = False
                    # print(child)
    while(len(child_pops) != popsize):
        temp_DNA = random.sample(range(0,row*column),len(parent1)) # Non-repeated sample
        if temp_DNA not in child_pops:
            child_pops.append(temp_DNA)
    return child_pops

def mutate_GATS(pops,ts_list,par_pops,row,column):
    """
    mutate with tabu list.

    Args:
        pops: Crossovered population.
        ts_list: tabu list.
        par_pops: Previous population.

    Return:
        pops_mutate: mutated population.
    """
    pops_mutate = []
    for i in range(len(pops)):
        flag = True
        while flag:
            pop = pops[i].copy()
            if random.random() < MUTATION_RATE:
                if np.random.rand() < 0.5:
                    t = random.randint(1,int(len(pop)/2))
                    count = 0
                    while count < t:
                        mut_pos1 = random.randint(0,len(pop)-1)
                        mut_pos2 = random.randint(0,len(pop)-1)
                        if mut_pos1 != mut_pos2:pop[mut_pos1],pop[mut_pos2] = pop[mut_pos2],pop[mut_pos1]
                        count +=1
                else:
                    empty_pos = np.zeros(row*column,dtype=int).tolist()
                    empty_list = list()
                    for j in range(len(pop)):
                        empty_pos[pop[j]] = 1
                    for j in range(len(empty_pos)):
                        if (empty_pos[j]==0):
                            empty_list.append(j)
                    if len(empty_list)!= 0:
                        # Number of vacancies for exchange
                        t = random.randint(1,len(empty_list))
                        # Select the vacant seatsindex
                        empty_index = random.sample(range(0, len(empty_list)), t)
                        # Select mutation point bits
                        mut_pos = random.sample(range(0, len(pop)), t)
                        # Correspondingly move to the vacant position
                        for j in range(t):
                            pop[mut_pos[j]] = empty_index[j]
            # TS
            if (pop not in ts_list):
                set_pop=set(pop)
                if (len(set_pop)==len(pop)):
                    pops_mutate.append(pop)
                    flag = False
    return pops_mutate