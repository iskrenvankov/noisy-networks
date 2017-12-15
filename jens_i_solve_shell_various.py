import fnmatch
import os
import subprocess
import pprint
import sys
from math import sqrt
import random

#circuits_dir = '2017-08-01_13-06-01'
circuits_dir = sys.argv[1]
num_calcs_perfect = 20
num_calcs_noisy = 20
num_qubits = 20
#measurement_string = "0" * 20
#measurement_string_list = [int(random.getrandbits(1)) for x in range(num_qubits)]
#measurement_string = ''.join(map(str, measurement_string_list))

measurement_string = "00111100001101001110"

def standard_deviation(a):
	n = float(len(a))
	return sqrt(sum([(x - sum(a) / n) ** 2 for x in a]) / (n-1))
 
def get_probability(file_name):

	circ_dir = os.path.join(circuits_dir, file_name)
	
	p = subprocess.Popen('python main.py '+circ_dir+' '+measurement_string+' -py samples=100', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for line in p.stdout.readlines():
		probability = float(line[13:-2])
	retval = p.wait()
	return probability

if __name__ == '__main__':

	perfect_probabilities = []
	noisy_probabilities = []
	dep_probabilities = []
	gate_probabilities = []
	#half_time_probabilities = []
	
	for file in os.listdir(circuits_dir):
		if fnmatch.fnmatch(file, '*perfect*'):
			for i in range(num_calcs_perfect):
				perfect_probabilities.append(get_probability(file))
				
		if fnmatch.fnmatch(file, '*dep*'):
			curr_dep_probabilities = []
			for i in range(num_calcs_noisy):
				curr_dep_probabilities.append(get_probability(file))
			dep_probabilities.append(curr_dep_probabilities)
				
		if fnmatch.fnmatch(file, '*gate*'):
			curr_gate_probabilities = []
			for i in range(num_calcs_noisy):
				curr_gate_probabilities.append(get_probability(file))
			gate_probabilities.append(curr_gate_probabilities)
				
		#if fnmatch.fnmatch(file, '*half_time*'):
			#curr_half_time_probabilities = []
			#for i in range(num_calcs_noisy):
			#	curr_half_time_probabilities.append(get_probability(file))
			#half_time_probabilities.append(curr_half_time_probabilities)
				
		else:
			# noisy file
			curr_noisy_probabilites = []
			for i in range(num_calcs_noisy):
				curr_noisy_probabilites.append(get_probability(file))
			noisy_probabilities.append(curr_noisy_probabilites)
			
	perfect_mean = 0.
	for perfect_prob in perfect_probabilities:
		perfect_mean += perfect_prob
	perfect_mean /= float(len(perfect_probabilities))
	
	noisy_mean = 0.
	noisy_means = []
	for noisy_sequence in noisy_probabilities:
		curr_sequence_noisy_mean = 0.
		for noisy_prob in noisy_sequence:
			curr_sequence_noisy_mean += noisy_prob
		curr_sequence_noisy_mean /= float(len(noisy_sequence))
		
		noisy_mean += curr_sequence_noisy_mean
		noisy_means.append(curr_sequence_noisy_mean)
	noisy_mean /= float(len(noisy_probabilities))
	
	dep_mean = 0.
	dep_means = []
	for dep_sequence in dep_probabilities:
		curr_sequence_dep_mean = 0.
		for dep_prob in dep_sequence:
			curr_sequence_dep_mean += dep_prob
		curr_sequence_dep_mean /= float(len(dep_sequence))
		
		dep_mean += curr_sequence_dep_mean
		dep_means.append(curr_sequence_dep_mean)
	dep_mean /= float(len(dep_probabilities))
	
	gate_mean = 0.
	gate_means = []
	for gate_sequence in gate_probabilities:
		curr_sequence_gate_mean = 0.
		for gate_prob in gate_sequence:
			curr_sequence_gate_mean += gate_prob
		curr_sequence_gate_mean /= float(len(gate_sequence))
		
		gate_mean += curr_sequence_gate_mean
		gate_means.append(curr_sequence_gate_mean)
	gate_mean /= float(len(gate_probabilities))
	
	#half_time_mean = 0.
	#half_time_means = []
	#for half_time_sequence in half_time_probabilities:
	#	curr_sequence_half_time_mean = 0.
	#	for half_time_prob in half_time_sequence:
	#		curr_sequence_half_time_mean += half_time_prob
	#	curr_sequence_half_time_mean /= float(len(half_time_sequence))
	#	
	#	half_time_mean += curr_sequence_half_time_mean
	#	half_time_means.append(curr_sequence_half_time_mean)
	#half_time_mean /= float(len(half_time_probabilities))
	
	#pp = pprint.PrettyPrinter(indent=4)
	#print(*perfect_probabilities)
	#pp.pprint(noisy_probabilities)
	
	print(measurement_string)
	print(perfect_mean)
	print(standard_deviation(perfect_probabilities))
	print(noisy_mean)
	print(standard_deviation(noisy_means))
	print(dep_mean)
	print(standard_deviation(dep_means))
	print(gate_mean)
	print(standard_deviation(gate_means))
	#print(half_time_mean)
	#print(standard_deviation(half_time_means))