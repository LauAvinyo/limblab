/*
 * Limb.cpp
 *
 *  Created on: Feb 10, 2011
 *      Author: mmusy
 */

#include "Limb.h"

Limb::Limb() {}
Limb::~Limb() {}

void      Limb::setPoints( vecpoints& a ) { m_points=a; };
vecpoints Limb::points() { return m_points; };

void  Limb::setAgeDay( int a ) { m_AgeDay=a; };
int   Limb::ageDay() { return m_AgeDay; };

void  Limb::setAgeTime( int a ) { m_AgeTime=a; };
int   Limb::ageTime() { return m_AgeTime; };
float Limb::time() { return m_AgeDay*24.0+m_AgeTime; };

float Limb::chi2() { return m_chi2; };
void  Limb::setChi2(float a)  { m_chi2 = a;};

TGraph* Limb::tgraph() const { return m_graph; }
void    Limb::setTGraph(TGraph* a) { this->m_graph = a;}

void    Limb::setJpgName( TString a ) { m_jpgname=a; };
TString Limb::jpgname() { return m_jpgname; };

void    Limb::setUserName( TString a ) { m_username=a; };
TString Limb::username() { return m_username; };

void  Limb::setFitError(float a) { this->m_fitError=a; }
float Limb::fitError() { return m_fitError; }

void Limb::setSide( int a ) { m_side=a; };
int  Limb::side() { return m_side; };


TVector2 Limb::barycenter() {
	TVector2 bary(0.0,0.0);
	if(m_points.empty()) return bary;
	for(std::vector<TVector2>::iterator i=m_points.begin(); i!=m_points.end(); i++) {
		bary += (*i);
	}
	return bary/m_points.size();
}

float Limb::averageRadius() {
	TVector2 bary = this->barycenter();
	float meanr=0;
	if(m_points.empty()) return 1;
	for(std::vector<TVector2>::iterator i=m_points.begin(); i!=m_points.end(); i++) {
		meanr += ((*i)-bary).Mod();
	}
	return meanr/m_points.size();
}

float Limb::roughOrientationAngle() {
	TVector2 v1 = m_points.front();
	TVector2 v2 = m_points.back();
	TVector2 b = this->barycenter();
	float alpha = (b-v1 + b-v2).Phi();
	return alpha;
}

TGraph* Limb::newtgraph() {

	int R = m_points.size();
	TGraph* tgreflimb = new TGraph(R);
	for(std::vector<TVector2>::iterator i = m_points.begin(); i!= m_points.end(); i++){
		TVector2 p = (*i);
		tgreflimb->SetPoint(distance(m_points.begin(),i), p.X(), -p.Y());
	}
	tgreflimb->SetName("newtgraph");
	return tgreflimb;
}

