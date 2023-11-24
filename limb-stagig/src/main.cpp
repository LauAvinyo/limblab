//==================================================================================
// Name        : LimbStager
// Author      : Marco Musy
// Version     : v7.1
// Copyright   : CRG (Centre de Regulacio Genomica, Barcelona), all rights reserved.
// Description : LimbStager in C++, Ansi-style
// Run interactively:
//  cd limbstager
//  Release/limbstager 'DB/kevin/E12;09_22_RH.txt'
//==================================================================================
#include "stager.h"
#include "reader.h"

using namespace std;

extern vector<Limb*> limbs;

/////////////////////////////////////////////////////////////////////////////////////
int main(int argc, char *argv[]) {

	if(argc!=2) {
		cout<<"ABORT: Wrong nr. of arguments: "<<argc-1<<endl;
		exit(0);
	}

	//fills vector limbs. May contain more than one limb.
	readDB(std::string(argv[1])); 

	for (vector<Limb*>::iterator k=limbs.begin(); k!=limbs.end(); k++) {

		Limb* alimb = (*k);
		if(alimb->points().size()<8) {
			cout<<"Too few points. Skip. "<<alimb->jpgname()<<endl;
			continue;
		}
		
		stageThisLimb( alimb ); 
		
		//python interface greps this line:
		cout<<"RESULT "<<alimb->time()<<" "<<alimb->fitError()<<" "<<alimb->chi2()<<endl;
	}

	return 0;
}


