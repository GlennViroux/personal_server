#ifndef ELEVATIONS_H
#define ELEVATIONS_H

#include "string"
#include "iostream"
#include "spacevector.h"

class Elevation
{
private:
    std::string epoch_;
    std::string station_;
    std::string sat_;
    SpaceVector station_pos_;
    SpaceVector sat_pos_;
    double elevation_;

public:
    Elevation(std::string epoch="",std::string station="",std::string sat="",SpaceVector station_pos=SpaceVector(),SpaceVector sat_pos=SpaceVector());

    friend std::ostream& operator<<(std::ostream & os,const Elevation & elev){
        os<<elev.epoch_<<","<<elev.station_<<","<<elev.sat_<<","<<elev.station_pos_<<","<<elev.sat_pos_<<","<<elev.elevation_;
        return os;
    }

    bool calculate_elevation();
};
#endif