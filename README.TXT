You need to install some additional modules in Python inorder to run from source code.

sudo apt-get install python-numpy
sudo apt-get install python-nlopt
sudo apt-get install python-matplotlib



Input files required for the simultion are availble in the zip file (example.zip). 

1)	errors.unsrt (Uncertainty data)
2)	nalkanes.bin
		This file can be created using nalkanes.thermo and nalkanes.trans using the program CreateBinFile which is a part of FlameMaster (See FlameMaster documentation.)

3)	nheptane.mech (Reaction mechanism file in FlameMaster format. FlameMaster has the ability to convert from ChemKin format to FlameMaster format) 
4)	target_input.opt

Program can be executed by calling main code from the directory of choice as (all the 4 above mentioned files should be present in that directory. Otherwise the path name should be given in the input file [target_input.opt].)



python /path/to/the/directory/optimize.py target_input.opt







Supports FlameMaster 3.3.10. compatibility with other versions are not tested. Require Unix based Operating system. 

FlameMaster can be downloaded at (https://www.itv.rwth-aachen.de/index.php?id=13&L=1) [In case the URL has changed, Look for RWTH AACHEN UNIVERSITY WEBSITE AT DOWNLOAD SECTION]

WARNING!!!!
Execution will take very long time to complete (Several hours) You can reduce target count in the input file for testing purpose without removing the target entries from the input file.

HAPPY OPTIMIZATION !!!!!!
All questions are welcome.
vaisakhtv92@gmail.com
