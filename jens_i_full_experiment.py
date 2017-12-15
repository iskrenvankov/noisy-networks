import fnmatch
import os
import subprocess
import pprint
import sys
from math import sqrt
import time

num_experiments = 20

if __name__ == '__main__':

	
	for i in range(num_experiments):
		p = subprocess.Popen('python generate_jens_i_noisy.py', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for line in p.stdout.readlines():
			#dir_name = str(line[:-2])[2:-1]
			dir_name = str(line[:-2])
			
		print(dir_name)
		pp = subprocess.Popen('python jens_i_solve_shell.py '+str(dir_name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for line in pp.stdout.readlines():
			print(line)