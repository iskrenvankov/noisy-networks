import random

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
	

if __name__ == '__main__':

	f = open('file.circ', 'w')
	
	f.write("import reference.circ\n\nmain:\n")

	# Hadamard all qubits
	# |0>^n -> |+>^n
	for i in range(num_qubits):
		f.write(get_single_qubit_gate_line(i, 'H'))
		
	# Apply CZ along grid
	# For each qubit, connect to the right and bottom
	for i in range(num_rows):
		for j in range(num_cols):
			if i < num_rows - 1:
				#bottom qubit exists
				f.write(get_two_qubit_gate_line(i*num_cols + j, (i+1)*num_cols + j, 'C', 'Z'))
			if j < num_cols - 1:
				#right qubit exists
				f.write(get_two_qubit_gate_line(i*num_cols + j, i*num_cols + (j+1), 'C', 'Z'))

	# Apply T gates to random qubits
	for i in range(num_rows):
		for j in range(num_cols):
			if bool(random.getrandbits(1)):
				f.write(get_single_qubit_gate_line(i*num_cols + j, 'T'))
				
	# Hadamard all qubits to measure in X basis
	for i in range(num_qubits):
		f.write(get_single_qubit_gate_line(i, 'H'))
				
	f.close()