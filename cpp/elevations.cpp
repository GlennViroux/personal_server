#include <string>
#include "math.h"

#include "elevations.h"

#define EARTH_FLATTE_GRS80 1.0/298.257222101
#define PI 3.14159265

Elevation::Elevation(std::string epoch,std::string station,std::string sat,SpaceVector station_pos,SpaceVector sat_pos)
{
    epoch_ = epoch;
    station_ = station;
    sat_ = sat;
    station_pos_ = station_pos;
    sat_pos_ = sat_pos;
};

bool Elevation::calculate_elevation()
{
    SpaceVector station_to_sat = sat_pos_ - station_pos_;
    double distance = station_to_sat.get_distance();

    if (distance<1e-10){
        elevation_ = 0;
        return true;
    }
    SpaceVector station_normal = station_pos_;
    double new_z = station_normal.get_z()/((1.0 - EARTH_FLATTE_GRS80) * (1.0 - EARTH_FLATTE_GRS80));
    station_normal.set_z(new_z);
    double aux_distance = station_normal.get_distance();
    SpaceVector station_normal_unit = station_normal/aux_distance;
    double aux = station_to_sat.dot_product(station_normal_unit);
    
    double sinE = aux/distance;
    elevation_ = asin(sinE) * 180 / PI;
    return true;

}