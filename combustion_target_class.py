import os
import numpy as np

class combustion_target():
###Class definition and acquisition of input parameters.	
	def __init__(self,data,index):
		self.data = data
		parameters = self.data.split(',')
		self.calculated = 0
		self.case_index = "case-"+str(index)
		self.input_file = self.target = self.simulation = self.temperature = self.pressure = self.phi = self.observed = None
		self.std_dvtn = 1.0
		for param in parameters:
			key_and_value = param.split()
			if len(key_and_value) == 1:
				continue
			
			key = key_and_value[0]
			content = key_and_value[2]
			
			if key == "input_file":
				self.input_file = os.path.abspath(content)
					
			if key == "target":
				self.target = content
				
			if key == "simulation":
				self.simulation = content
				
			if key == "T":
				self.temperature = float(content)
			
			if key == "P":
				self.pressure = float(content)
				
			if key == "phi":
				self.phi = float(content)
				
			if key == "observed":
				self.observed = float(content)
				
			if key == "deviation":
				self.std_dvtn = float(content)
				
			if self.target == "Fsl":
				if key == "start_profile":
					self.startProfile_location = content

#This function goes through a file previously created by the "generate_target_value_tables" function in data management module 
#and extract target value information for each case and sort them based on the extend of perturbation.
	def make_eta_lists(self,reaction_index):
		
		home_dir = os.getcwd()
		os.chdir(self.case_index)
		eta_values = open("sim_data.lst",'r').readlines()
		self.primary_plus =[]
		self.primary_minus = []
		self.secondary = []
		self.size = len(reaction_index)-1
		for i in range(self.size):
			self.sec = []
			for j in range(self.size+1):
				self.sec.append(0.0)
			self.secondary.append(self.sec)
				
		for eta in eta_values:
			param = eta.split()
			if param[0] == '0' and param[1] == '0':
				self.calculated = float(param[3])
				continue
			elif param[0] == '0' and param[2] == 'plus':
				self.primary_plus.append(float(param[3]))
		
			elif param[0] == '0' and param[2] == 'minus':
				self.primary_minus.append(float(param[3]))
				
				
			elif param[0] != '0':	
				f = reaction_index.index(param[0])
				s = reaction_index.index(param[1])
				self.secondary[f][s] = float(param[3])		
		os.chdir(home_dir)
		
#This function creates a set of coefficients from the calculated eta values collected by the function make_eta _lists of combustion_target_class
#These co-efficients define the response surface for each target hence they're connected to the respective instance of the class.	
	def create_response_surface(self, reaction_index):
		self.make_eta_lists(reaction_index)
		self.p_p = np.array(self.primary_plus)
		self.p_m = np.array(self.primary_minus)
		self.s = np.array(self.secondary)
		
		##Calculation of co-efficients
		self.a_i = (self.p_p - self.p_m)/2.0
		self.a_ii = (self.p_p -(2*self.calculated) +self.p_m)/2.0
		self.a_ij = np.zeros((self.size, self.size+1))
		for i in range(self.size):
			for j in range(self.size+1):
				if j > i:
					self.a_ij[i][j] = self.s[i][j] - self.calculated - self.a_i[i] - self.a_i[j] - self.a_ii[i] - self.a_ii[j]
					
					
		self.co_efficients = np.append(self.a_i, np.append(self.a_ii, self.a_ij))

#This function calculates the target value for any set of normalised vectiors, values of all x must be less than 1 and greater than -1. Function returns a second order polynomial. 		
		
	def calculated_target_value(self,x):
		target_value = self.calculated
		for i in range(len(x)):
			target_value+= self.a_i[i]*x[i] +self.a_ii[i]*x[i]**2
		for i in range(self.size):
			for j in range(self.size+1):
				if j > i:
					target_value += self.a_ij[i][j]*x[i]*x[j]
		return target_value
								
			
		
