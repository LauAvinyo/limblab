#include "utilities.h"
using namespace std;

/////////////////////////////////////////////////////////////
TString getword(int i, TString line){
	TObjArray * words = line.Tokenize(" ");
	int nwords = words->GetEntriesFast();
	if(nwords<i) {
		cout<<i<<" wrong access in line:\n"<<line<<endl;
		exit(1);
	}
	TObjString* tmp= (TObjString*)words->operator[](i-1);
	TString word = tmp->GetString().Data();
	delete words;
	return word;
}

int getwordnr(TString line){
	TObjArray * words = line.Tokenize(" ");
	int n = words->GetEntriesFast();
	delete words;
	return n;
}


std::string tostring(float k) {
	  std::stringstream ss;  
	  ss<<k;  
	  std::string s;  
	  ss>>s;  
	  return s;
} 

/////////////////////////////////////////////////////////////////////////////////////////
double getLength(const TGraph* gr){

	double dist=0;
	unsigned int n = gr->GetN();
	double x1,y1,x2,y2,a ,b;
	for(unsigned int i=0; i<n-1; i++){
		gr->GetPoint(i,   x1,y1);
		gr->GetPoint(i+1, x2,y2);
		a= x1-x2;
		b= y1-y2;
		dist += TMath::Sqrt( a*a + b*b );
	}
	return dist;
}


//////////////////////////////////////////////////////////////////////////////////
TVector2 barycenterof(const TGraph* gr) {
	TVector2 bary(0.0,0.0);
	int n=gr->GetN();
	for(int i=0; i<n; i++){
		double x1,y1;
		gr->GetPoint(i, x1,y1);
		TVector2 p1(x1,y1);
		bary += p1;
	}
	return bary/n;
}


/////////////////////////////////////////////////////////////////////////////////////////
TVector2 rotate3D(const TVector3& u, const double& alpha, const double& beta, const double& gamma) {
	//promote to 3D
	TRotation rx, ry, rz;
	rz.RotateZ(alpha);
	ry.RotateY(beta);
	rx.RotateX(gamma);
	TVector3 v = ((rz * ry) * rx) * u;
	return TVector2(v.X(), v.Y());
}


/////////////////////////////////////////////////////////////////////////////////////////
int indexOfMin(vector<float>& v) {
	vector<float>::iterator imin = min_element(v.begin(), v.end());
	int k = distance(v.begin(), imin);
	return k;
}









