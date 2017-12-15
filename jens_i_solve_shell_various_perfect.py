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
measurement_string_list = [int(random.getrandbits(1)) for x in range(num_qubits)]
measurement_string = ''.join(map(str, measurement_string_list))

#measurement_string = "01011100001011100000"

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
	
	for file in os.listdir(circuits_dir):
		if fnmatch.fnmatch(file, '*perfect*'):
			for i in range(num_calcs_perfect):
				perfect_probabilities.append(get_probability(file))
			
	perfect_mean = 0.
	for perfect_prob in perfect_probabilities:
		perfect_mean += perfect_prob
	perfect_mean /= float(len(perfect_probabilities))
	
	print(measurement_string)
	print(perfect_mean)
	print(standard_deviation(perfect_probabilities))