// store photon as starting point (last point in simulation) and 
// direction (first point outside head - last point)
// i.e. the resulting vector will point towards the head/tumor

#ifndef __LINE_VEC_HH__
#define __LINE_VEC_HH__

#include <TObject.h>
#include <TVector3.h>

class line_vec  : public TObject {
private:
  
  TVector3 _sp;
  TVector3 _d;
public:
  line_vec();
  // construct vector from two point
  line_vec(TVector3 starting_point,  TVector3 second_point);
  ~line_vec();
  TVector3 start() { return _sp;}
  TVector3 dir_unit() {return _d.Unit(); }

  //  ClassDef(line_vec, 0);
};

line_vec::line_vec() {
  // I might want to change this to something more pronounced
  // in principle all TVector3 are initialized to 0,0,0
    _d = TVector3(0.0, 0.0, 0.0);
    _sp = TVector3(0.0, 0.0, 0.0);
  }

line_vec::line_vec(TVector3  starting_point,  TVector3 second_point) {
  _sp = starting_point;
  _d = second_point - starting_point;
}

line_vec::~line_vec() {

}
#endif
