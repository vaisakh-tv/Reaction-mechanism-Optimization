import subprocess

def create_input_file(target,fuel, g_reaction, bin_file_location):
	global_reaction = ''
	for i in g_reaction:
		global_reaction += i
	
	if target.input_file != None:
		instring = open(target.input_file,'r').read()
	
	elif target.target == "Tig":	
		instring = """############
# Numerics #
############

RelTol = 1.0e-10
AbsTol = 1.0e-12

TStart = 0.0
TEnd = 1.0e0


#######
# I/O #
#######

#AdditionalOutput is TRUE
#WriteEverySolution is TRUE
#PrintMolarFractions is TRUE

OutputPath is ./output
NOutputs = 50

#############
# Chemistry #
#############

MechanismFile is mechanism.pre
globalReaction is {g_r};

fuel is {f}
oxidizer is O2

#########
# Flame #
#########

Flame is {simulation} Homo Reactor
#Flame is Isobar Homo Reactor
#ExactBackward is TRUE

phi = {phi}

Pressure = {pressure}


#######################
# Boundary conditions #
#######################

#ContInc = -25
#ContType is Temperature
#ContBound = 800

InitialCond {{
	t = {temperature}
	X->N2 = 0.8
	X->O2 = 0.2
}}
""".format(pressure = target.pressure, temperature = target.temperature, phi = target.phi, simulation = target.simulation, f = fuel, g_r = global_reaction)
	
	elif target.target == "Fsl":
		instring = """############
# Numerics #
############

#### Newton solver ####

UseNumericalJac is TRUE
UseSecondOrdJac is TRUE
UseModifiedNewton = TRUE

DampFlag = TRUE
LambdaMin = 1.0e-2

#Switch on time dependent solution
timedepflag = TRUE
deltatstart = 0.0001

MaxIter = 5000
TolRes = 1.0e-15
TolDy = 1e-4

#### grid ####

DeltaNewGrid = 25
OneSolutionOneGrid = TRUE
initialgridpoints = 89
maxgridpoints = 139
q = -0.25
R = 60

########################
# Sensitivity Analysis #
########################

ReactionFluxAnal is TRUE

#######
# I/O #
#######

WriteEverySolution = TRUE
PrintMolarFractions is TRUE


OutputPath is ./Output/n_heptane
StartProfilesFile is {s_p_loc}

#############
# Chemistry #
#############

MechanismFile is mechanism.pre
globalReaction is {g_r};

fuel is {f}
oxidizer is O2

#########
# Flame #
#########

Flame is {simulation}
ExactBackward is FALSE

phi = {phi}

pressure = {pressure}

#ComputeWithRadiation is TRUE
#Thermodiffusion is TRUE

#######################
# Boundary conditions #
#######################

#ConstMassFlux is TRUE
#MassFlux = 0.3

Unburnt Side {
	dirichlet {
		t = {temperature}
	}
}""".format(pressure = target.pressure, temperature = target.temperature, phi = target.phi, simulation = target.simulation, f = fuel, g_r = global_reaction, s_p_loc =target.startProfile_location)
	
	
	infile = open("FlameMaster.input",'w')
	infile.write(instring)
	infile.close()
	
	run_file = open("run",'w')
	s = """#!/bin/bash
ScanMan -i mechanism.mech -t {bin_file} &> ScanMan.log
FlameMaster &> Flame.log
""".format(bin_file = bin_file_location) 

	run_file.write(s)
	run_file.close()
	

