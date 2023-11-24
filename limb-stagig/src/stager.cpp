#include "stager.h"
#include "plotter.h"
#include "utilities.h"

#include "Math/Minimizer.h"
#include "Math/Factory.h"
#include "Math/Functor.h"
#include <algorithm>
using namespace std;

TGraph* datagraph, *theograph, *originaltgraph;
double datagraph_dist, theograph_dist;
TVector2 thislimb_barycenter;
vector<float> minParams;
int alimbside;
const unsigned Npars(6);
double par_save[Npars];
double sum_save;

extern vector<Limb*> reflimbs;

bool Enable3D = 1;


/////////////////////////////////////////////////////////////////////////////////////////
Double_t getSigma(const TGraph* g, unsigned int i) {

	unsigned n   = g->GetN();
	double sigma = datagraph_dist /n /10.; 
	//10. is a rough estimate of how much of the
	//fraction of the point-point in data to the actual distance point-curve
	return sigma;
}

///////////////////////////////////////////////////////////////////////////////////////////
double calc_chi2(const double *par) {

	double pixels= par[0];
	double alpha = par[1];
	double xshift= par[2];
	double yshift= par[3];
	double beta  = par[4];
	double gamma = par[5];

	//trasforms original theograph:
	double scale = 1./pixels;
	transform_originaltgraph_3D(scale, alpha, beta, gamma, xshift, yshift);

	//calculate chi2
	double x1,y1,x2,y2, a,b, dist2, sum=0;
	unsigned n = datagraph->GetN();
	unsigned m = theograph->GetN();
	unsigned jcloser=0;
    double sigma = datagraph_dist /n /10.; 

	for(unsigned i=0; i<n; i++){
		datagraph->GetPoint(i, x1,y1);
		// double sigma = getSigma(datagraph, i);

		double mindist2=1.e+10;
		for(unsigned j=0; j<m; j++){
			theograph->GetPoint(j, x2,y2);
			a = x1-x2; b = y1-y2;
			dist2 = (a*a) + (b*b);
			if(dist2<mindist2) { mindist2=dist2; jcloser=j; }
		}
		
		//refine distance by interpolating closest 3 points
		double mindist_refined2=0;
		if(jcloser>0 && jcloser<m-1) {
			double x,y;
			unsigned j1=jcloser-1, j2=jcloser, j3=jcloser+1;
			TVector2 p1,p2,p3, p(x1,y1);
			theograph->GetPoint(j1, x,y); p1.Set(x,y);
			theograph->GetPoint(j2, x,y); p2.Set(x,y);
			theograph->GetPoint(j3, x,y); p3.Set(x,y);
			double mindist_refined  = dist_from_two_segments(p1,p2,p3, p);
			mindist_refined2 = mindist_refined*mindist_refined;
		} else {//reduce importance of first and last point distance
            mindist_refined2 = mindist2/n;
		}
		
		sum += mindist_refined2/sigma/sigma; //now its normalized

	}
	sum /= (n-Npars); //NdF 

	if (sum < sum_save) {//stupid root returns wrong random pars with minuit->X()
		for(unsigned i=0; i<Npars; i++) par_save[i] = par[i];
		sum_save = sum;
	}

	return sum;
}


/////////////////////////////////////////////////////////////////////////////////////
vector<float> fitReference(Limb* areflimb, Limb* alimb) {

	vector<float> result(0);
		
	originaltgraph    = areflimb->tgraph();
	theograph         = areflimb->newtgraph();
	theograph_dist    = getLength(theograph); //cache it for speed
	theograph->SetName(TString("plot_limb"+tostring(alimb->time())));

	//choose initial values for fit
	double averad     = alimb->averageRadius();
	double init_alpha = alimb->roughOrientationAngle();
	double init_xshift= thislimb_barycenter.X();
	double init_yshift= thislimb_barycenter.Y();

	//the average size of references MUST be 1.0 in TimeCourse/ and RefLimb.txt
	// the reflimbs must be centered at 0,0
	double init_pixel = 1./averad; 
		
	double maxalpha=12.0/57.3,  maxbeta=12./57.3, maxgamma=12./57.3;
	if(areflimb->time()<260) { maxbeta/=2.; maxgamma/=2.; };
	double minpix = init_pixel/1.20, maxpix = init_pixel*1.20;
	double steppix = fabs(maxpix-minpix)/100.;

	double minshiftx = init_xshift-averad/2.;
	double maxshiftx = init_xshift+averad/2.;
	double minshifty = init_yshift-averad/2.;
	double maxshifty = init_yshift+averad/2.;
	double stepshift = averad/100.;
    
	//MINUIT/////////////////////////////////////
    ROOT::Math::Minimizer* minuit = ROOT::Math::Factory::CreateMinimizer("Minuit2","minimize");
    ROOT::Math::Functor f(&calc_chi2, Npars);
    minuit->SetFunction(f);
    minuit->SetPrintLevel(0);
	minuit->SetLimitedVariable(0, "pixel",  init_pixel, steppix, minpix, maxpix);
	minuit->SetLimitedVariable(1, "alpha",  init_alpha, .02, init_alpha-maxalpha, init_alpha+maxalpha);
	minuit->SetLimitedVariable(2, "xshift", init_xshift, stepshift, minshiftx, maxshiftx);
	minuit->SetLimitedVariable(3, "yshift", init_yshift, stepshift, minshifty, maxshifty);
	minuit->SetLimitedVariable(4, "beta",   0.0, .02, -maxbeta,  maxbeta);
	minuit->SetLimitedVariable(5, "gamma",  0.0, .02, -maxgamma, maxgamma);

    if( !Enable3D ){
    	minuit->SetFixedVariable(4, "beta" ,  0.); //disable 3D rotations
    	minuit->SetFixedVariable(5, "gamma",  0.);
    }
	sum_save=1.e+10;
	minuit->SetMaxFunctionCalls(2000);
	minuit->SetStrategy(1); minuit->Minimize();

    if (minuit->Status() > 2) { //REFIT if it went wrong
	    // cout<<areflimb->time()<<" status "<<minuit->Status()<<endl;
	 	minuit->SetLimitedVariable(0, "pixel",  par_save[0], steppix, minpix, maxpix);
		minuit->SetLimitedVariable(1, "alpha",  par_save[1], .01, init_alpha-maxalpha, init_alpha+maxalpha);
		minuit->SetLimitedVariable(2, "xshift", par_save[2], stepshift, minshiftx, maxshiftx);
		minuit->SetLimitedVariable(3, "yshift", par_save[3], stepshift, minshifty, maxshifty);
		minuit->SetLimitedVariable(4, "beta",   par_save[4], .01, -maxbeta, maxbeta);
		minuit->SetLimitedVariable(5, "gamma",  par_save[5], .01, -maxgamma, maxgamma);
		minuit->SetMaxFunctionCalls(2000);
	   	minuit->SetStrategy(0);	minuit->Minimize();
	    // cout<<areflimb->time()<<" refit "<<minuit->Status()<<endl;
    }
		
	for (unsigned j=0; j < Npars; ++j) result.push_back(par_save[j]);
	calc_chi2(par_save); //make an extra call to update theograph
	    
	// cout<<"\nINIT pixel="<<init_pixel<<"\t min and max= "<< minpix<<"\t"<< maxpix<<endl;
	// cout<<"INIT alpha="<<init_alpha<<"\t min and max= "<< init_alpha-maxalpha<<"\t"<< init_alpha+maxalpha<<endl;
	// cout<<"INIT xshift="<<init_xshift<<"\t min and max= "<< minshiftx<<"\t"<< maxshiftx<<endl;
	// cout<<"INIT yshift="<<init_yshift<<"\t min and max= "<< minshifty<<"\t"<< maxshifty<<endl;
	// cout<<" refLimb fit "<<areflimb->time()<<" chi2="<<sum_save<<" Ncalls="<< minuit->NCalls() <<endl;
	// minuit->PrintResults();

    delete(minuit);
	return result;	//theograph contains the fitted shape
}


/////////////////////////////////////////////////////////////////////////////////////
void stageThisLimb(Limb* alimb) {
/////////////////////////////////////////////////////////////////////////////////////
	if(!alimb) return;
	datagraph = alimb->tgraph();
	

	bool NotSureOfSide = true;
	if(alimb->side()) NotSureOfSide = false;
	if (NotSureOfSide) {
		alimbside = 1; //assume right
		alimb->setSide(1);
	} else alimbside = alimb->side();

	double chi2, chi2_best, besttime;
	datagraph_dist = getLength(datagraph); //cache it for speed
	thislimb_barycenter = alimb->barycenter();

	int nrefs = reflimbs.size(), ibest;
	vector<float> pointtime(nrefs); 
	vector<float> pointchi2(nrefs); 
	vector< vector<float> > fitresults(nrefs);
	vector<TGraph*> graphs(nrefs);
	for (unsigned i=0; i < nrefs; i++) pointchi2[i]=9999.;

	//loop on reflimbs/////////////////////////////// 4 BY 4, first scan
	for (unsigned i=0; i < nrefs; i += 4) { 
		Limb* areflimb = reflimbs.at(i);
		
		//test: put +=4 to +=1 above and comment out this line:
		// if(areflimb->time() > 256) continue;
        // if(areflimb->time()!= alimb->time()+1) continue;//SMOOTHNESS analysis

		fitresults[i] = fitReference(areflimb, alimb); 
		pointtime[i]  = areflimb->time();
		pointchi2[i]  = sum_save;
		graphs[i]     = theograph;
	}
	ibest = indexOfMin(pointchi2);
	chi2_best = pointchi2[ibest];

	if(NotSureOfSide) { ////// Auto mode: try with flipping side
		alimbside = -1; //try as left
		vector< vector<float> > fitresults_m(nrefs);
		vector<float> pointchi2_m(nrefs);
		for (unsigned i=0; i < nrefs; i++) pointchi2_m[i]=9999.;

		vector<TGraph*>  graphs_m(nrefs);
		for (unsigned i=0; i < nrefs; i += 4) { /// 4 BY 4
			Limb* areflimb  = reflimbs.at(i);
			fitresults_m[i] = fitReference(areflimb, alimb); 
			pointchi2_m[i]  = sum_save;
			graphs_m[i]     = theograph;
		}
		int ibest_m = indexOfMin(pointchi2_m);
		float chi2_best_m = pointchi2_m[ibest_m];

		cout<<"side = "<<alimbside
			<<"  chi2_best = "<<chi2_best<<" MIRRORED= "<<chi2_best_m<<endl;

		if (chi2_best_m < chi2_best) { //indeed it was flipped!
			cout<<"Warning: flipping side is being applied. "<<alimb->side()<<endl;

			fitresults = fitresults_m;
			pointchi2  = pointchi2_m;
			graphs     = graphs_m;
			ibest      = indexOfMin(pointchi2);
			chi2_best  = pointchi2[ibest];

			alimb->setSide(-1);

		} else { //forget flipping
			alimbside = 1; //put back to right
		}
	}

	//loop on reflimbs/////////////////////////////// EVEN
	for (unsigned i=2; i < nrefs-2; i += 2) { 

		//decide if doing it or not
		if (pointchi2[i]<9998.) continue; //was already done
		float ca = pointchi2[i-2]/chi2_best;
		float cb = pointchi2[i+2]/chi2_best;
		if (ca>5. and cb>5.) continue;

		Limb* areflimb = reflimbs.at(i);
		fitresults[i] = fitReference(areflimb, alimb); 
		pointtime[i]  = areflimb->time();
		pointchi2[i]  = sum_save;
		graphs[i]     = theograph;
	}
	ibest = indexOfMin(pointchi2);
	chi2_best = pointchi2[ibest];
	// cout<<"EVEN chi2_best = "<<chi2_best<<endl<<endl;

	//loop on reflimbs/////////////////////////////// ODD
	for (unsigned i=1; i < nrefs-1; i += 2) { 

		//decide if doing it or not
		if (pointchi2[i]<9998.) continue; //was already done
		float ca = pointchi2[i-1]/chi2_best;
		float cb = pointchi2[i+1]/chi2_best;
		if (ca>4. and cb>4.) continue;

		Limb* areflimb = reflimbs.at(i);		
		fitresults[i] = fitReference(areflimb, alimb); 
		pointtime[i]  = areflimb->time();
		pointchi2[i]  = sum_save;
		graphs[i]     = theograph;
	}

	ibest = indexOfMin(pointchi2);
	chi2_best = pointchi2[ibest];

	besttime  = pointtime[ibest];
	theograph = graphs[ibest];
	minParams = fitresults[ibest];
	// cout<<"ODD chi2_best = "<<chi2_best<<endl<<endl;

	TGraph* chi2curve = new TGraph();
	TGraph* probcurve = new TGraph();
	chi2curve->SetName("chi2curve");
	probcurve->SetName("probcurve");

	//renormalize chi2:
	float N = datagraph->GetN();
	for(unsigned int kk=0; kk<pointtime.size(); kk++) {
		double ax = pointtime.at(kk);
		if (ax<0.1) continue;
		double ay = pointchi2.at(kk);

        chi2curve->SetPoint(chi2curve->GetN(), ax, ay/chi2_best );

		double newchi2 = (ay/chi2_best)*(N-Npars); //rescale errors and un-reduce it!
		double esponente    = -newchi2   * (N-Npars)/N/2. ;
		double minesponente = -(N-Npars) * (N-Npars)/N/2. ;
		double val;
		if(esponente-minesponente<-10.) val=0.;
		else val = 0.4*TMath::Exp( esponente-minesponente );
		probcurve->SetPoint(probcurve->GetN(), ax, val );
	}
	
	double hmin= reflimbs.front()->time()-1;
	double hmax= reflimbs.back() ->time()+1;
	TF1* gau = new TF1("gau","[0]*exp(-(x-[1])*(x-[1])/2./[2]/[2])/[2]", hmin,hmax);
	gau->SetParameters(0.9, besttime, 2*getRMS(probcurve));
	gau->SetParLimits(2, 0.1, 24);
	gau->SetNpx(1000);
	gau->SetLineColor(4);
	gau->SetLineWidth(2);
	if(besttime > hmin+10 && besttime< hmax-10) { //fix the gaussian average to mean value
		gau->FixParameter(1, getMean(probcurve));
	} else {
		gau->FixParameter(1, besttime);
	}
	probcurve->Fit("gau","q");

	//calculate confidence levels at 1 sigma = 67%
	double atotprob=0, stepsize=fabs(hmax-hmin)/1000;
	double plow=0, phigh=0, highpoint=0, lowpoint=0, midpoint=0;
	for (double step=hmin; step<hmax; step+=stepsize) atotprob += probcurve->Eval(step);
	for (double step=hmin; step<hmax; step+=stepsize) {
		plow += probcurve->Eval(step)/atotprob;
		if(plow<(1.-0.67)/2.) { lowpoint=step; }
		if(plow>0.5) { midpoint=step; break; }
	}
	for (double step=hmax; step>hmin; step-=stepsize) {
		phigh += probcurve->Eval(step)/atotprob;
		if(phigh>(1-0.67)/2) { highpoint=step; break; }
	}
	

	double finalerror = TMath::Max( (highpoint-lowpoint)/2., gau->GetParameter(2) );
	//add a systematic error 1h due to limited nr of litters..
	finalerror = sqrt(finalerror*finalerror+1.*1.);
	int iday = int(besttime/24.);

	alimb->setAgeDay(iday);
	alimb->setAgeTime(besttime-iday*24);
	alimb->setFitError(finalerror);
	alimb->setChi2(chi2_best);

	drawCanvas(alimb, chi2curve, probcurve);///////////////////

	return;
}

/////////////////////////////////////////////////////////////////////////////////////////
void transform_originaltgraph_3D(double scale, double alpha, double beta, double gamma,
									double xshift, double yshift) {
	//transforms global variable originaltgraph
	TVector3 xaxis(1,0,0), yaxis(0,1,0), zaxis(0,0,1);
	unsigned int m = originaltgraph->GetN();
	double x, y;
	for(unsigned int j=0;j<m; j++){
		originaltgraph->GetPoint(j, x,y);
		x *= scale; y *= scale;
		if(alimbside>0) y = -y;
		TVector3 v(x,y, 0);//promote to 3D
		TVector2 u = rotate3D(v, alpha,  beta, gamma);
		theograph->SetPoint(j, u.X()+xshift, u.Y()+yshift ); //project on xy
	}
}

/////////////////////////////////////////////////////////////////////////////////////////
double dist_from_segment(const TVector2& p1, const TVector2& p2, const TVector2& p) {
	TVector2 v = (p2-p1).Unit();
	TVector2 u = (p-p1);
	double a = u*v;
	double b = (p-p2)*v;
	double dist = TMath::Sqrt(u.Mod2() - a*a);
	if(a*b <0) return dist; //the point is inside the range of the segment
	else return TMath::Min(u.Mod(), (p-p2).Mod());
}
double dist_from_two_segments(const TVector2& p1, const TVector2& p2, 
							  const TVector2& p3, const TVector2& p){
	return TMath::Min(dist_from_segment(p1,p2, p), dist_from_segment(p2,p3, p));
}