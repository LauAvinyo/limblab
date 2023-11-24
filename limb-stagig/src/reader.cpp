#include "utilities.h"
#include "reflimbs.h"

using namespace std;

vector<Limb*> reflimbs;
vector<Limb*>    limbs;

///////////////////////////////////////////////////////////// reads limb and reflimbs
void readDB(TString limbfilename) {
	/////////////////////////////////////////////////////////

	TString username, namejpg;
	Char_t  name[50];
	Float_t Pixelsize;
	Int_t   AgeDay;
	Int_t   AgeTime;
	Int_t   PredAgeDay;
	Int_t   PredAgeTime;
	Float_t splinelength;
	Int_t   N;
	Float_t meas_x[5000];
	Float_t meas_y[5000];
	Int_t   R, Age;
	Float_t ref_x[900];
	Float_t ref_y[900];
	int     alimbside;

	limbs.clear();

	int iii=0;
	TString line;
	ifstream indata;

	cout<<"Reading DB: "+limbfilename<<endl;
	indata.open(limbfilename);
	do {
		if(line.ReadLine(indata).eof()) break;

		int nwords = getwordnr(line);
		if(!nwords) continue;
		N=0;
		if(nwords==9){
			username   = getword(1, line);
			name[0]    = (*(getword(2, line).Data()));
			namejpg    = getword(2, line);
			alimbside  = 0;
			if(getword(3, line) != "u") alimbside = (getword(3, line)=="r" ? 1 : -1);
			Pixelsize  = getword(4, line).Atof();
			AgeDay     = getword(5, line).Atoi();
			AgeTime    = getword(6, line).Atoi();
			PredAgeDay = getword(7, line).Atoi();
			PredAgeTime= getword(8, line).Atoi();
			N          = getword(9, line).Atoi();
		} else if(nwords>3) { cout<<"DB ERROR: wrong header size in "<< line <<endl; continue; }
		for(int i=0; i<N; i++){
			if(line.ReadLine(indata).eof()) break;
			if(getword(1, line)=="MEASURED"){
				meas_x[i] = getword(2, line).Atof();
				meas_y[i] = getword(3, line).Atof();
			}
		}

		line.ReadLine(indata);
		// if(getwordnr(line)>3) { cout<<"DB ERROR: wrong spline size in "<< line <<endl; continue; }
		if(N) {
			TString rootname = "limb_" + tostring(iii++);
			Limb* limb = new Limb();

			TGraph* tg = new TGraph(N);
			vector<TVector2> vv;
			for(int i=0; i<N; i++){
				TVector2    v(  meas_x[i], -meas_y[i]);//the minus is a coordinate convention
				tg->SetPoint(i, meas_x[i], -meas_y[i]);
				vv.push_back(v);
			}
			tg->SetTitle(rootname);
			tg->SetName(rootname);
			limb->setTGraph( tg );

			limb->setPoints(vv);
			limb->setJpgName(namejpg);
			limb->setUserName(username);
			limb->setSide(alimbside);
			limb->setAgeDay(AgeDay);
			limb->setAgeTime(AgeTime);

			limbs.push_back( limb );
		}

	} while (true);

	indata.close();

	///////////////////////////////////////////////////////// reflimbs
	reflimbs.clear();
	std::stringstream refLimbDataStream;
	refLimbDataStream << DBString();

	iii=0;
	do {
		if(line.ReadLine(refLimbDataStream).eof()) break;
		int nwords = getwordnr(line);
		if(!nwords) continue;
		Age = getword(1, line).Atoi();
		R   = getword(2, line).Atoi();
		for(int i=0; i<R; i++ ){
			if(line.ReadLine(refLimbDataStream).eof()) break;
			ref_x[i] = getword(1, line).Atof();
			ref_y[i] = getword(2, line).Atof();
		}
		if(R) {
			TString rootname = "reflimb_" + tostring(iii++);
			Limb* reflimb = new Limb();

			int ageday= int(Age/24.);
			int agetime= Age-24*(ageday);
			reflimb->setAgeDay(ageday);
			reflimb->setAgeTime(agetime);

			TGraph* reftg = new TGraph(R);
			vector<TVector2> vv;
			for(int i=0; i<R; i++){
				TVector2      v(   ref_x[i], -ref_y[i]);//the minus is a coordinate convention
				reftg->SetPoint(i, ref_x[i], -ref_y[i]);
				vv.push_back(v);
			}
			reftg->SetTitle(rootname);
			reftg->SetName(rootname);
			reflimb->setPoints(vv);
			reflimb->setTGraph(reftg);

			reflimbs.push_back( reflimb );
		}
	} while (true);

	return;
}

