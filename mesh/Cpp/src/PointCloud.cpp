#include <stdio.h>
#include <iostream>
#include <vector>
#include <algorithm> 
#include "dec_util.h"
#include "PointCloud.h"


PointCloud::PointCloud(std::vector<Eigen::VectorXd>& P, int k): data{P}, tree(3, data){
    tree.buildIndex();
    this->num_v = P.size();
    this->E.resize(k*P.size(), 2);
    int cnt = 0;
    for (int i = 0; i < P.size(); ++i)
    {
        std::vector<size_t> neighbors = kNearestNeighbors(i, k);
        for (int j = 0; j < neighbors.size(); ++j)
        { 
            this->E(cnt, 0) = i;
            this->E(cnt, 1) = neighbors[j]; 
            cnt++;
        }
        /* code */
    }
    this->E = preprocess_matrix(this->E);
    for (int i = 0; i < this->E.rows(); ++i)
    {
        this->map_e.insert(std::pair<key_e, int>(std::make_tuple(this->E(i, 0), this->E(i, 1)), i));
        // std::cout<<"cur: "<<i<<", i: "<<E(i,0)<<", j:"<<E(i,1)<<std::endl;
    }
    // this->E.conservativeResize(cnt, 2); 
    //  
    this->init_indices();
    this->build_boundary_mat1();
}

// void PointCloud::initialize(Eigen::MatrixXd &P, double distance){
// 	this->num_v = P.rows();
// 	Eigen::MatrixXd dis = Eigen::MatrixXd::Zero(P.rows(), P.rows());
// 	this->E.resize(2*P.rows(), 2);
// 	int cnt = 0;
// 	for (int i = 0; i < P.rows()-1; ++i)
// 	{
// 		for (int j = i+1; j < P.rows(); ++j)
// 		{
// 			dis(i, j) = (P.row(i)-P.row(j)).norm();
// 			if (dis(i, j) < distance)
// 			{
// 				/* code */
// 				this->E(cnt, 0) = i;
// 				this->E(cnt, 1) = j;
// 				this->map_e.insert(std::pair<key_e, int>(std::make_tuple(i, j), cnt));
// 				cnt++;
// 			}
// 		}
// 	}
// 	std::cout<<"max distance:"<<dis.rowwise().maxCoeff().maxCoeff()<<", min distance:"<<dis.rowwise().minCoeff().minCoeff()<<std::endl;
// 	std::cout<<"cnt:"<<cnt<<std::endl;
// 	this->E.conservativeResize(cnt, 2); 
// 	//
// 	this->init_indices();
// 	this->build_boundary_mat1();
// }

std::vector<size_t> PointCloud::kNearest(Eigen::VectorXd query, size_t k) {
    if (k > data.points.size()) throw std::runtime_error("k is greater than number of points");
    std::vector<size_t> outInds(k);
    std::vector<double> outDistSq(k);
    tree.knnSearch(&query[0], k, &outInds[0], &outDistSq[0]);
    return outInds;
}

std::vector<size_t> PointCloud::kNearestNeighbors(size_t sourceInd, size_t k) {
    if ((k + 1) > data.points.size()) throw std::runtime_error("k+1 is greater than number of points");

    std::vector<size_t> outInds(k + 1);
    std::vector<double> outDistSq(k + 1);
    tree.knnSearch(&data.points[sourceInd](0), k + 1, &outInds[0], &outDistSq[0]);

    // remove source from list
    bool found = false;
    for (size_t i = 0; i < outInds.size(); i++) {
      if (outInds[i] == sourceInd) {
        outInds.erase(outInds.begin() + i);
        // outDistSq.erase(outDistSq.begin() + i);
        found = true;
        break;
      }
    }

    // if the source didn't appear, just remove the last point
    if (!found) {
      outInds.pop_back();
      outDistSq.pop_back();
    }

    return outInds;
}

void PointCloud::init_indices(){
    this->Vi.resize(this->num_v);
    for (int i = 0; i < this->num_v; ++i){
        this->Vi[i] = i;
    }
    this->Ei.resize(this->E.rows());
    for (int i = 0; i < this->E.rows(); ++i){ 
        this->Ei[i] = i;
    }
    this->Fi.resize(this->F.rows());
    for (int i = 0; i < this->F.rows(); ++i){
        this->Fi[i] = i;
    }
}

void PointCloud::build_boundary_mat1(){
    this->bm1.resize(this->num_v, this->E.rows());
    std::vector<Eigen::Triplet<int> > tripletList;
    tripletList.reserve(2*this->E.rows());
    for(int i=0; i<this->E.rows(); i++){
        tripletList.push_back(Eigen::Triplet<int>(this->E(i,0), i, -1));
        tripletList.push_back(Eigen::Triplet<int>(this->E(i,1), i, 1));
    }
    this->bm1.setFromTriplets(tripletList.begin(), tripletList.end());
    this->pos_bm1 = this->bm1.cwiseAbs();
    // std::cout<<"this->bm1:\n"<<this->bm1<<std::endl;
    // std::cout<<"this->pos_bm1:\n"<<this->pos_bm1<<std::endl;
}

std::tuple<std::vector<int>, std::vector<int>> PointCloud::ElementSets() const{
    return std::tuple<std::vector<int>, std::vector<int>>(this->Vi, this->Ei);
}

Eigen::SparseMatrix<int> PointCloud::BoundaryMatrices() const{
    return this->bm1;
}

Eigen::SparseMatrix<int> PointCloud::UnsignedBoundaryMatrices() const{
    return this->pos_bm1;
}