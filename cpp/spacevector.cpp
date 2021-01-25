#include "math.h"

#include "spacevector.h"

SpaceVector::SpaceVector(double x,double y,double z){
    x_ecef_ = x;
    y_ecef_ = y;
    z_ecef_ = z;  
}

void SpaceVector::set_x(double x){
    x_ecef_ = x; 
}

void SpaceVector::set_y(double y){
    y_ecef_ = y; 
}

void SpaceVector::set_z(double z){
    z_ecef_ = z; 
}

double SpaceVector::get_x(){
    return x_ecef_;
}

double SpaceVector::get_y(){
    return y_ecef_;
}

double SpaceVector::get_z(){
    return z_ecef_;
}

double SpaceVector::get_distance(){
    return sqrt(this->x_ecef_*this->x_ecef_+this->y_ecef_*this->y_ecef_+this->z_ecef_*this->z_ecef_);
}

double SpaceVector::dot_product(const SpaceVector & other){
    return this->x_ecef_*other.x_ecef_+this->y_ecef_*other.y_ecef_+this->z_ecef_*other.z_ecef_;
}