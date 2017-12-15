import os
import random
from math import e
from datetime import datetime

DEPOLARIZATION_RATE = 9e-4         #2.5.1 random pauli per s
#DEPOLARIZATION_RATE = 4.5e-4
#DEPOLARIZATION_RATE = 0.

DEPHASING_RATE = 7.2e-3            #2.5.2 Z per s
#DEPHASING_RATE = 3.6e-3 
#DEPHASING_RATE = 0.

PREPARATION_RATE = 2e-4            #2.5.3 X
MEASUREMENT_RATE = 5e-4            #2.5.3 X

#SINGLE_QUBIT_RATE = 1.5e-6         #2.5.4 random Pauli
#SINGLE_QUBIT_RATE = 0.75e-6
SINGLE_QUBIT_RATE = 0.

#MULTI_QUBIT_RATE_SINGLE = 5.5e-4   #2.5.5 random Paulis
#MULTI_QUBIT_RATE_SINGLE = 2.75e-4
MULTI_QUBIT_RATE_SINGLE = 0.

#MULTI_QUBIT_RATE_MULTI = 6e-5      #2.5.5 ZZ
#MULTI_QUBIT_RATE_MULTI = 3e-5 
MULTI_QUBIT_RATE_MULTI = 0.

#LINKING_RATE
MEASUREMENT_TIME = 2e-3            #Measurement speed. in s
GATE_TIME = 5e-4                   #2.4 Unitary gate speed. in s

LINKING_TIME = 1.5                 #2.4 Linking operation speed. in s
#LINKING_TIME = 0.75
#LINKING_TIME = 0.

Paulis = ['X', 'Y', 'Z']

noisy_files_count = 20

num_rows = 4
num_cols = 5
num_qubits = num_rows * num_cols

def get_single_qubit_gate_line(i, gate):
	# return the line string that applies the gate to the qubit at index i
	
	line = ''
	for k in range(i):
		line += '_'
	line += gate
	for k in range(i+1, num_qubits):
		line += '_'
	line += '\n'
	
	return line

def get_two_qubit_gate_line(i, j, gateI, gateJ):
	# return the line string that applies the two-qubit gate
	# (gateI, gateJ) to the qubits and indices i and j
	# assuming i < j
	
	line = ''
	for k in range(i):
		line += '_'
	line += gateI
	for k in range(i+1, j):
		line += '_'
	line += gateJ
	for k in range(j+1, num_qubits):
		line += '_'
	line += '\n'
	
	return line
	
def single_qubit_noise(i):
	# return the line string that randomly applies single-qubit noise
	# to the qubit at index i
	
	line = ''
	if random.random() < SINGLE_QUBIT_RATE:
		line += get_single_qubit_gate_line(i, random.choice(Paulis))
		
	return line
	
def two_qubit_noise(i, j):
	# return the line string that randomly applies two-qubit noise
	# to the qubits at indices i and j
	
	line = ''
	if random.random() < MULTI_QUBIT_RATE_SINGLE:
		line += get_single_qubit_gate_line(i, random.choice(Paulis))
	if random.random() < MULTI_QUBIT_RATE_SINGLE:
		line += get_single_qubit_gate_line(j, random.choice(Paulis))
	if random.random() < MULTI_QUBIT_RATE_MULTI:
		line += get_single_qubit_gate_line(i, 'Z')
		line += get_single_qubit_gate_line(j, 'Z')
		
	return line
	
def time_based_noise(time):
	# return the line string that randomly applies time-based noise
	# to all qubits in the system during an operation lasting 
	# some given time
	
	line = ''
	for i in range(num_qubits):
		# depolarization
		if random.random() < 1 - e**(-time * DEPOLARIZATION_RATE):
			# Poisson process
			line += get_single_qubit_gate_line(i, random.choice(Paulis))
		# dephasing
		if random.random() < 1 - e**(-time * DEPHASING_RATE):
			# Poisson process
			line += get_single_qubit_gate_line(i, 'Z')
			
	return line
	
def entangle_right(is_even_column_index, is_noise):
	# apply entanglement or CZ two-qubit noise to the right
	
	line = ''
	for i in range(num_rows):
		for j in range(0 if is_even_column_index else 1, num_cols, 2):
			if j < num_cols - 1:
				#right qubit exists
				left_qubit_index = i*num_cols + j
				right_qubit_index = i*num_cols + (j+1)
				
				if is_noise:
					line += two_qubit_noise(left_qubit_index, right_qubit_index)
				else:
					line += get_two_qubit_gate_line(left_qubit_index, right_qubit_index, 'C', 'Z')
					
	return line
	
def entangle_bottom(is_even_row_index, is_noise):
	# apply entanglement or CZ two-qubit noise downwards
	
	line = ''
	for j in range(num_cols):
		for i in range(0 if is_even_row_index else 1, num_rows, 2):
			if i < num_rows - 1:
				#bottom qubit exists
				top_qubit_index = i*num_cols + j
				bottom_qubit_index = (i+1)*num_cols + j
				
				if is_noise:
					line += two_qubit_noise(top_qubit_index, bottom_qubit_index)
				else:
					line += get_two_qubit_gate_line(top_qubit_index, bottom_qubit_index, 'C', 'Z')
					
	return line

if __name__ == '__main__':

	timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	os.makedirs(timestamp)
	
	perfect_file_string = ""
	noisy_file_strings = ["" for i in range(noisy_files_count)]
	
	perfect_file_string += "import ../circuits/reference.circ\n\nmain:\n"
	for i in range(noisy_files_count):
		noisy_file_strings[i] += "import ../circuits/reference.circ\n\nmain:\n"
		
	# Preparation errors
	for i in range(noisy_files_count):
		for j in range(num_qubits):
			if random.random() < PREPARATION_RATE:
				noisy_file_strings[i] += get_single_qubit_gate_line(j, 'X')

	# Hadamard all qubits
	# |0>^n -> |+>^n
	for i in range(num_qubits):
		line_string = get_single_qubit_gate_line(i, 'H')
		perfect_file_string += line_string
		for j in range(noisy_files_count):
			noisy_file_strings[j] += line_string
		
	# Apply perfect CZ along grid
	# For each qubit, connect to the right and bottom
	perfect_file_string += entangle_right(True, False)
	perfect_file_string += entangle_right(False, False)
	perfect_file_string += entangle_bottom(True, False)
	perfect_file_string += entangle_bottom(False, False)
		
	# Apply noisy CZs along respective grids
	for i in range(noisy_files_count):
		# First step: even-indexed columns' qubits to their right neighbours
		# Apply CZ
		noisy_file_strings[i] += entangle_right(True, False)
		# Apply two-qubit CZ noise
		noisy_file_strings[i] += entangle_right(True, True)
		# Apply time-based noise
		# Time needed is 1 link + 1 Bell measurement to teleport + 1 apply gate
		noisy_file_strings[i] += time_based_noise(LINKING_TIME + MEASUREMENT_TIME + GATE_TIME)
		
		# Second step: odd-indexed columns' qubits to their right neighbours
		# Apply CZ
		noisy_file_strings[i] += entangle_right(False, False)
		# Apply two-qubit CZ noise
		noisy_file_strings[i] += entangle_right(False, True)
		# Apply time-based noise
		# Time needed is 1 link + 1 Bell measurement to teleport + 1 apply gate
		noisy_file_strings[i] += time_based_noise(LINKING_TIME + MEASUREMENT_TIME + GATE_TIME)
		
		# Third step: even-indexed rows' qubits to their bottom neighbours
		# Apply CZ
		noisy_file_strings[i] += entangle_bottom(True, False)
		# Apply two-qubit CZ noise
		noisy_file_strings[i] += entangle_bottom(True, True)
		# Apply time-based noise
		# Time needed is 1 link + 1 Bell measurement to teleport + 1 apply gate
		noisy_file_strings[i] += time_based_noise(LINKING_TIME + MEASUREMENT_TIME + GATE_TIME)
		
		# Fourth step: odd-indexed rows' qubits to their bottom neighbours
		# Apply CZ
		noisy_file_strings[i] += entangle_bottom(False, False)
		# Apply two-qubit CZ noise
		noisy_file_strings[i] += entangle_bottom(False, True)
		# Apply time-based noise
		# Time needed is 1 link + 1 Bell measurement to teleport + 1 apply gate
		noisy_file_strings[i] += time_based_noise(LINKING_TIME + MEASUREMENT_TIME + GATE_TIME)
		
	# Generate random bit string for random T-gate application
	# Must be identical across noisy files, as well as with the perfect file
	curr_bitstring = "10010011100001001010"
	t_gates_bit_string = [bool(int(curr_bitstring[x])) for x in range(num_qubits)]
	#t_gates_bit_string = [bool(random.getrandbits(1)) for x in range(num_qubits)]
	
	# Apply T gates to perfect file
	for i in range(num_qubits):
		if t_gates_bit_string[i]:
			perfect_file_string += get_single_qubit_gate_line(i, 'T')
	
	# Apply T gates to noisy files
	for i in range(noisy_files_count):
		for j in range(num_qubits):
			if t_gates_bit_string[j]:
				# Apply T-gate
				noisy_file_strings[i] += get_single_qubit_gate_line(j, 'T')
				# Apply single-qubit noise
				noisy_file_strings[i] += single_qubit_noise(j)
				# APply time-based noise
				noisy_file_strings[i] += time_based_noise(GATE_TIME)
				
	# Hadamard all qubits to measure in X basis
	for i in range(num_qubits):
		line_string = get_single_qubit_gate_line(i, 'H')
		perfect_file_string += line_string
		for j in range(noisy_files_count):
			noisy_file_strings[j] += line_string
		
	# Measurement errors
	for i in range(noisy_files_count):
		for j in range(num_qubits):
			if random.random() < MEASUREMENT_RATE:
				noisy_file_strings[i] += get_single_qubit_gate_line(j, 'X')
				
	# Write perfect file
	perfect_file = open(timestamp+'/perfect.circ', 'w')
	perfect_file.write(perfect_file_string)
	perfect_file.close()
	
	# Write noisy files
	for i in range(noisy_files_count):
		noisy_file = open(timestamp+'/dep_'+str(i)+'.circ', 'w')
		noisy_file.write(noisy_file_strings[i])
		noisy_file.close()
		
	print(timestamp)