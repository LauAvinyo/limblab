#ifndef UTILITIES_H_
#define UTILITIES_H_

#include <Riostream.h>
#include <vector>
#include <iostream>
#include <stdlib.h>

#include <TMath.h>
#include <TStyle.h>
#include <TString.h>
#include <TROOT.h>
#include <TGraph.h>
#include <TF1.h>
#include <TF2.h>
#include <TH2F.h>
#include <TCanvas.h>
#include <TVirtualFitter.h>
#include <TAxis.h>
#include <TFitResult.h>
#include <TFitResultPtr.h>
#include <TLine.h>
#include <TVector2.h>
#include <TVector3.h>
#include <TLatex.h>
#include <TArrow.h>
#include <TRotation.h>
#include <TString.h>
#include <TObjString.h>

#include "Limb.h"

#include <sstream>
// #define tostring( x ) static_cast< std::ostringstream & >( ( std::ostringstream() << std::dec << x ) ).str()

std::string tostring(float k);

TString getword(int i, TString line);

int getwordnr(TString line);

double getLength(const TGraph *gr);

TVector2 barycenterof(const TGraph *gr);

TVector2 rotate3D(const TVector3 &u, const double &alpha, const double &beta, const double &gamma);

double getMean(TGraph *gr);

double getRMS(TGraph *gr);

double dist_from_segment(const TVector2 &p1, const TVector2 &p2, const TVector2 &p);
double dist_from_two_segments(const TVector2 &p1, const TVector2 &p2, const TVector2 &p3,
							  const TVector2 &p);

int indexOfMin(std::vector<float> &v);

#endif /* UTILITIES_H_ */
