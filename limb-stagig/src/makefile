
###################### On Linux ########################
# download and unpack root v6 from https://root.cern/install/all_releases/
# update ROOTSYS below to match the install directory:

ROOTSYS=/opt/homebrew/Cellar/root/6.30.06/

###################### On Mac ##########################
# brew install root
#or
# brew install --build-from-source root
#export PATH=$PATH:$ROOTSYS/bin

########################################################

# optionally: on line 235 of plotter.cpp change output figure location.


DEPS = stager.h reader.h utilities.h Limb.h plotter.h
OBJS = main.o utilities.o Limb.o plotter.o reader.o reflimbs.o stager.o
OPTS = `${ROOTSYS}/bin/root-config --cflags`

all :  $(OBJS)
	g++ -o "limbstager" $(OBJS) `${ROOTSYS}/bin/root-config --glibs`


main.o : main.cpp $(DEPS)
	gcc -c $(OPTS) -I$(ROOTSYS)/include main.cpp -o main.o

utilities.o : utilities.cpp $(DEPS)
	gcc -c $(OPTS) -I$(ROOTSYS)/include utilities.cpp -o utilities.o

Limb.o : Limb.cpp $(DEPS)
	gcc -c $(OPTS) -I$(ROOTSYS)/include Limb.cpp -o Limb.o

plotter.o : plotter.cpp $(DEPS)
	gcc -c $(OPTS) -I$(ROOTSYS)/include plotter.cpp -o plotter.o

reader.o : reader.cpp $(DEPS)
	gcc -c $(OPTS) -I$(ROOTSYS)/include reader.cpp -o reader.o

reflimbs.o : reflimbs.cpp reflimbs.h
	gcc -c $(OPTS) -I$(ROOTSYS)/include reflimbs.cpp -o reflimbs.o

stager.o : stager.cpp $(DEPS)
	gcc -c $(OPTS) -I$(ROOTSYS)/include stager.cpp -o stager.o

.PHONY: clean
clean :
	rm -f limbstager *.o


