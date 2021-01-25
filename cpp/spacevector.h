#ifndef SPACEVECTOR_H
#define SPACEVECTOR_H

#include "iostream"

class SpaceVector
{
private:
    double x_ecef_;
    double y_ecef_;
    double z_ecef_;

public:
    SpaceVector(double x = 0,double y = 0,double z = 0);

    void set_x(double x);
    void set_y(double y);
    void set_z(double z);
    double get_x();
    double get_y();
    double get_z();

    double get_distance();
    double dot_product(const SpaceVector & other);

    friend std::ostream& operator<<(std::ostream & os,const SpaceVector & vect){
        os<<vect.x_ecef_<<","<<vect.y_ecef_<<","<<vect.z_ecef_;
        return os;
    }

    SpaceVector operator+(const SpaceVector & vect){
        SpaceVector result;
        result.x_ecef_ = this->x_ecef_+vect.x_ecef_;
        result.y_ecef_ = this->y_ecef_+vect.y_ecef_;
        result.z_ecef_ = this->z_ecef_+vect.z_ecef_;
        return result;
    }

    SpaceVector operator-(const SpaceVector & vect){
        SpaceVector result;
        result.x_ecef_ = this->x_ecef_-vect.x_ecef_;
        result.y_ecef_ = this->y_ecef_-vect.y_ecef_;
        result.z_ecef_ = this->z_ecef_-vect.z_ecef_;
        return result;
    }

    SpaceVector operator/(const double & d){
        SpaceVector result = SpaceVector(this->x_ecef_/d,this->y_ecef_/d,this->z_ecef_/d);
        return result;
    }


};

#endif