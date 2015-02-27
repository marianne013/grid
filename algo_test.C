#include "TVector3.h"

#include <iostream>
#include <vector>
#include "line_vec.hh"

// macro to test a number of algorithm on trivial data

// (a) 'vertex' finder (point of closest approach between two non-parallel straight lines)
// (b) 3d clustering algorithm

// root [0] .L algo_test.C++
// root [1] algo_test()

using namespace std;

TVector3 find_vertex(line_vec track_a, line_vec track_b) {
  
  TVector3 start_diff = track_a.start() - track_b.start();
  TVector3 unit_a = track_a.dir_unit();
  TVector3 unit_b = track_b.dir_unit();

  float ta = ( -(start_diff*unit_a) + (start_diff *  unit_b) * (unit_a * unit_b) )/ 
    ( 1.0 - ( (unit_a * unit_b) *  (unit_a * unit_b)) );
  float tb =   ( (start_diff*unit_b) - (start_diff *  unit_a) * (unit_a * unit_b) )/ 
    ( 1.0 - ( (unit_a * unit_b) *  (unit_a * unit_b)) );

  TVector3 close_a = track_a.start()  + (ta *  unit_a);
  TVector3 close_b = track_b.start()  + (tb * unit_b);
  
  // now what I really want to store as a vertex is the middle of the Vector going from close_a to close_b
  
  cout << "find_vertex::Closest point on Vector A = " << close_a.X() << ", " << close_a.Y() << " ," << close_a.Z() << endl;
  cout << "find_vertex::Closest point on Vector B = " << close_b.X() << ", " << close_b.Y() << " ," << close_b.Z() << endl;

  TVector3 from_a_to_b = close_b - close_a;
  // conceptually that's more of a point than a vector
  TVector3 vertex = close_a + 0.5 * from_a_to_b;
  cout << "find_vertex::The vertex is here:  " << vertex.X() << ", " <<  vertex.Y() << ", " <<  vertex.Z() << endl;

  return vertex;
}

vector<TVector3> find_cluster(vector<TVector3> & vertex_cand, float cutoff = 10.0) {
  
  Int_t best_cluster_size = 0;
  vector<TVector3> best_cluster_tmp;
  vector<TVector3> best_cluster;
  for (size_t v = 0; v < vertex_cand.size(); ++v) {
    cout << "Looking at " << v << " " <<  vertex_cand[v] .X() << " " << vertex_cand[v] .Y() << " " << vertex_cand[v] .Z() << endl;
    best_cluster_tmp.clear();
    for  (size_t vv = 0; vv < vertex_cand.size(); ++vv) {
      cout << "Checking match for " << vv << " " <<  vertex_cand[vv] .X() << " " << vertex_cand[vv] .Y() << " " << vertex_cand[vv] .Z() << endl;
      Float_t dist = (vertex_cand[v] - vertex_cand[vv]).Mag();
      cout << "dist is: " << dist << endl;
      if (dist < cutoff) {
	// this includes the seed itself
	best_cluster_tmp.push_back(vertex_cand[vv]);
      }
    } // vv
    // see if this seed is better than any of the previous ones
    cout << "This cluster " << v << " has size " <<  best_cluster_tmp.size() << ", best cluster size so far: " << best_cluster_size << endl;
    if (Int_t(best_cluster_tmp.size()) > best_cluster_size) {
      cout << "New best cluster size found !" << endl;
      // if yes, keep these for future reference
      best_cluster_size = best_cluster_tmp.size();
      best_cluster = best_cluster_tmp;
    }
  } // v
  return best_cluster;
} // find_cluster

// returns the average in x,y,z for a cluster
TVector3 vertex_ave(vector<TVector3> & vertex_cluster) {
  Float_t x_ave = 0.0;
  Float_t y_ave = 0.0;
  Float_t z_ave = 0.0;
  for (size_t v = 0; v < vertex_cluster.size(); ++v) {
    x_ave += vertex_cluster[v].X();
    y_ave += vertex_cluster[v].Y();
    z_ave += vertex_cluster[v].Z();
  }
  Float_t noc = Float_t(vertex_cluster.size());
  TVector3 ave_vert(x_ave/noc, y_ave/noc, z_ave/noc);
  return ave_vert;
    
} // vertex ave


void algo_test() {
  
  // Vector A starts at (0.0,0.5,0.5) and points along (1,1,1) (too simple ?)
  // Vector B starts at (2,1,1) and points along (0.5, 0.5, 4)
  TVector3 dir_a(1.0,1.0,1.0);  // (1.0,1.0,1.0)
  TVector3 dir_b(0.5, 0.5, 4.0); // (0.5, 0.5, 4.0) 

  TVector3 unit_a = dir_a.Unit();
  TVector3 unit_b = dir_b.Unit();

  // check for parallel vectors and bow out if they are
  TVector3 cross = unit_a.Cross(unit_b);
  // account for floats
  if (cross.Mag() < 0.01)  {
    cout << "These vectors seem to be parallel, there won't be a vertex !" << endl; 
    exit(0);
  }


  TVector3 start_a(0.0, 0.5, 0.5);  
  TVector3 start_b(2.0, 1.0, 1.0); 
  TVector3 start_diff = start_a - start_b;

  float ta = ( -(start_diff*unit_a) + (start_diff *  unit_b) * (unit_a * unit_b) )/ 
    ( 1.0 - ( (unit_a * unit_b) *  (unit_a * unit_b)) );
  float tb =   ( (start_diff*unit_b) - (start_diff *  unit_a) * (unit_a * unit_b) )/ 
    ( 1.0 - ( (unit_a * unit_b) *  (unit_a * unit_b)) );

  TVector3 close_a = start_a + (ta *  unit_a);
  TVector3 close_b = start_b + (tb * unit_b);
  
  // now what I really want to store as a vertex is the middle of the Vector going from close_a to close_b
  

  cout << "Closest point on Vector A = " << close_a.X() << ", " << close_a.Y() << " ," << close_a.Z() << endl;
  cout << "Closest point on Vector B = " << close_b.X() << ", " << close_b.Y() << " ," << close_b.Z() << endl;

  TVector3 from_a_to_b = close_b - close_a;
  // conceptually that's more of a point than a vector
  TVector3 vertex = close_a + 0.5 * from_a_to_b;
  cout << "The vertex is here:  " << vertex.X() << ", " <<  vertex.Y() << ", " <<  vertex.Z() << endl;

  // now try this with the find_vertex function
  line_vec line_a(start_a, start_a+dir_a);
  line_vec line_b(start_b, start_b+dir_b);
  
  TVector3 vertex_again = find_vertex(line_a, line_b);
  

  // test the clustering algorithm
  TVector3 vec_a(1.0, 1.0, 1.0);
  TVector3 vec_b(2.0, 2.0, 2.0);
  TVector3 vec_c(3.0, 3.0, 3.0);
  TVector3 vec_a1(1.1, 1.0, 1.0);
  TVector3 vec_b1(2.1, 2.0, 2.0);
  TVector3 vec_c1(3.1, 3.0, 3.0);
  TVector3 vec_a2(1.1, 1.2, 1.0);
  TVector3 vec_b2(2.1, 2.2, 2.0);
  TVector3 vec_c2(3.1, 3.0, 3.2);
  TVector3 vec_a3(3.1, 1.2, 1.0);
  TVector3 vec_b3(3.1, 2.3, 2.0);
  TVector3 vec_c3(3.4, 3.4, 3.4);
  TVector3 vec_a4(2.1, 2.2, 2.0);
  TVector3 vec_b4(2.1, 2.3, 2.0);
  TVector3 vec_c4(2.4, 2.4, 2.4);

  vector<TVector3> points;
  points.push_back(vec_a);  points.push_back(vec_b);  points.push_back(vec_c);
  points.push_back(vec_a1);  points.push_back(vec_b1);  points.push_back(vec_c1);
  points.push_back(vec_a2);  points.push_back(vec_b2);  points.push_back(vec_c2);
  points.push_back(vec_a3);  points.push_back(vec_b3);  points.push_back(vec_c3);
  points.push_back(vec_a4);  points.push_back(vec_b4);  points.push_back(vec_c4);

  vector<TVector3> good_points = find_cluster(points, 1.0);
  cout << good_points.size() << endl;
  TVector3 vertex_av = vertex_ave(good_points);
  cout << "Cluster average: " << vertex_av.X() << " " << vertex_av.Y() << " " << vertex_av.Z() << endl; 


  vector<TVector3> test_ave;
  test_ave.push_back(vec_a);
  test_ave.push_back(vec_b);
  test_ave.push_back(vec_c);
  TVector3 av = vertex_ave(test_ave);
  cout << "vertex_ave test: " <<  av.X() << " " << av.Y() << " " << av.Z() << endl; 


  // Line defined by two points - how far is the third point away ?
  TVector3 point_one(1.0, 1.0, 1.0);
  TVector3 point_two(2.0, 1.0, 1.0);
  TVector3 point_three(1.5, 1.5, 1.0);
  TVector3 point_four(1.5, 1.0, 1.0);
  
  // thanks to Wolfram Alpha
  // line is x1, x2, point is x0
  // x = cross prduct
  // d = |(x2 - x1) x (x1 - x0)| / | x2-x1 |

  Float_t d1 =  ((point_two - point_one).Cross(point_one - point_three)).Mag() /
    (point_two - point_one).Mag();
  cout << "d1: " << d1 << endl;
  Float_t d2 =  ((point_two - point_one).Cross(point_one - point_four)).Mag() /
      (point_two - point_one).Mag();
  cout << "d2: " << d2 << endl;

}


