import matplotlib.pyplot as plt
import numpy as np


def plot_errors(target_list,opt_x):
	x = np.arange(len(target_list))
	y = []
	z = []
	cases = []
	for i in target_list:
		y.append(abs(i.calculated - i.observed)/i.observed*100)
		z.append(abs(i.calculated_target_value(opt_x) - i.observed)/i.observed*100)
		cases.append(i.case_index)
		
	fig = plt.figure()
	plt.title("Errors before and after optimization")
	plt.xlabel("Target cases")
	plt.ylabel("Errors (%)")
	sub1 = plt.subplot()

	plt.subplots_adjust(left=0.15, bottom=0.2, right=0.95, top=0.8, wspace=0, hspace=0)
	plt.xticks(x,cases,rotation='vertical')
	sub1.bar(x-0.1, y, width=0.2,color='b',align="center",label="Old error")
	sub1.bar(x+0.1, z, width=0.2,color='r', align="center",label="New Error")
	plt.legend(loc='upper center', shadow=True)
	plt.savefig("Error_plot.eps",format="eps", figsize=(20,10), dpi = 1200)


def plot_vector(reaction_index, opt_x):
	x = np.arange(len(reaction_index))
	fig = plt.figure()
	plt.title("Normalized Optimum Vector")
	plt.xlabel("Reaction index")
	plt.ylabel("Perturbed rate constant (Normalized)")
	sub1 = plt.subplot()
	
	plt.subplots_adjust(left=0.15, bottom=0.2, right=0.95, top=0.8, wspace=0, hspace=0)
	plt.xticks(x,reaction_index,rotation='vertical')
	plt.xlim(-1,len(reaction_index))
	sub1.bar(x, opt_x,width=0.2, color='b', align='center')
	plt.savefig("Optimum_vector.eps",format="eps", figsize=(20,10), dpi = 1200)
