import random
import numpy as np
import os
import subprocess
from math import sqrt

ket0 = np.array([[1.],[0.]])
ket1 = np.array([[0.],[1.]])
kets = [ket0, ket1]
I = np.eye(2)
H = 1./np.sqrt(2) * np.array([[1,1],[1,-1]])
T = np.array([[1.,0.],[0.,np.exp(1j*np.pi/4.)]])
CZ = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,-1]])


def standard_deviation(a):
	n = float(len(a))
	if n == 1:
		return 0.
	return sqrt(sum([(x - sum(a) / n) ** 2 for x in a]) / (n-1))
	
def get_probability(file_name):
	p = subprocess.Popen('python main.py '+file_name+' '+measurement_string+' -py samples=100', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for line in p.stdout.readlines():
		probability = float(line[13:-2])
	retval = p.wait()
	return probability
	
def getUi(n,i,U):
	if i == 0:
		Ui = U
	else:
		Ui = np.eye(2)

	for temp in range(1,n):
		if temp == i:
			currMatrix = U
		else:
			currMatrix = np.eye(2)
			
		Ui = np.kron(Ui, currMatrix)
		
	return Ui

def getCUij(n,i,j,CU):
	
	I = np.eye(2)
	SWAP = np.array([[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]])
	swapForward = 1
	swapBackward = 1

	for currPos in range(i,j-1):
		currSwap = 1
		for x in range(0,currPos):
			currSwap = np.kron(currSwap, I)
		currSwap = np.kron(currSwap, SWAP)
		for x in range(currPos+2,n):
			currSwap = np.kron(currSwap, I)
		
		swapForward = np.dot(currSwap,swapForward)
		swapBackward = np.dot(swapBackward,currSwap)

	CUij = 1
	for x in range(0,j-1):
		CUij = np.kron(CUij, I)
	CUij = np.kron(CUij, CU)
	for x in range(j+1,n):
		CUij = np.kron(CUij, I)
		
	CUij = np.dot(swapBackward,np.dot(CUij,swapForward))
	return CUij

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
	
num_rows = 3
num_cols = 3
num_qubits = num_rows * num_cols
num_calcs_perfect = 20
	
if __name__ == '__main__':

	for run_counter in range(20):

		f = open('file.circ', 'w')
		
		f.write("import circuits\\reference.circ\n\nmain:\n")

		psi0 = 1
		Hn = 1

		# Hadamard all qubits
		# |0>^n -> |+>^n
		for i in range(num_qubits):
			f.write(get_single_qubit_gate_line(i, 'H'))
			
			psi0 = np.kron(psi0, ket0)
			Hn = np.kron(Hn, H)
			
		psi = np.dot(Hn, psi0)
			
		# Apply CZ along grid
		# For each qubit, connect to the right and bottom
		for i in range(num_rows):
			for j in range(num_cols):
				if i < num_rows - 1:
					#bottom qubit exists
					controlIndex = i*num_cols + j
					zIndex = (i+1)*num_cols + j
					
					f.write(get_two_qubit_gate_line(controlIndex, zIndex, 'C', 'Z'))
					
					psi = np.dot(getCUij(num_qubits, controlIndex, zIndex, CZ), psi)
					
				if j < num_cols - 1:
					#right qubit exists
					controlIndex = i*num_cols + j
					zIndex = i*num_cols + (j+1)
					
					f.write(get_two_qubit_gate_line(controlIndex, zIndex, 'C', 'Z'))
					
					psi = np.dot(getCUij(num_qubits, controlIndex, zIndex, CZ), psi)

		# Apply T gates to random qubits
		for i in range(num_rows):
			for j in range(num_cols):
				if bool(random.getrandbits(1)):
					f.write(get_single_qubit_gate_line(i*num_cols + j, 'T'))
					
					psi = np.dot(getUi(num_qubits, i*num_cols + j, T), psi)
					
		# Hadamard all qubits to measure in X basis
		for i in range(num_qubits):
			f.write(get_single_qubit_gate_line(i, 'H'))
			
		psi = np.dot(Hn, psi)
					
		f.close()
		
		# Calculate exact bruteforce output
		rad = np.dot(psi0.conj().T, psi)
		prob = np.real((rad * np.conjugate(rad)).item(0))
		print("Bruteforce probability: "+str(prob))
		
		measurement_string = "0" * num_qubits
		perfect_probabilities = []
		for i in range(num_calcs_perfect):
			perfect_probabilities.append(get_probability('file.circ'))
			
		os.remove('file.circ')
				
		perfect_mean = 0.
		for perfect_prob in perfect_probabilities:
			perfect_mean += perfect_prob
		perfect_mean /= float(len(perfect_probabilities))
		
		print("Perfect mean: "+str(perfect_mean))
		print("Perfect std: "+str(standard_deviation(perfect_probabilities)))