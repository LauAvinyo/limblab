#ifndef stager_H_
#define stager_H_
#include "utilities.h"


Double_t getSigma(const TGraph* g, unsigned int i);

double calc_chi2(const double *par);

void transform_originaltgraph_3D(double scale, double alpha, double beta, double gamma,	double xshift, double yshift);

void stageThisLimb(Limb* alimb);



#endif