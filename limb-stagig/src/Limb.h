/*
 * Limb.h
 *
 *  Created on: Feb 10, 2011
 *      Author: mmusy
 */

#ifndef LIMB_H_
#define LIMB_H_

#include <TGraph.h>
#include <TVector2.h>
#include <TVector3.h>
#include <TString.h>
#include <vector>

typedef std::vector<TVector2> vecpoints;


class Limb {

public:
	Limb();
	virtual ~Limb();

    void    setUserName(TString a);
    TString username();

    void    setJpgName(TString a) ;
    TString jpgname();

    void      setPoints( vecpoints& a );
    vecpoints points();

    void setAgeDay( int a ) ;
    int  ageDay();
    
    void setAgeTime( int a ) ;
    int  ageTime();

    void setSide( int a ) ;
    int  side() ;
        
    void  setChi2(float a);
    float chi2();

    void    setFitError(float a);
    float   fitError();

    void    setTGraph(TGraph* );
    TGraph* tgraph() const;
    TGraph* newtgraph();

    float time();
    TVector2 barycenter();
    float averageRadius();
    float roughOrientationAngle();
 

private:
    int       m_side, m_AgeDay, m_AgeTime;
    vecpoints m_points;
	TGraph*   m_graph;
    float     m_chi2, m_fitError;
    TString   m_username, m_jpgname;
};

#endif /* LIMB_H_ */
