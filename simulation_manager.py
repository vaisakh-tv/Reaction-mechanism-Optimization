import os, shutil, re, math #default python modules

import make_input_file #program specific modules

home_dir = os.getcwd()

#function to create directories and the required input files in a systematic way directories are named with the reaction index
def make_directories_for_simulation(case_dir,ind,mech_loc,unsert, target_list, fuel, g_reaction, bin_file_location):
	dir_list = []
	for case in case_dir: #loop for creating case directories
		if os.path.isdir(home_dir+"/case-"+str(case)) == True:
			continue
		os.mkdir("case-"+str(case))  	# make a dir for a target
		os.chdir("case-"+str(case))		#get into that dir
		os.mkdir('0')		# make folder for first order cases
		os.chdir('0')
		os.mkdir('0')		# make folder for nominal
		os.chdir('0')
		shutil.copyfile(mech_loc,'./mechanism.mech') #copy mechanism file
		make_input_file.create_input_file(target_list[case], fuel, g_reaction, bin_file_location) #generate input file
		dir_list.append(os.path.abspath('run'))
		os.mkdir("output")
		os.chdir("..")
		for i in ind: #loop for primary perturbation
			os.mkdir(i)
			os.chdir(i)
			os.mkdir("plus")
			os.mkdir("minus")
			os.chdir("plus")
			mechanism = open("../../0/mechanism.mech",'r')
			create_mechanism_file(mechanism,i,unsert[i],"plus")
			mechanism.close()
			make_input_file.create_input_file(target_list[case], fuel, g_reaction, bin_file_location)
			dir_list.append(os.path.abspath('run'))
			os.mkdir("output")
			os.chdir('..')
			os.chdir("minus")
			mechanism = open("../../0/mechanism.mech",'r')
			create_mechanism_file(mechanism, i, unsert[i], "minus")
			mechanism.close()
			make_input_file.create_input_file(target_list[case], fuel, g_reaction, bin_file_location)
			dir_list.append(os.path.abspath('run'))
			os.mkdir("output")
			os.chdir('../..')
		os.chdir('..')
		for i_i, i in enumerate(ind[:-1]): #Nested loop for secondary perturbations
			os.mkdir(i)	# make folders to do second order perturbations
			os.chdir(i)	# get into folder for second order
			os.mkdir('0')	#make folder to store mech file of  first order
			shutil.copyfile('../0/'+i+"/plus/mechanism.mech", "./0/mechanism.mech")#/plus/
			for j_i,j in enumerate(ind):
				if j_i > i_i:
					os.mkdir(j)
					os.chdir(j)
					mechanism = open("../0/mechanism.mech",'r')
					create_mechanism_file(mechanism, j, unsert[j], "plus")
					mechanism.close()
					make_input_file.create_input_file(target_list[case], fuel, g_reaction, bin_file_location)
					dir_list.append(os.path.abspath('run'))
					os.mkdir("output")
					os.chdir("..")
				
			os.chdir("..")
		os.chdir("..")
	return dir_list


#create a mechanism file py perturbing only the given reaction by checking the index in a regular expression
def create_mechanism_file(mech_file, reaction_index, unsert, flag):
	if flag == "plus":
		x = 1.0
	if flag == "minus":
		x = -1.0
	mech  = mech_file.read()
	w = re.compile(r'\n{}:.*?->.*?a\s*?=.*?(\S*?E\S\d*?\s).*?\}}'.format(reaction_index), re.DOTALL | re.IGNORECASE) #Regular expression for determining reaction. Group(1) will extract pre exp factor
	match = re.search(w, mech)
	if match == None:
		print("Unable to perturb reaction rate at {}... Reaction not found. Exiting".format(reaction_index))#If reaction was not found in mechanism file
		exit()
	reaction = match.group()
	pre_exp = match.group(1)
	#Perturb the forward reaction rate.
	pre_exp_p = "{:.4E} ".format(float(pre_exp)*math.exp(x*math.log(unsert)))#Equation for perturbing pre-exponential factor.

	new_reaction = reaction.replace(str(pre_exp), pre_exp_p+" ")

	new_mech = mech.replace(reaction, new_reaction)
	
	#Perturb the backward reaction if the rate index is specified as forward reaction by a suffix f
	back_reaction_index = ''
	if reaction_index[-1] == "f":
		back_reaction_index = reaction_index[:-1]+"b"
	elif reaction_index[-1] == "b":
		back_reaction_index = reaction_index[:-1]+"f"
	
	if back_reaction_index != '':
		w = re.compile(r'\n{}:.*?->.*?a\s*?=.*?(\S*?E\S\d*?\s).*?\}}'.format(back_reaction_index), re.DOTALL | re.IGNORECASE)
		match = re.search(w, new_mech)
		if match != None:
			reaction = match.group()
			pre_exp = match.group(1)
			#Perturb the backward reaction rate.
			pre_exp_p = "{:.4E} ".format(float(pre_exp)*math.exp(x*math.log(unsert)))

			new_reaction = reaction.replace(str(pre_exp), pre_exp_p+" ")

			new_mech = new_mech.replace(reaction, new_reaction)

	ff = open("mechanism.mech",'w')
	ff.write(new_mech)
	ff.close()
		
