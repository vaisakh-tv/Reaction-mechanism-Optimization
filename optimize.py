#python default modules
import nlopt
import numpy as np
import os, sys, re, threading, subprocess, time

#program specific modules
import make_input_file
import FlameMaster_in_parallel
import combustion_target_class
import data_management
import simulation_manager
import plotter

### KEY WORDS #######
mechanism = "mechanism"
targets_count = "targets_count"
targets = "targets:"
home_dir = os.getcwd()
fuel_name = "fuel"
global_reaction_eqn = "global_reaction"
parallel_thread_count = "parallel_threads"
plus = "plus"
minus = "minus"
unsrt = "uncertainty_data"
bin_file = "bin_file"

###########
#open the input file and check for arguements
###########
if len(sys.argv) > 1:
	input_file = open(sys.argv[1],'r')
	lines = input_file.readlines()
	print("Input file found\n")
else:
	print("Please enter a valid input file name as arguement. \n For details of preparing the input file, please see the UserManual\n\nProgram exiting")
	exit()

#!!!!!!! GET MECHANISM FILE , number of targets  from the input file !!!!!!!!!
for line in lines:
	######check for comments!!!!!!!!!!
	if "#" in line:
		line = line[:line.index('#')]
		
	word = line.split()
	if mechanism in word:
		mech_file_location = os.path.abspath(word[word.index(mechanism) + 2])
		
	if bin_file in word:
		bin_file_location = os.path.abspath(word[word.index(bin_file) + 2])
		
	if targets_count in word:
		no_of_targets = int(word[word.index(targets_count) + 2])
		
	if fuel_name in word:
		fuel = word[word.index(fuel_name) + 2]
		
	if global_reaction_eqn in word:
		global_reaction = word[word.index(global_reaction_eqn) + 2:]
		
	if parallel_thread_count in word:
		parallel_threads = int(word[word.index(parallel_thread_count) + 2])+1
		
	if unsrt in word:
		unsrt_location = os.path.abspath(word[word.index(unsrt) + 2])
		
	if targets in word:
		start_line = lines.index(line) + 1
		stop_line = start_line + no_of_targets

	

##!!!  MAKE A LIST OF TARGET CLASS CONTAINING EACH TARGET AS A CASE
target_list = []
c_index = 0
for target in lines[start_line:stop_line]:
	if "#" in target:
		target = target[:target.index('#')]
		
	t = combustion_target_class.combustion_target(target,c_index)
	c_index +=1
	target_list.append(t)
case_dir = range(len(target_list))
print("optimization targets identified\n")


##########Obtain uncertainty data from user input file!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

unsrt_file = open(unsrt_location,'r')
unsrt_data , reaction_index = data_management.extract_index_and_uncertainty(unsrt_file)

#########Generate Directories and mechanism files for FlameMaster !!!!!!!!!!!!!!!!!!!!!!!!!!!!!

if os.path.isfile("progress") == False:
	FlameMaster_Execution_location = simulation_manager.make_directories_for_simulation(case_dir,reaction_index,mech_file_location,unsrt_data, target_list, fuel, global_reaction, bin_file_location)
	locations = open("locations",'w')
	for i in FlameMaster_Execution_location:
		locations.write(i+"\n")
	locations.close()
	#########Run FlameMaster  Simulations!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	FlameMaster_in_parallel.run_FlameMaster_parallel(FlameMaster_Execution_location, parallel_threads, bin_file_location)
else:
	progress = open("progress",'r').readlines()
	FlameMaster_Execution_location = open("locations",'r').readlines()
	missing_location = data_management.find_missing_location(FlameMaster_Execution_location, progress)
	FlameMaster_in_parallel.run_FlameMaster_parallel(missing_location, parallel_threads, bin_file_location)


########## Extract target values!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
for case in case_dir:
	os.chdir("case-"+str(case))
	f = open("sim_data.lst",'w')
	data_sheet = data_management.generate_target_value_tables(FlameMaster_Execution_location, target_list, case, fuel)
	f.write(data_sheet)
	f.close()
	os.chdir(home_dir)


########################################
#												      #
#       RESPONSE SURFACE      DEVELOPMENT                              #
#			 									      #
########################################

	
for case in target_list:
	case.create_response_surface(reaction_index)


####Build the objective function and perform nlopt routine.!!!!!!!!!!!!!!!!!!!!!!!!!!!
def obj_function(x, grad):
	obj = 0.0
	global target_list
	for case in target_list:
		obj += ((case.calculated_target_value(x) - case.observed)/case.std_dvtn)**2

	return obj

#Specifics of nlopt module refer to nlopt python api for details.
var = len(reaction_index)
opt = nlopt.opt(0, var)
opt.set_lower_bounds(-1)
opt.set_upper_bounds(1)
opt.set_min_objective(obj_function)
opt.set_maxeval(var*10000)
opt.set_maxtime(7200)

#Prints the output of optimization.	
init_guess = np.zeros(var)
print("\n\nAlgorithm used for optimization : {}\n\n".format(opt.get_algorithm_name()))
t = time.time()
opt_x = opt.optimize(init_guess)
dt = int(time.time() - t)

hours = dt/3600
minutes = (dt%3600)/60
seconds = dt%60
print("Time for performing Optimization: {h} hours,  {m} minutes, {s} seconds\n................................................ ".format(h = hours, m = minutes, s =seconds))

minf = opt.last_optimum_value()
print(">>>>>>>>>>>>>>>\n\nOptimized Vectors\n\n>>>>>>>>>>>>>>>>>")
for i, j in enumerate(reaction_index):
	print("\n{}\t{}".format(j, opt_x[i]))
	

print("\n\n\nInitial objective function value : {}\n".format(obj_function(init_guess, 0)))
print("Optimized objective function value : {}\n".format(obj_function(opt_x, 0)))

####Build the optimized mechanism!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

data_management.generate_optimized_mechanism(mech_file_location, reaction_index, unsrt_data, opt_x)
data_management.make_log_files(target_list, reaction_index, opt_x)
plotter.plot_errors(target_list, opt_x)
plotter.plot_vector(reaction_index, opt_x)
print("generating log files and optimized mechanism file..... \n\n>>>>>> Program Exiting <<<<<<")
