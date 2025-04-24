from addict import Dict
from qiskit import QuantumCircuit
import os, xlrd, xlwt, math, itertools, random, toolbox, copy
import numpy as np, networkx as nx, matplotlib.pyplot as plt, seaborn as sns
from func_modules.topo.gene_topo_ops.qasm import GA_steps

def generate_individual(Q_NUM,row,column):
    """
        Generate individual.

        Args:
            Q_NUM(int): Qubit Number.

        Return:
            individual
    """
    # Disregarding the case where the number of qubits is 1.
    if Q_NUM == 1:
        print("Too few qubits number!")
        return
    else:
        individual = random.sample(range(0,row*column),Q_NUM)
    return individual

def export_to_excel(best_pop_list,min_fitness_list,filepath):
    """
       Export the algorithm results to excel.
    """
    xls=xlwt.Workbook()
    sht1=xls.add_sheet('sheet1')
    sht1.write(0,0,"position")
    sht1.write(0,1,"min_fitness_list")
    i=1
    for j in range(len(best_pop_list)):
        sht1.write(i,0,str(list(best_pop_list[j])))
        sht1.write(i,1,str(min_fitness_list[j]))
        i=i+1
    xls.save(filepath)
    print("迭代信息保存在{}".format(filepath))
    return

def generate_standard_coordinate(row,col):
    """
        Generate coordinates list.

        Args:
            M: row.
            N: column.

        Return:
            standard_coordinate: Standard coordinates list.
    """
    standard_coordinate = []
    for i in range(row): # row
        for j in range(col): # column
            standard_coordinate.append([j,i]) # Rectangular coordinate system
    return standard_coordinate

def get_coupling_list(circuit):
    """
    Get coupling degree list.

    Args:
        circuit(QuantumCircuit): Quantum circuit of the quantum program.

    Return:
        coupling_list(list): Qubit pairs in the program, which have cx two-qubit gates.
    """
    circuit = circuit.decompose().decompose()
    coupling_list = []
    for instr,a,b in circuit._data:
        if instr.name == 'barrier' or instr.name == 'measure':
            continue
        if instr.num_qubits>1:
            i=0
            l=[]
            for _ in range(instr.num_qubits):
                l.append(a[i].index)
                i=i+1
            coupling_list.append(l)
    return coupling_list

def convert_format(pos, edge):
    qubits_num = len(pos)
    new_pos = []
    new_edge = []
    for k, v in pos.items():
        new_pos.append(v)
    for i in range(0, qubits_num):
        for j in range(i+1, qubits_num):
            if edge[i][j] == 1:
                new_edge.append([pos[i], pos[j]])
    # supportnumpy.int32Convert data type toint
    new_pos1 = Dict()
    for i in range(0, qubits_num):
        topo_pos = copy.deepcopy(pos[i])
        topo_pos[0] = int(topo_pos[0])
        topo_pos[1] = int(topo_pos[1])
        new_pos1["q"+str(i)] = copy.deepcopy(topo_pos)
    new_edge1 = []
    for edge in new_edge:
        pos1 = edge[0]
        pos2 = edge[1]
        new_edge1.append([[int(pos1[0]), int(pos1[1])], [int(pos2[0]), int(pos2[1])]])

    new_edge2 = []
    for edge in new_edge1:
        pos1 = edge[0]
        pos2 = edge[1]
        for q_name, topo_pos in new_pos1.items():
            if topo_pos == pos1:
                q0 = q_name
            elif topo_pos == pos2:
                q1 = q_name
        new_edge2.append([q0, q1])

    return copy.deepcopy(new_pos1), copy.deepcopy(new_edge2)

def get_coupling_degree_matrix(circuit,qp_name:str, matrix_path:str):
    """
    Get coupling degree matrix M.

    Args:
        circuit(QuantumCircuit): Quantum circuit of the quantum program.
        qp_name(str): Name of the quantum program. 

    Return:
        Coupling Degree Matrix M
    """

    print("生成耦合度矩阵...")
    QNUM = len(circuit._qubits) # Qubit Number
    coupling_list = get_coupling_list(circuit) # coupling degree list

    # Build coupling degree matrix M.
    M = np.zeros((QNUM,QNUM),int)
    M=np.asarray(M)
    for i in range(len(coupling_list)):
        coupling_tuple_list = list(itertools.combinations(coupling_list[i], 2))
        for item in coupling_tuple_list:
            x1 = item[0]
            x2 = item[1]
            M[x1][x2]=M[x1][x2]+1
            M[x2][x1]=M[x2][x1]+1
    dpi =300
    fig = plt.figure(dpi=dpi,figsize=(25.6, 14.4))
    # Show coupling degree matrix M.
    ax=sns.heatmap(M,annot=True,center=9)
    #plt.show()
    '''
    # Save
    if not os.path.exists('./image'):
        os.makedirs('./image')
    heat_map_path = f'./image/{qp_name}_heat_map.png'
    '''
    toolbox.jg_and_create_path(matrix_path)
    plt.savefig(matrix_path)
    plt.clf()
    # print("The coupling degree matrixheatmapSave in{}".format(f'./image/{qp_name}_heat_map.png'))
    print("耦合度矩阵的heatmap保存在{}".format(matrix_path))
    return M

def processor_architecture_qubits_pos_draw(processor_architecture_layout_path,pos):
    """
       draw qubits position
    """
    try:
        dpi =300
        fig = plt.figure(dpi=dpi,figsize=(25.6, 14.4))
        G = nx.Graph()
        point = list(pos.keys())
        G.add_nodes_from(point)
        nlabels = dict(zip(point, point))
        nx.draw_networkx_nodes(G, pos, node_size=350, node_color="#6cb6ef")
        nx.draw_networkx_labels(G, pos, nlabels)
        plt.axis("equal")
        toolbox.jg_and_create_path(processor_architecture_layout_path)
        plt.savefig(processor_architecture_layout_path)
        # plt.show()
    except:
        print("..")

def processor_architecture_draw(processor_architecture_path,pos,edges):
    """
       draw processor architecture
    """
    try:
        G = nx.Graph()
        point = list(pos.keys())
        G.add_nodes_from(point)
        loc_all = list(pos.values())
        G.add_edges_from(loc_all)
        nlabels = dict(zip(point, point))
        edgesT = []
        length = len(pos)
        for i in range(length):
            for j in range(i + 1, length):
                key = edges[i][j]
                if key == 1:
                    edgesT.append((i, j))
        nx.draw_networkx_nodes(G, pos,node_size=750, node_color="#6cb6ef") 
        nx.draw_networkx_edges(G, pos, edgesT)
        nx.draw_networkx_labels(G, pos, nlabels)
        plt.axis("equal")
        toolbox.jg_and_create_path(processor_architecture_path)
        plt.savefig(processor_architecture_path)
        # plt.show()
    except:
        print("..")

def PAD_GATS(topo_convergence_path,qp_name:str,M,path, row: int = None, col: int = None):
    """
    Use GATS to get processor architecture.

    Args:
        qp_name(str): Name of the quantum program. 
        M: Coupling Degree Matrix.
        path: Store path of iteration results.

    Return:
        path: Path of processor architecture.
    """

    print("遗传算法迭代...")
   
    path = path+qp_name+'_GATS'+'.xls'
    Q_NUM=len(M) # Qubit Number

    '''
    # Create the activity adjacency matrix.
    edge_matrix = M.copy()
    '''
    
    # Genetic Algorithm(GA) parameters
    POP_SIZE = 100           # population size 
    N_GENERATIONS = 15      # iterations
    TOURNAMENT_SIZE = 3      # tournament selection

    # Tabu Search(TS) parameters
    ts_length = Q_NUM*(Q_NUM-1)/2  # tabu length
    ts_list = []                   # tabu list
    ts_time = []                   # tabu time

    # Initialize population
    row = row
    column = col
    if row is None and col is None:
        column = math.ceil(math.sqrt(Q_NUM))
        row = math.ceil(Q_NUM/column)
        print("默认拓扑的行数为{}，列数为{}".format(row, column))
    elif row is None:
        row = math.ceil(Q_NUM/column)
        print("计算得拓扑的行数为{}，列数为{}".format(row, column))
    elif column is None:
        column = math.ceil(Q_NUM/row)
        print("计算得拓扑的行数为{}，列数为{}".format(row, column))

    standard_coordinate = generate_standard_coordinate(row,column)
    pop = np.zeros((POP_SIZE,Q_NUM),dtype=int).tolist()
    for i in range(POP_SIZE):
        flag = True
        while flag:
            temp_individual = generate_individual(Q_NUM,row,column)
            if temp_individual not in pop:
                for j in range(Q_NUM):
                    pop[i][j] = temp_individual[j]
                flag = False

    # population fitness value
    fitness = np.zeros((POP_SIZE,1),dtype=float)
    fitness = GA_steps.get_fitness(pop,M,standard_coordinate,row,column).tolist()
   
    # Keep current optimal
    best_fit = min(fitness)
    best_pop = pop[fitness.index(best_fit)].copy()

    # Tabu
    ts_list.append(best_pop)
    ts_time.append(ts_length)

    best_fit_list = list()
    best_fit_list.append(best_fit[0])

    best_pop_list = list()
    best_pop_list.append(best_pop)

    for iteration in range(N_GENERATIONS-1):
        # select
        pop1 = GA_steps.tournament_select(pop,POP_SIZE,fitness,TOURNAMENT_SIZE)
        pop2 = GA_steps.tournament_select(pop,POP_SIZE,fitness,TOURNAMENT_SIZE)

        # crossover
        child_pops = GA_steps.crossover_GATS(POP_SIZE,pop1,pop2,ts_list,row,column)
        # mutate
        child_pops = GA_steps.mutate_GATS(child_pops,ts_list,pop,row,column)

        child_fits = [None]*POP_SIZE
        child_fits = GA_steps.get_fitness(child_pops,M,standard_coordinate,row,column)

        # compete
        for i in range(POP_SIZE):
            if fitness[i] > child_fits[i]:
                fitness[i] = child_fits[i]
                pop[i] = child_pops[i].copy()

        # update tabu list
        ts_time = [x-1 for x in ts_time]
        if 0 in ts_time:
            ts_list.remove(ts_list[ts_time.index(0)])
            ts_time.remove(0)

        # update optimal
        if best_fit>=min(fitness):
            best_fit = min(fitness)
            best_pop = pop[fitness.index(best_fit)]

        # add tabu
        ts_list.append(best_pop)
        ts_time.append(ts_length)
            
        best_fit_list.append(best_fit[0])
        best_pop_list.append(best_pop)
        # print('%d:optimal value %.1f' % (iteration+2, best_fit[0]))

    export_to_excel(best_pop_list,best_fit_list,path)
    
    # show convergence
    abscissa = np.arange(1,N_GENERATIONS+1)
    l1,= plt.plot(abscissa,best_fit_list,color='r',marker='o')
    plt.xlabel("number of iterations")
    plt.ylabel("fitness")
    plt.legend(handles=[l1,],labels=['GATS',],loc=1)
    toolbox.jg_and_create_path(topo_convergence_path)
    plt.savefig(topo_convergence_path)
    # plt.show()
    plt.clf()
    print("适应度收敛结果保存在{}".format(topo_convergence_path))

    return path,row,column,standard_coordinate 

def qasm_to_topo(qasm_path,
                 row,
                 col,
                 matrix_path,
                 topo_convergence_path,
                 qubit_layout_path,
                 topo_pruning_path,
                 final_topo_path):
    """
    Get processor architecture.

    Return:
        pos, actual_edge2: layout and connections of processor architecture.
    """
    qasm_path = copy.deepcopy(qasm_path)
    topo_ops = Dict()

    # Read the quantum program file.
    f=open(qasm_path)
    code=f.read()
    # Using qiskit to construct quantum circuit.
    circuit=QuantumCircuit.from_qasm_str(code)
    file_name, file_extension = toolbox.get_file_name_from_path(qasm_path)
    # Build coupling degree matrix M.
    M = get_coupling_degree_matrix(circuit, file_name, matrix_path)
    # Store path of iteration results
    if not os.path.exists('./excel'):
        os.makedirs('./excel')
    path_excel='./excel/'

    # Processor Architecture Design
    path_of_architecture_result,row,col,standard_coordinate  = PAD_GATS(topo_convergence_path,file_name,M,path_excel, row, col)

    # show processor architecture
    workbook = xlrd.open_workbook(path_of_architecture_result)
    sheet1 = workbook.sheet_by_index(0)
    num=sheet1.nrows-1
    example=sheet1.cell(num,0).value
    # position = [int(example[i]) for i in range(len(example)) if example[i] not in ['[', ']', ',', ' ']]
    position=eval(example)
    Q_NUM = len(M)
    DNA = np.zeros((Q_NUM*2),dtype=int)
    for i in range(len(position)):
        DNA[i*2]= standard_coordinate[int(position[i])][0]
        DNA[i*2+1]= standard_coordinate[int(position[i])][1]

    node_index = 0  #Starting point of standard serial number
    # Create a complete grid diagram
    G_complete = nx.grid_graph(dim=[row, col], periodic=False)
    DNA_set = set(tuple(pair) for pair in zip(DNA[0::2], DNA[1::2]))
    G_complete_set = set(list(G_complete.nodes()))
    unused_nodes_set = G_complete_set.difference(DNA_set)
    for i in unused_nodes_set:
        G_complete.remove_node(i)

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
                if M[i][j] != 0 and GA_steps.get_distance(v1, v2) == 1:
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
                if d_S!=GA_steps.get_distance(v1, v2):
                    # Need to add edges.
                    a_path=nx.shortest_path(G_complete,(v1[0],v1[1]),(v2[0],v2[1]))
                    for k in range(len(a_path)-1):
                        G.add_edge(pos_q[a_path[k]], pos_q[a_path[k+1]])
                        actual_edge2[pos_q[a_path[k]]][pos_q[a_path[k+1]]]=1
                        actual_edge2[pos_q[a_path[k+1]]][pos_q[a_path[k]]]=1
    
    processor_architecture_qubits_pos_draw(qubit_layout_path,q_pos)
    plt.clf()
    
    processor_architecture_draw(topo_pruning_path,q_pos,actual_edge1)
    plt.clf()

    processor_architecture_draw(final_topo_path,q_pos,actual_edge2)
    plt.clf()
      
    # Interface with the new architecture

    poss, edges = convert_format(q_pos, actual_edge2)
    topo_ops.positions = poss
    topo_ops.edges = edges
    topo_ops.col_num = col
    topo_ops.row_num = row

    return copy.deepcopy(topo_ops)