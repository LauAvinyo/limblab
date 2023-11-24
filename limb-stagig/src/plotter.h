#ifndef plotter_H_
#define plotter_H_
#include "utilities.h"

void drawCanvas(Limb* alimb, TGraph* chi2curve, TGraph* probcurve);

Double_t gaussian2D(Double_t* x, Double_t* par);

void draw3DAxes();

void fixAspectRatio(TGraph* gr);

double fround(double n, int d);


#endif