#include "plotter.h"
#include "stager.h"
#include "utilities.h"
using namespace std;

extern TGraph* datagraph;
extern TGraph* theograph;
extern double datagraph_dist;
extern vector<float> minParams;
extern vector<Limb*> reflimbs;

/////////////////////////////////////////////////////////////

void drawCanvas(Limb* alimb, TGraph* chi2curve, TGraph* probcurve) {
	
	if(!theograph) return;

	const int Nptxy = 300;
	TCanvas* canvas = new TCanvas("c1", "Staging System Output",0,0, 1200*1., 620*1.);
	fixAspectRatio(datagraph);

	double besttime  = alimb->time();
	double chi2_best = alimb->chi2();
	double finalerror= alimb->fitError();

	for (int i =0; i<theograph->GetN(); i++){
		double xp,yp; theograph->GetPoint (i, xp, yp);
		cout<<"FITSHAPE  "<<xp<<"  "<<yp<<endl;	
	}

	canvas->Clear();
	canvas->Divide(2,1);
	canvas->cd(1);
	canvas->SetBorderMode(0);
	canvas->SetFrameBorderMode(0);
	canvas->SetFillColor(10);
	canvas->SetFixedAspectRatio();
	gStyle->SetDrawBorder(0);
	gStyle->SetOptFit(0);
	gStyle->SetOptStat(0);
	gStyle->SetOptTitle(0);
	gStyle->SetPalette(8);
	gPad->SetFillColor(10);

	gPad->SetTopMargin(   0.14); 
	gPad->SetBottomMargin(0.06); 

	double xmin = datagraph->GetXaxis()->GetXmin(), ymin = datagraph->GetYaxis()->GetXmin();
	double xmax = datagraph->GetXaxis()->GetXmax(), ymax = datagraph->GetYaxis()->GetXmax();
	TF2* g2d = new TF2("g2d", gaussian2D, xmin,xmax,ymin,ymax, 0);
	g2d->SetNpx(Nptxy); g2d->SetNpy(Nptxy);
	g2d->GetXaxis()->SetLabelSize(0.0); g2d->GetYaxis()->SetLabelSize(0.0);
	g2d->GetXaxis()->SetTitleSize(0.0); g2d->GetYaxis()->SetTitleSize(0.0);
	g2d->GetXaxis()->SetTickLength(0.0);g2d->GetYaxis()->SetTickLength(0.0);
	g2d->SetMinimum(0.0); //looks nicer
	g2d->Draw("col");

	theograph->SetLineWidth(3); theograph->Draw("PL");
	std::string aa = "";
	TLatex warnp; warnp.SetTextSize(0.035); warnp.SetTextAngle(5); warnp.SetTextColor(kRed+1);
	if(datagraph->GetN()<20) aa= "WARNING! Low number of points";
	if(datagraph->GetN()<15) aa= "WARNING! Very low number of points";
	warnp.DrawTextNDC(0.2, 0.48, aa.c_str());

	//warn about too different length of data vs fit shape
	double theograph_dist=getLength(theograph);
	double diffdist = fround(100.*fabs(theograph_dist- datagraph_dist)/datagraph_dist, 0);
	TLatex warn_l; warn_l.SetTextSize(0.033); warn_l.SetTextAngle(5); warn_l.SetTextColor(kRed+1);
	if (diffdist > 15) {
		aa= "WARNING! Lengths different by "+tostring(diffdist)+TString("\%");
		warn_l.DrawTextNDC(0.2, 0.40, aa.c_str());
	}
	cout<< "Total lengths different by "<< diffdist << " per cent"<<endl;

	//draw barycenter and axes in space
	draw3DAxes(); 

	chi2curve->GetYaxis()->SetTitle( "scaled #chi_{#nu}^{2}" );
	canvas->cd(2); gPad->SetFillColor(10); gPad->Divide(1,2); gPad->cd(1);
	chi2curve->SetMinimum(0); chi2curve->SetMaximum(3.99);
	chi2curve->GetYaxis()->SetLabelSize(0.05);
	chi2curve->GetXaxis()->SetLabelSize(0.05);
	chi2curve->GetXaxis()->SetTitleSize(0.05);
	chi2curve->GetYaxis()->SetTitleSize(0.05);
	chi2curve->GetXaxis()->SetTickLength(-0.01);chi2curve->GetYaxis()->SetTickLength(0.02);
	chi2curve->Draw("APL");

	TLatex latex; latex.SetTextSize(0.075);latex.SetTextAngle(0);
	aa =  "#chi_{#nu}^{2} = "+tostring(fround(chi2_best, 1));
	latex.DrawLatex(besttime-8., .35, TString(aa) );

	aa = "";
	if(chi2_best>  5) aa = "#color[91]{WARNING! High #chi_{#nu}^{2}}";
	if(chi2_best>  8) aa = "#color[2]{WARNING! Very high #chi_{#nu}^{2}}";
	latex.SetTextSize(0.08); latex.SetTextAngle(5);
	latex.DrawLatex(275, 2, TString(aa) );

	double hmin= reflimbs.front()->time()-1;
	double hmax= reflimbs.back() ->time()+1;
	chi2curve->GetXaxis()->SetLimits(hmin, hmax);
	TLine chiline(hmin,1, hmax,1); chiline.SetLineColor(40); chiline.SetLineStyle(2); chiline.Draw();
	chi2curve->SetMarkerStyle(21);chi2curve->SetMarkerSize(0.7);chi2curve->SetMarkerColor(9);
	canvas->cd(2); gPad->SetFillColor(10); gPad->cd(2);
	//calculate confidence levels at 1 sigma = 67%
	double atotprob=0, stepsize=(hmax-hmin)/1000,
			plow=0, phigh=0, highpoint=0, lowpoint=0, midpoint=0;
	for (double step=hmin; step<hmax; step+=stepsize) atotprob += probcurve->Eval(step);
	for (double step=hmin; step<hmax; step+=stepsize) {
		plow += probcurve->Eval(step)/atotprob;
		if(plow<(1-0.67)/2) { lowpoint=step; }
		if(plow>0.5) { midpoint=step; break; }
	}
	for (double step=hmax; step>hmin; step-=stepsize) {
		phigh += probcurve->Eval(step)/atotprob;
		if(phigh>(1-0.67)/2) { highpoint=step; break; }
	}

	probcurve->SetLineWidth(1);
	probcurve->SetLineStyle(3);
	probcurve->SetMarkerStyle(7);
	probcurve->GetXaxis()->SetTitle("staging time (hours)");
	probcurve->GetYaxis()->SetTitle("prob. density");
	probcurve->GetXaxis()->SetTitleSize(0.05);
	probcurve->GetYaxis()->SetTitleSize(0.05);
	probcurve->GetYaxis()->SetLabelSize(0.05);
	probcurve->GetXaxis()->SetLabelSize(0.05);
	probcurve->GetXaxis()->SetLimits(hmin, hmax);
	probcurve->SetMaximum(0.449); probcurve->SetMinimum(0.); 
	probcurve->GetXaxis()->SetTickLength(0.02);probcurve->GetYaxis()->SetTickLength(0.02);
	probcurve->Draw("AP");
	gPad->RedrawAxis();

	TF1* gau = probcurve->GetFunction("gau");
	TLatex ltext; ltext.SetTextSize(0.05);
	aa =  "Median:  "+tostring(fround(midpoint, 1))
    				 +"^{+" +tostring(fround(highpoint-midpoint,1))+"}"
    				 +"_{--"+tostring(fround(midpoint -lowpoint,1))+"} h";
	ltext.DrawLatex(255., .36, TString(aa) );
	aa =  "Mean:     "+tostring(fround(gau->GetParameter(1),1))
    				  +" #pm"+tostring(fround(gau->GetParameter(2),1))+" h";
	ltext.DrawLatex(255., .40, TString(aa) );
	
	canvas->cd(1);

	//add #somites and forelimb estimation
	TString som_s = "", forel_s="";
	if (besttime<330) {
		ltext.SetTextSize(0.033);
		ltext.SetTextFont(62);
		double foretime     = (besttime-1.565)/1.028; //alex calibration
		double foretime_day = int(foretime/24.);
		double foretime_h   = fround(foretime - foretime_day*24., 0);
		TString foretime_hs = foretime_h<10 ? "0":"";
		foretime_hs += tostring(foretime_h);

		double nrsom          = 0.37 * besttime -54.225;//alex calibration
		double nrsom_forelimb = 0.37 * foretime -54.225;//alex calibration
		double nrsom_e = finalerror*0.37+0.5;
		som_s = ",  nr.somites: "+
			tostring(fround(nrsom, 1))+" #pm"+tostring(fround(nrsom_e, 1));
		forel_s = " #color[50]{ (if forelimb: mE"+
			tostring(foretime_day)+":"+foretime_hs+
			",  nr.somites: "+tostring(fround(nrsom_forelimb, 1))+
			")}";
	}

	int iday = int(besttime/24.);
	TString sres = "#color[2]{  Hindlimb is: mE"+tostring(iday)+":"
			+(besttime-iday*24 <10 ? "0":"") + tostring(besttime-iday*24)
			+ " #pm" + tostring(fround(finalerror,1))+ "h"+som_s+"}";

	ltext.SetTextSize(0.035); ltext.SetTextAngle(0); ltext.SetNDC(1);
	if (besttime<330) {
		ltext.DrawLatex(0.09,0.930, sres);
		ltext.SetTextSize(0.032);
		ltext.DrawLatex(0.09,0.885, forel_s);
	}
	else {
		ltext.DrawLatex(0.09,0.900, sres);
	}

	//filename l/r
	ltext.SetTextSize(0.025); ltext.SetTextColor(1);ltext.SetTextFont(102);
	ltext.DrawLatex(0.122,0.825, alimb->jpgname());
	ltext.DrawLatex(0.122,0.798, alimb->side()<0? "left side":"right side");

	//date of process and code version
	ltext.SetTextColor(1); ltext.SetTextSize(0.020);
	//TDatime datatime;
	//ltext.DrawLatex(0.050,0.005, "User: "+TString(alimb->username())+", "+
	//	TString(datatime.AsString())+", LimbStager v7.2");

	canvas->cd(2); gPad->cd(2);
	TArrow *arrow1 = new TArrow(alimb->time(),0.1,alimb->time(),0.0 ,0.015,"|>");
	arrow1->SetFillColor(10); arrow1->SetLineColor(2); arrow1->SetLineStyle(2);
	if(alimb->time()>=hmin and alimb->time()<=hmax){
		if(alimb->time()>hmin && alimb->time()<hmax) arrow1->Draw();
	}
	TArrow *arrow2 = new TArrow(besttime,0.1,besttime,0.0 ,0.015,"|>");
	if(besttime>=hmin && besttime<=hmax){
		arrow2->SetFillColor(2);  arrow2->SetLineColor(2); arrow2->Draw();
	}

	//labels Exx:xx
	TLatex lab0; lab0.SetTextSize(0.05); lab0.SetTextAngle(80.);
	TLatex lab1; lab1.SetTextSize(0.05); lab1.SetTextAngle(80.);
	TLatex lab2; lab2.SetTextSize(0.05); lab2.SetTextAngle(80.);
	TLatex lab3; lab3.SetTextSize(0.05); lab3.SetTextAngle(80.);
	TLatex lab4; lab4.SetTextSize(0.05); lab4.SetTextAngle(80.);
	TLatex lab5; lab5.SetTextSize(0.05); lab5.SetTextAngle(80.);
	TLatex lab6; lab6.SetTextSize(0.05); lab6.SetTextAngle(80.);
	TLatex lab7; lab7.SetTextSize(0.05); lab7.SetTextAngle(80.);
	TLatex lab8; lab8.SetTextSize(0.05); lab8.SetTextAngle(80.);
	TLatex lab9; lab9.SetTextSize(0.05); lab9.SetTextAngle(80.);
	TLatex lab10; lab10.SetTextSize(0.05); lab10.SetTextAngle(80.);
	TLatex lab11; lab11.SetTextSize(0.05); lab11.SetTextAngle(80.);
	TLatex lab12; lab12.SetTextSize(0.05); lab12.SetTextAngle(80.);
	lab0.DrawLatex(249., .46, TString("E10:09") );
	lab1.DrawLatex(261., .46, TString("E10:21") );
	lab2.DrawLatex(273., .46, TString("E11:09") );
	lab3.DrawLatex(285., .46, TString("E11:21") );
	lab4.DrawLatex(297., .46, TString("E12:09") );
	lab5.DrawLatex(309., .46, TString("E12:21") );
	lab6.DrawLatex(321., .46, TString("E13:09") );
	lab7.DrawLatex(333., .46, TString("E13:21") );
	lab8.DrawLatex(345., .46, TString("E14:09") );
	lab9.DrawLatex(357., .46, TString("E14:21") );
	lab10.DrawLatex(369.,.46, TString("E15:09") );
	lab11.DrawLatex(381.,.46, TString("E15:21") );

	////////////////////////////////////////////////////////////////////////
	canvas->cd(); canvas->Update();

	//on server:
	// TString	picname= "newstagingsystem/userarea/"+alimb->username()+"/"+alimb->jpgname()+"_SI.gif";
    // if(alimb->jpgname()=="default.JPG") picname="newstagingsystem/userarea/demo/default.JPG.gif";
	//otherwise:
	TString	picname= alimb->jpgname()+".png";

	//cout<<"Printing "<<picname<<endl;
	canvas->Print(picname);

	g2d->Delete();
	chi2curve->Delete();
	probcurve->Delete();
	datagraph->Delete();
	theograph->Delete();

	//printout//////////////////////
	for (int j=0; j<6; ++j) cout<<j<<" Parameter = "<<fround(minParams[j],4)<<endl;
	cout<< "Min chi2    = "<< chi2_best <<endl;
    cout<< "PREDICTED age "<<iday<<":"<< (besttime-iday*24 < 10 ? "0":"")<< besttime-iday*24//dont change
        << " (" << besttime <<"h +-"<<fround(finalerror,1)<<"h) \tname= "<< alimb->jpgname()<<endl;

	return;
}


/////////////////////////////////////////////////////////////////////////////////////////
Double_t gaussian2D(Double_t* x, Double_t* par){

	double xmean , ymean;
	unsigned int n = datagraph->GetN();

	double gaus = 0;
	for(unsigned int i =0; i<n; i++){
		datagraph->GetPoint(i, xmean, ymean);
		double sigma = getSigma(datagraph, i)  /.3; // 3. is for visualization only
		double rx=(x[0]-xmean)/sigma;
		double ry=(x[1]-ymean)/sigma;
		double expo = rx*rx + ry*ry;
		if(expo>10) continue;
		gaus += TMath::Exp(-expo/2.) /sigma;
	}
	return gaus*40.0 /n ;
}

//////////////////////////////////////////////////////////////////////////////////////////
void draw3DAxes() {

	double alpha = minParams[1];
	double beta  = minParams[4];
	double gamma = minParams[5];

	TVector3 xaxis(1,0,0), yaxis(0,1,0), zaxis(0,0,1);
	double arrsize = (theograph->GetXaxis()->GetXmin() - theograph->GetXaxis()->GetXmax())/8.;

    TVector2 theob = barycenterof(theograph);
	TVector2 xaxis2 = rotate3D(xaxis, alpha, beta, gamma)* -arrsize + theob;
	TVector2 yaxis2 = rotate3D(yaxis, alpha, beta, gamma)* -arrsize + theob;
	TVector2 zaxis2 = rotate3D(zaxis, alpha, beta, gamma)*  arrsize + theob;

	double parrsize=0.005;
	TArrow*  xarr = new TArrow(xaxis2.X(), xaxis2.Y(), theob.X(), theob.Y(), parrsize, "<|");
	TArrow*  yarr = new TArrow(yaxis2.X(), yaxis2.Y(), theob.X(), theob.Y(), parrsize, "<|");
	TArrow*  zarr = new TArrow(zaxis2.X(), zaxis2.Y(), theob.X(), theob.Y(), parrsize, "<|");

	double offs = arrsize/6;
	TLatex* xlat = new TLatex(xaxis2.X()-offs, xaxis2.Y()+offs,"x");
	xlat->SetTextFont(12); xlat->SetTextColor(9); xlat->SetTextSize(0.03); xlat->Draw();
	TLatex* ylat = new TLatex(yaxis2.X()+offs, yaxis2.Y()+offs,"y");
	ylat->SetTextFont(12); ylat->SetTextColor(8); ylat->SetTextSize(0.03); ylat->Draw();
	TLatex* zlat = new TLatex(zaxis2.X()-offs, zaxis2.Y()+offs,"z");
	zlat->SetTextFont(12); zlat->SetTextColor(633); zlat->SetTextSize(0.03); zlat->Draw();

	xarr->SetLineColor(9); xarr->SetFillColor(9); xarr->SetLineWidth(2); xarr->Draw();
	yarr->SetLineColor(8); yarr->SetFillColor(8); yarr->SetLineWidth(2); yarr->Draw();
	zarr->SetLineColor(633); zarr->SetFillColor(633); zarr->SetLineWidth(2); zarr->Draw();
}


/////////////////////////////////////////////////////////////////////////////////////////
void fixAspectRatio(TGraph* gr) {//, double size=0

	double xmin = gr->GetXaxis()->GetXmin();
	double xmax = gr->GetXaxis()->GetXmax();
	double ymin = gr->GetYaxis()->GetXmin();
	double ymax = gr->GetYaxis()->GetXmax();

	double rangex = xmax-xmin;
	double rangey = ymax-ymin;
	double commonrange = TMath::Max(rangex, rangey);

	double xmin_new = (xmin+rangex/2) - commonrange/2;
	double xmax_new = (xmin+rangex/2) + commonrange/2;
	double ymin_new = (ymin+rangey/2) - commonrange/2;
	double ymax_new = (ymin+rangey/2) + commonrange/2;

	// if(size!=0) { ymin_new=xmin_new=-size; ymax_new=xmax_new=size; }

	gr->GetXaxis()->SetLimits(xmin_new, xmax_new);
	gr->GetYaxis()->SetLimits(ymin_new, ymax_new);
}

//////////////////////////////////////////////////////////////////////////////////
double getMean(TGraph* gr) {
	double res=0,den=0;
	int n=gr->GetN();
	for(int i=0; i<n; i++){
		double x1,y1;
		gr->GetPoint(i, x1,y1);
		res += x1*y1;
		den += y1;
	}
	return res/den;
}

//////////////////////////////////////////////////////////////////////////////////
double getRMS(TGraph* gr) {
	double res=0,den=0;
	double mean= getMean(gr);
	int n=gr->GetN();
	for(int i=0; i<n; i++){
		double x1,y1;
		gr->GetPoint(i, x1,y1);
		res += (x1-mean) * (x1-mean)*y1;
		den += y1;
	}
	return TMath::Sqrt(res/den);
}

////////////////////////////////////////////////////////////////////////////////////
double fround(double n, int d){
	double base=10;
	return floor(n * pow(base, d) + .5) / pow(base, d);
}
