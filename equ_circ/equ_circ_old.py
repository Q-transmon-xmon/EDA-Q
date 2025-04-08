###############################################################################################
# File Name: equ_circ_old.py
# Description: This file provides functionality for generating and updating plasma circuits.
############################################################################################

from addict import Dict
import numpy as np
import matplotlib.pyplot as plt
from equ_circ.qucat import Network, GUI, L, J, C, R
from equ_circ import qucat
import os
import csv
import tkinter as tk
from tkinter import ttk


def generate_equ_circ(topology):
    """
    Generate an equivalent circuit.

    Input:
        topology: The topology structure, including qubit positions and connection relationships.

    Output:
        None.
    """
    print("Drawing equivalent circuit...")
    q_pos = topology.positions
    edge = topology.edges

    print(q_pos)

    file_path = 'process_options/circuits/M_N_topo.txt'
    folder_path = 'process_options/circuits'
    folder = os.path.exists(folder_path)
    if not folder:
        os.makedirs(folder_path)
    csv_path1 = 'process_options/circuits/q_data.csv'
    csv_path2 = 'process_options/circuits/r_data.csv'
    clear_file(file_path)
    clear_file(csv_path1)
    clear_file(csv_path2)

    for key in q_pos:
        print("key = {}".format(key))
        Qubit_circuit(q_pos[key][0] * 4, -q_pos[key][1] * 4, 65e-15, 14e-9, key)
    length = len(q_pos)
    adjacency_matrix = [[0 for _ in range(length)] for _ in range(length)]

    node_to_index = {node: index for index, node in enumerate(q_pos.keys())}
    for edge in edge:
        node1, node2 = edge
        index1, index2 = node_to_index[node1], node_to_index[node2]
        adjacency_matrix[index1][index2] = 1
    rows = len(adjacency_matrix)
    cols = len(adjacency_matrix[0])
    for j in range(rows):
        for k in range(cols):
            if adjacency_matrix[j][k] == 1:
                if q_pos[str('q') + str(j)][1] == q_pos[str('q') + str(k)][1]:
                    if q_pos[str('q') + str(j)][0] < q_pos[str('q') + str(k)][0]:
                        link_circuit_Parallel_positive(q_pos[str('q') + str(j)][0] * 4,
                                                       -q_pos[str('q') + str(j)][1] * 4, j)
                    else:
                        link_circuit_Parallel_negative(q_pos[str('q') + str(j)][0] * 4,
                                                       -q_pos[str('q') + str(j)][1] * 4, j)
                if q_pos[str('q') + str(j)][0] == q_pos[str('q') + str(k)][0]:
                    if q_pos[str('q') + str(j)][1] > q_pos[str('q') + str(k)][1]:
                        link_circuit_Vertical_positive(q_pos[str('q') + str(j)][0] * 4,
                                                       -q_pos[str('q') + str(j)][1] * 4, j)
                    else:
                        link_circuit_Vertical_negative(q_pos[str('q') + str(j)][0] * 4,
                                                       -q_pos[str('q') + str(j)][1] * 4, j)
    print("woiehfowenfoiwefoi")
    cir = GUI('process_options/circuits/M_N_topo.txt',
              edit=True,
              plot=True,
              print_network=False
              )
    if update_qubit() == 1:
        update_qubit()
        cir = GUI('process_options/circuits/M_N_topo.txt',
                  edit=True,
                  plot=True,
                  print_network=False
                  )
    if update_res() == 1:
        update_res()
        cir = GUI('process_options/circuits/M_N_topo.txt',
                  edit=True,
                  plot=True,
                  print_network=False
                  )
    return


def Qubit_circuit(x1, y1, Cq, Lj, num):
    """
    Generate a qubit circuit.

    Input:
        x1, y1: Qubit position.
        Cq, Lj: Capacitance and inductance values.
        num: Qubit number.

    Output:
        None.
    """
    with open('process_options/circuits/M_N_topo.txt', 'a') as file:
        file.write("C;" +
                   str(x1) + "," + str(y1) + ";" +
                   str(x1) + "," + str(y1 + 1) + ";" +
                   str(Cq) + ";" +
                   "C" + str(num)
                   + "\n" + "J;" +
                   str(x1 + 1) + "," + str(y1) + ";" +
                   str(x1 + 1) + "," + str(y1 + 1) + ";" +
                   str(Lj) + ";" +
                   "L" + str(num)
                   + "\n" + "W;" +
                   str(x1) + "," + str(y1) + ";" +
                   str(x1 + 1) + "," + str(y1) + ";" + ";" +
                   "\n" + "W;" +
                   str(x1) + "," + str(y1 + 1) + ";" +
                   str(x1 + 1) + "," + str(y1 + 1) + ";" + ";" +
                   "\n" + "G;" +
                   str(x1 + 1) + "," + str(y1 + 2) + ";" +
                   str(x1 + 1) + "," + str(y1 + 1) + ";" + ";" +
                   "\n"
                   )
        file.close
    data = (num, (x1, y1), Cq * 10 ** 15, Lj * 10 ** 9)
    with open('process_options/circuits/q_data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)


def Resonator_circuit(x1, y1, Cr, Lr, num):
    """
    Generate a resonator circuit.

    Input:
        x1, y1: Resonator position.
        Cr, Lr: Capacitance and inductance values.
        num: Resonator number.

    Output:
        None.
    """
    with open('process_options/circuits/M_N_topo.txt', 'a') as file:
        file.write("C;" +
                   str(x1) + "," + str(y1) + ";" +
                   str(x1) + "," + str(y1 + 1) + ";" +
                   str(Cr) + ";" +
                   "Cr" + str(num)
                   + "\n" + "L;" +
                   str(x1 + 1) + "," + str(y1) + ";" +
                   str(x1 + 1) + "," + str(y1 + 1) + ";" +
                   str(Lr) + ";" +
                   "Lr" + str(num)
                   + "\n" + "W;" +
                   str(x1) + "," + str(y1) + ";" +
                   str(x1 + 1) + "," + str(y1) + ";" + ";" +
                   "\n" + "W;" +
                   str(x1) + "," + str(y1 + 1) + ";" +
                   str(x1 + 1) + "," + str(y1 + 1) + ";" + ";" +
                   "\n" + "G;" +
                   str(x1 + 1) + "," + str(y1 + 2) + ";" +
                   str(x1 + 1) + "," + str(y1 + 1) + ";" + ";" +
                   "\n"
                   )
        file.close
    data = ('r' + str(num), (x1, y1), Cr * 10 ** 15, Lr * 10 ** 9)
    with open('process_options/circuits/r_data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)


def C_Vertical_circuit(x1, y1, Cc):
    """
    Generate a vertical capacitor circuit.

    Input:
        x1, y1: Position.
        Cc: Capacitance value.

    Output:
        None.
    """
    with open('process_options/circuits/M_N_topo.txt', 'a') as file:
        file.write("C;" +
                   str(x1) + "," + str(y1) + ";" +
                   str(x1) + "," + str(y1 + 1) + ";" +
                   str(Cc) + ";" +
                   "Cc"
                   + "\n"
                   )
        file.close


def C_Parallel_circuit(x1, y1, Cc):
    """
    Generate a parallel capacitor circuit.

    Input:
        x1, y1: Position.
        Cc: Capacitance value.

    Output:
        None.
    """
    with open('process_options/circuits/M_N_topo.txt', 'a') as file:
        file.write("C;"
                   + str(x1) + "," + str(y1) + ";"
                   + str(x1 + 1) + "," + str(y1) + ";"
                   + str(Cc) + ";"
                   + "Cc"
                   + "\n"
                   )
        file.close


def link_circuit_Parallel_positive(x1, y1, num):
    """
    Generate a positive parallel link circuit.

    Input:
        x1, y1: Position.
        num: Number.

    Output:
        None.
    """
    C_Parallel_circuit(x1 + 1, y1, 6e-15)
    Resonator_circuit(x1 + 2, y1, 65e-15, 21e-9, str(num) + str(1))
    C_Parallel_circuit(x1 + 3, y1, 6e-15)


def link_circuit_Parallel_negative(x1, y1, num):
    """
    Generate a negative parallel link circuit.

    Input:
        x1, y1: Position.
        num: Number.

    Output:
        None.
    """
    C_Parallel_circuit(x1 - 1, y1, 6e-15)
    Resonator_circuit(x1 - 2, y1, 65e-15, 21e-9, str(num) + str(2))
    C_Parallel_circuit(x1 - 3, y1, 6e-15)


def link_circuit_Vertical_negative(x1, y1, num):
    """
    Generate a negative vertical link circuit.

    Input:
        x1, y1: Position.
        num: Number.

    Output:
        None.
    """
    C_Vertical_circuit(x1, y1 - 1, 6e-15)
    Resonator_circuit(x1, y1 - 2, 65e-15, 21e-9, str(num) + str(3))
    C_Vertical_circuit(x1, y1 - 3, 6e-15)


def link_circuit_Vertical_positive(x1, y1, num):
    """
    Generate a positive vertical link circuit.

    Input:
        x1, y1: Position.
        num: Number.

    Output:
        None.
    """
    C_Vertical_circuit(x1, y1 + 1, 6e-15)
    Resonator_circuit(x1, y1 + 2, 65e-15, 21e-9, str(num) + str(4))
    C_Vertical_circuit(x1, y1 + 3, 6e-15)


def clear_file(file_path):
    """
    Clear the content of a file.

    Input:
        file_path: File path.

    Output:
        None.
    """
    if os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.truncate(0)


def update_qubit():
    """
    Update qubit parameters.

    Input:
        None.

    Output:
        Update flag.
    """
    update = 0
    with open('process_options/circuits/M_N_topo.txt', 'r') as file:
        data = file.readlines()

    data_list = [line.strip().split(';') for line in data]

    choice = input("Do you want to modify the capacitance value of a qubit? (y/n): ")

    if choice.lower() == 'y':
        file_path = 'process_options/circuits/q_data.csv'
        create_table_from_csv(file_path)
        bit_to_modify = input("Please select the qubit to modify, e.g., q0, q1: ")
        new_value = input(f"Please enter the new capacitance value for {bit_to_modify.lower()} (in fF): ")

        index_to_modify = -1
        for i, item in enumerate(data_list):
            if len(item) > 1 and item[0] == 'C' and item[-1] == f'C{bit_to_modify.lower()}':
                index_to_modify = i
                break

        if index_to_modify != -1:
            data_list[index_to_modify][3] = str(int(new_value) * 10 ** -15)
            update_csv_cell(file_path, str(bit_to_modify), 2, new_value)
            print(f"The capacitance value of {bit_to_modify.lower()} has been successfully updated.")
        else:
            print(f"No corresponding line found for {bit_to_modify.lower()} to modify.")

        with open('process_options/circuits/M_N_topo.txt', 'w') as file:
            for item in data_list:
                file.write(';'.join(item) + '\n')
        update = 1
    else:
        print("No modifications were made.")
    return update


def update_res():
    """
    Update resonator parameters.

    Input:
        None.

    Output:
        Update flag.
    """
    update = 0
    with open('process_options/circuits/M_N_topo.txt', 'r') as file:
        data = file.readlines()

    data_list = [line.strip().split(';') for line in data]

    choice = input("Do you want to modify the design value of a resonator? (y/n): ")

    if choice.lower() == 'y':
        file_path = 'process_options/circuits/r_data.csv'
        create_table_from_csv(file_path)
        bit_to_modify = input("Please select the resonator to modify, e.g., r01, r11: ")
        param_to_modify = input(
            f"Please enter the parameter name to modify for {bit_to_modify} (C for capacitance, L for inductance): ")
        if param_to_modify.lower() == 'c':
            new_value = input(f"Please enter the new capacitance value for {bit_to_modify} (in fF): ")

            index_to_modify = -1
            for i, item in enumerate(data_list):
                if len(item) > 1 and item[0] == 'C' and item[-1] == f'C{bit_to_modify}':
                    index_to_modify = i
                    break

            if index_to_modify != -1:
                data_list[index_to_modify][3] = str(int(new_value) * 10 ** -15)
                update_csv_cell(file_path, str(bit_to_modify), 2, new_value)
                print(f"The capacitance value of {bit_to_modify} has been successfully updated.")
            else:
                print(f"No corresponding line found for {bit_to_modify} to modify.")
        elif param_to_modify.lower() == 'l':
            new_value = input(f"Please enter the new inductance value for {bit_to_modify} (in nH): ")

            index_to_modify = -1
            for i, item in enumerate(data_list):
                if len(item) > 1 and item[0] == 'L' and item[-1] == f'L{bit_to_modify}':
                    index_to_modify = i
                    break

            if index_to_modify != -1:
                data_list[index_to_modify][3] = str(int(new_value) * 10 ** -9)
                update_csv_cell(file_path, str(bit_to_modify), 3, new_value)
                print(f"The inductance value of {bit_to_modify} has been successfully updated.")
            else:
                print(f"No corresponding line found for {bit_to_modify} to modify.")

        with open('process_options/circuits/M_N_topo.txt', 'w') as file:
            for item in data_list:
                file.write(';'.join(item) + '\n')
        update = 1
    else:
        print("No modifications were made.")
    return update


def create_table_from_csv(file_path):
    """
    Create a table from a CSV file.

    Input:
        file_path: CSV file path.

    Output:
        None.
    """
    data = []
    with open(file_path, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)

    root = tk.Tk()
    root.title("File Content Table")

    tree = ttk.Treeview(root, columns=tuple("col" + str(i + 1) for i in range(len(data[0]))), show="headings")

    column_names = ["Name", "Coordinates", "C (Capacitance)", "L (Inductance)"]
    for i in range(len(data[0])):
        tree.heading("col" + str(i + 1), text=column_names[i])

    for row in data:
        if len(row) == len(data[0]):
            tree.insert("", "end", values=row)
        else:
            print(f"Data row {row} has a different number of columns than specified in the table")

    tree.pack()
    root.mainloop()


def update_csv_cell(file_path, target_row, target_column, new_value):
    """
    Update a cell in a CSV file.

    Input:
        file_path: CSV file path.
        target_row: Target row.
        target_column: Target column.
        new_value: New value.

    Output:
        None.
    """
    data = []
    with open(file_path, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)

    # Find the index of the target row
    target_row_index = -1
    for i, row in enumerate(data):
        if target_row in row:
            target_row_index = i
            break

    if target_row_index != -1:
        data[target_row_index][target_column] = new_value

    # Write the updated content back to the CSV file
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)