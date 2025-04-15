#########################################################################
# File Name: primitives.py
# Description: Used to generate equivalent circuit files and modify circuit parameters.
#              Includes functions to generate equivalent circuit files, modify qubit parameters,
#              and modify coupling cavity parameters.
#########################################################################

import toolbox
import csv
import os
from equ_circ.qucat import Network, GUI, L, J, C, R
from equ_circ import qucat
import numpy as np

e = 1.60217657e-19  # Elementary charge
h = 6.62606957e-34  # Planck's constant
hbar = 1.0545718E-34  # Reduced Planck's constant


def generate_equ_circ_files(topo_ops, txt_path, qcsv_path, rcsv_path):
    """
    Generate equivalent circuit txt file, qubit csv file, and coupling cavity csv file.

    Input:
        topo_ops: Object containing topology operation information.
        txt_path: String, path to the txt file.
        qcsv_path: String, path to the qubit csv file.
        rcsv_path: String, path to the coupling cavity csv file.

    Output:
        None
    """
    print("Drawing equivalent circuit...")
    q_pos = topo_ops.positions
    edge = topo_ops.edges

    toolbox.jg_and_create_path(txt_path)
    toolbox.jg_and_create_path(qcsv_path)
    toolbox.jg_and_create_path(rcsv_path)

    toolbox.clear_file(txt_path)
    toolbox.clear_file(qcsv_path)
    toolbox.clear_file(rcsv_path)

    for key in q_pos:
        Qubit_circuit(q_pos[key][0] * 4, -q_pos[key][1] * 4, 65e-15, 14e-9, key, txt_path, qcsv_path)
    # Create a 2D list of appropriate size
    length = len(q_pos)
    adjacency_matrix = [[0 for _ in range(length)] for _ in range(length)]

    # Get the mapping from node names to indices
    node_to_index = {node: index for index, node in enumerate(q_pos.keys())}

    # Fill the adjacency matrix based on connection relationships
    for edge in edge:
        node1, node2 = edge
        index1, index2 = node_to_index[node1], node_to_index[node2]
        adjacency_matrix[index1][index2] = 1
    rows = len(adjacency_matrix)
    cols = len(adjacency_matrix[0])
    for j in range(rows):
        for k in range(cols):
            # if j > k:
            if adjacency_matrix[j][k] == 1:
                # print(f"({j}, {k})")
                if q_pos[str('q') + str(j)][1] == q_pos[str('q') + str(k)][1]:
                    if q_pos[str('q') + str(j)][0] < q_pos[str('q') + str(k)][0]:
                        link_circuit_Parallel_positive(q_pos[str('q') + str(j)][0] * 4,
                                                       -q_pos[str('q') + str(j)][1] * 4, str(k) + str(j), txt_path,
                                                       rcsv_path)
                    else:
                        link_circuit_Parallel_negative(q_pos[str('q') + str(j)][0] * 4,
                                                       -q_pos[str('q') + str(j)][1] * 4, str(k) + str(j), txt_path,
                                                       rcsv_path)
                if q_pos[str('q') + str(j)][0] == q_pos[str('q') + str(k)][0]:
                    if q_pos[str('q') + str(j)][1] > q_pos[str('q') + str(k)][1]:
                        link_circuit_Vertical_positive(q_pos[str('q') + str(j)][0] * 4,
                                                       -q_pos[str('q') + str(j)][1] * 4, str(k) + str(j), txt_path,
                                                       rcsv_path)
                    else:
                        link_circuit_Vertical_negative(q_pos[str('q') + str(j)][0] * 4,
                                                       -q_pos[str('q') + str(j)][1] * 4, str(k) + str(j), txt_path,
                                                       rcsv_path)

    return


def change_qubit_options(txt_path, qcsv_path, qubit_name, value):
    """
    Modify qubit parameters.

    Input:
        txt_path: String, path to the txt file.
        qcsv_path: String, path to the qubit csv file.
        qubit_name: String, name of the qubit.
        value: Float, new parameter value.

    Output:
        None
    """
    with open(txt_path, 'r') as file:
        data = file.readlines()

    # Convert file content to a list
    data_list = [line.strip().split(';') for line in data]

    index_to_modify = -1
    for i, item in enumerate(data_list):
        if len(item) > 1 and item[0] == 'C' and item[-1] == f'C{qubit_name.lower()}':
            index_to_modify = i
            break
    if index_to_modify != -1:
        # Update data
        data_list[index_to_modify][3] = str(round(float(value) * 10 ** -15, 17))
        # Update information in the csv file
        update_csv_cell_qubit(qcsv_path, str(qubit_name), 2, value)
        print(f"{qubit_name.lower()}的电容值已成功更新。")

    else:
        print(f"未找到要修改的{qubit_name.lower()}对应的行。")

    with open(txt_path, 'w') as file:
        for item in data_list:
            file.write(';'.join(item) + '\n')

    return


def change_coupling_options(txt_path, rcsv_path, coupling_line_name, op_name, op_value):
    """
    Modify coupling cavity parameters.

    Input:
        txt_path: String, path to the txt file.
        rcsv_path: String, path to the coupling cavity csv file.
        coupling_line_name: String, name of the coupling cavity.
        op_name: String, name of the parameter to modify.
        op_value: Float, new parameter value.

    Output:
        None
    """
    with open(txt_path, 'r') as file:
        data = file.readlines()

    # Convert file content to a list
    data_list = [line.strip().split(';') for line in data]
    if op_name.lower() == 'c':
        # Find the index of the line to modify
        index_to_modify = -1
        for i, item in enumerate(data_list):
            if len(item) > 1 and item[0] == 'C' and item[-1] == f'C{coupling_line_name}':
                index_to_modify = i
                break

        # If the line to modify is found
        if index_to_modify != -1:
            # Update data
            data_list[index_to_modify][3] = str(round(float(op_value) * 10 ** -15, 17))
            # Update information in the csv file
            update_csv_cell_resonator(rcsv_path, str(coupling_line_name), 2, op_value)
            print(f"{coupling_line_name}的电容值已成功更新。")
        else:
            print(f"未找到要修改的{coupling_line_name}对应的行。")
    elif op_name.lower() == 'l':
        # Find the index of the line to modify
        index_to_modify = -1
        for i, item in enumerate(data_list):
            if len(item) > 1 and item[0] == 'L' and item[-1] == f'L{coupling_line_name}':
                index_to_modify = i
                break

        # If the line to modify is found
        if index_to_modify != -1:
            # Update data
            data_list[index_to_modify][3] = str(round(float(op_value) * 10 ** -9, 11))
            # Update information in the csv file
            update_csv_cell_resonator(rcsv_path, str(coupling_line_name), 3, op_value)
            print(f"{coupling_line_name}的电感值已成功更新。")

        else:
            print(f"未找到要修改的{coupling_line_name}对应的行。")

    with open(txt_path, 'w') as file:
        for item in data_list:
            file.write(';'.join(item) + '\n')

    return


def find_qubit_options(qcsv_path, qubit_name):
    """
    Query qubit parameters.

    Input:
        qcsv_path: String, path to the qubit csv file.
        qubit_name: String, name of the qubit.

    Output:
        Parameter value, or None if not found.
    """
    with open(qcsv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == qubit_name:
                return float(row[2])  # Return the third column data (index 2)

    return None  # Return None if no corresponding data is found


def find_coupling_options(rcsv_path, coupling_line_name, op_name):
    """
    Query coupling cavity parameters.

    Input:
        rcsv_path: String, path to the coupling cavity csv file.
        coupling_line_name: String, name of the coupling cavity.
        op_name: String, name of the parameter to query.

    Output:
        Parameter value, or None if not found.
    """
    with open(rcsv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if op_name == 'c' and row[0] == coupling_line_name:
                return float(row[2])
            elif op_name == 'l' and row[0] == coupling_line_name:
                return float(row[3])

    return None  # Return None if no corresponding data is found


def display_equ_circ(txt_path):
    """
    Display the equivalent circuit editor.

    Input:
        txt_path: String, path to the txt file.

    Output:
        None
    """
    cir = GUI(txt_path,  # Location of the circuit file
              edit=True,  # Open the GUI to edit the circuit
              plot=True,  # Plot the circuit after editing
              print_network=False  # Do not print the network
              )
    return


def save_equ_circ_image(txt_path, image_path):
    """
    Save the equivalent circuit image.

    Input:
        txt_path: String, path to the txt file.
        image_path: String, path to save the image.

    Output:
        None
    """
    return


def Qubit_circuit(x1, y1, Cq, Lj, num, txt_path, qcsv_path):  # x1,y1,C_value,J_value
    """
    Generate txt and csv files for the qubit circuit.

    Input:
        x1: Float, x-coordinate of the qubit.
        y1: Float, y-coordinate of the qubit.
        Cq: Float, capacitance value of the qubit.
        Lj: Float, inductance value of the qubit.
        num: String or integer, qubit number.
        txt_path: String, path to the txt file.
        qcsv_path: String, path to the qubit csv file.

    Output:
        None
    """
    with open(txt_path, 'a') as file:
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

    Ec = e ** 2 / 2 / Cq / hbar

    data = (num, (x1, y1), Cq * 10 ** 15, Lj * 10 ** 9, round(Ec / 2 / np.pi / 1e6, 2))
    # Write data to the CSV file in a loop
    with open(qcsv_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)


def Resonator_circuit(x1, y1, Cr, Lr, num, txt_path, rcsv_path):  # x1,y1,C_value,J_value
    """
    Generate txt and csv files for the coupling cavity circuit.

    Input:
        x1: Float, x-coordinate of the coupling cavity.
        y1: Float, y-coordinate of the coupling cavity.
        Cr: Float, capacitance value of the coupling cavity.
        Lr: Float, inductance value of the coupling cavity.
        num: String or integer, coupling cavity number.
        txt_path: String, path to the txt file.
        rcsv_path: String, path to the coupling cavity csv file.

    Output:
        None
    """
    with open(txt_path, 'a') as file:
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
        # file.close

    data = ('r' + str(num), (x1, y1), Cr * 10 ** 15, Lr * 10 ** 9)
    # Write data to the CSV file in a loop
    with open(rcsv_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)


def C_Vertical_circuit(x1, y1, Cc, txt_path):
    """
    Generate a vertical capacitor circuit.

    Input:
        x1: Float, x-coordinate of the capacitor.
        y1: Float, y-coordinate of the capacitor.
        Cc: Float, capacitance value.
        txt_path: String, path to the txt file.

    Output:
        None
    """
    with open(txt_path, 'a') as file:
        file.write("C;" +
                   str(x1) + "," + str(y1) + ";" +
                   str(x1) + "," + str(y1 + 1) + ";" +
                   str(Cc) + ";" +
                   "Cc" +
                   "\n"
                   )

        file.close


def C_Parallel_circuit(x1, y1, Cc, txt_path):
    """
    Generate a parallel capacitor circuit.

    Input:
        x1: Float, x-coordinate of the capacitor.
        y1: Float, y-coordinate of the capacitor.
        Cc: Float, capacitance value.
        txt_path: String, path to the txt file.

    Output:
        None
    """
    with open(txt_path, 'a') as file:
        file.write("C;" +
                   str(x1) + "," + str(y1) + ";" +
                   str(x1 + 1) + "," + str(y1) + ";" +
                   str(Cc) + ";" +
                   "Cc" +
                   "\n"
                   )
        file.close


def L_Vertical_circuit(x1, y1, Lr, txt_path):
    """
    Generate a vertical inductor circuit.

    Input:
        x1: Float, x-coordinate of the inductor.
        y1: Float, y-coordinate of the inductor.
        Lr: Float, inductance value.
        txt_path: String, path to the txt file.

    Output:
        None
    """
    with open(txt_path, 'a') as file:
        file.write("L;" +
                   str(x1) + "," + str(y1) + ";" +
                   str(x1) + "," + str(y1 + 1) + ";" +
                   str(Lr) + ";" +
                   "L" +
                   "\n"
                   )
        file.close


def L_Parallel_circuit(x1, y1, Lr, txt_path):
    """
    Generate a parallel inductor circuit.

    Input:
        x1: Float, x-coordinate of the inductor.
        y1: Float, y-coordinate of the inductor.
        Lr: Float, inductance value.
        txt_path: String, path to the txt file.

    Output:
        None
    """
    with open(txt_path, 'a') as file:
        file.write("L;"
                   + str(x1) + "," + str(y1) + ";"
                   + str(x1 + 1) + "," + str(y1) + ";"
                   + str(Lr) + ";"
                   + "L"
                   + "\n"
                   )
        file.close


def Lj_Vertical_circuit(x1, y1, Lj, txt_path):
    """
    Generate a vertical Josephson junction circuit.

    Input:
        x1: Float, x-coordinate of the Josephson junction.
        y1: Float, y-coordinate of the Josephson junction.
        Lj: Float, inductance value of the Josephson junction.
        txt_path: String, path to the txt file.

    Output:
        None
    """
    with open(txt_path, 'a') as file:
        file.write("J;"
                   + str(x1) + "," + str(y1) + ";"
                   + str(x1) + "," + str(y1 + 1) + ";"
                   + str(Lj) + ";"
                   + "Lj"
                   + "\n"
                   )
        file.close


def Lj_Parallel_circuit(x1, y1, Lj, txt_path):
    """
    Generate a parallel Josephson junction circuit.

    Input:
        x1: Float, x-coordinate of the Josephson junction.
        y1: Float, y-coordinate of the Josephson junction.
        Lj: Float, inductance value of the Josephson junction.
        txt_path: String, path to the txt file.

    Output:
        None
    """
    with open(txt_path, 'a') as file:
        file.write("J;"
                   + str(x1) + "," + str(y1) + ";"
                   + str(x1 + 1) + "," + str(y1) + ";"
                   + str(Lj) + ";"
                   + "Lj"
                   + "\n"
                   )
        file.close


def link_circuit_Parallel_positive(x1, y1, num, txt_path, rcsv_path):
    """
    Generate a positive parallel link circuit.

    Input:
        x1: Float, x-coordinate of the link.
        y1: Float, y-coordinate of the link.
        num: String or integer, link number.
        txt_path: String, path to the txt file.
        rcsv_path: String, path to the coupling cavity csv file.

    Output:
        None
    """
    C_Parallel_circuit(x1 + 1, y1, 3e-15, txt_path=txt_path)
    Resonator_circuit(x1 + 2, y1, 300e-15, 100e-9, str(num), txt_path=txt_path, rcsv_path=rcsv_path)
    C_Parallel_circuit(x1 + 3, y1, 3e-15, txt_path=txt_path)


def link_circuit_Parallel_negative(x1, y1, num, txt_path, rcsv_path):
    """
    Generate a negative parallel link circuit.

    Input:
        x1: Float, x-coordinate of the link.
        y1: Float, y-coordinate of the link.
        num: String or integer, link number.
        txt_path: String, path to the txt file.
        rcsv_path: String, path to the coupling cavity csv file.

    Output:
        None
    """
    C_Parallel_circuit(x1 - 1, y1, 3e-15, txt_path=txt_path)
    Resonator_circuit(x1 - 2, y1, 300e-15, 100e-9, str(num), txt_path=txt_path, rcsv_path=rcsv_path)
    C_Parallel_circuit(x1 - 3, y1, 3e-15, txt_path=txt_path)


def link_circuit_Vertical_negative(x1, y1, num, txt_path, rcsv_path):
    """
    Generate a negative vertical link circuit.

    Input:
        x1: Float, x-coordinate of the link.
        y1: Float, y-coordinate of the link.
        num: String or integer, link number.
        txt_path: String, path to the txt file.
        rcsv_path: String, path to the coupling cavity csv file.

    Output:
        None
    """
    C_Vertical_circuit(x1, y1 - 1, 3e-15, txt_path=txt_path)
    Resonator_circuit(x1, y1 - 2, 300e-15, 100e-9, str(num), txt_path=txt_path, rcsv_path=rcsv_path)
    C_Vertical_circuit(x1, y1 - 3, 3e-15, txt_path=txt_path)


def link_circuit_Vertical_positive(x1, y1, num, txt_path, rcsv_path):
    """
    Generate a positive vertical link circuit.

    Input:
        x1: Float, x-coordinate of the link.
        y1: Float, y-coordinate of the link.
        num: String or integer, link number.
        txt_path: String, path to the txt file.
        rcsv_path: String, path to the coupling cavity csv file.

    Output:
        None
    """
    C_Vertical_circuit(x1, y1 + 1, 3e-15, txt_path=txt_path)
    Resonator_circuit(x1, y1 + 2, 300e-15, 100e-9, str(num), txt_path=txt_path, rcsv_path=rcsv_path)
    C_Vertical_circuit(x1, y1 + 3, 3e-15, txt_path=txt_path)


# def clear_file(file_path):
#     if os.path.exists(file_path):
#         with open(file_path, 'w') as file:
#             file.truncate(0)

# Modify csv data
def update_csv_cell_qubit(file_path, target_row, target_column, new_value):
    """
    Update the cell data in the qubit csv file.

    Input:
        file_path: String, path to the csv file.
        target_row: String, content of the target row.
        target_column: Integer, index of the target column.
        new_value: String or number, new cell value.

    Output:
        None
    """
    # Read the CSV file content
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

    Ec = e ** 2 / 2 / float(new_value) / 10 ** -15 / hbar
    if target_row_index != -1:
        data[target_row_index][target_column] = new_value
        data[target_row_index][-1] = round(Ec / 2 / np.pi / 1e6, 2)

    # Write the updated content back to the CSV file
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


def update_csv_cell_resonator(file_path, target_row, target_column, new_value):
    """
    Update the cell data in the coupling cavity csv file.

    Input:
        file_path: String, path to the csv file.
        target_row: String, content of the target row.
        target_column: Integer, index of the target column.
        new_value: String or number, new cell value.

    Output:
        None
    """
    # Read the CSV file content
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