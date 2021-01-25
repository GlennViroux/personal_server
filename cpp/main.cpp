#include <fstream>
#include <iostream>
#include <vector>
#include <string>
#include <map>

#include "spacevector.h"
#include "elevations.h"

bool write_csv(
    const std::string &filename,
    const std::map<std::string, std::vector<std::string>> &values,
    std::string &error_msg)
{
    std::ofstream myFile(filename);

    //Check data
    auto it = values.begin();
    double data_size = it->second.size();
    for (auto const &p : values)
    {
        if (data_size != p.second.size())
        {
            error_msg = "Error writing CSV file: all vectors should be of equal length";
            return false;
        }
    }

    std::vector<std::string> columns;
    std::vector<std::vector<std::string>> data;

    for (auto p : values)
    {
        columns.push_back(p.first);
        for (unsigned int i = 0; i < p.second.size(); i++)
        {
            if (data.size() <= i)
            {
                std::vector<std::string> new_vect;
                data.push_back(new_vect);
            }
            data[i].push_back(p.second[i]);
        }
    }

    for (unsigned int i = 0; i < columns.size(); i++)
    {
        if (i != columns.size() - 1)
        {
            myFile << columns[i] << ",";
        }
        else
        {
            myFile << columns[i];
        }
    }
    myFile << "\n";

    for (auto row : data)
    {
        for (unsigned int i = 0; i < row.size(); i++)
        {
            if (i != row.size() - 1)
            {
                myFile << row[i] << ",";
            }
            else
            {
                myFile << row[i];
            }
        }
        myFile << "\n";
    }

    myFile.close();
    return true;
}

bool write_csv(
    const std::string & filename,
    const std::vector<Elevation> & data)
{
    std::ofstream myFile(filename);
    myFile << "epoch,station,sat,x_stat,y_stat,z_stat,x_sat,y_sat,z_sat,elev\n";

    for (auto const value:data){
        myFile << value << "\n";
    }

    return true;

}


bool read_csv(
    const std::string filename,
    std::vector<Elevation> &data)
{
    std::ifstream myFile(filename);
    if (!myFile.is_open())
        throw std::runtime_error("Could not open file: " + filename);

    if (!myFile.good())
        throw std::runtime_error("File " + filename + " is not good");

    std::string line;
    std::string delimiter = ",";
    size_t pos = 0;
    unsigned int count = 0;
    std::string token;

    std::string epoch,station,sat;
    SpaceVector station_pos,sat_pos;
    double x_stat,y_stat,z_stat,x_sat,y_sat,z_sat;
    std::getline(myFile, line);

    while (std::getline(myFile, line))
    {
        pos = 0;
        count = 0;
        while ((pos = line.find(delimiter)) != std::string::npos)
        {
            count++;
            token = line.substr(0, pos);
            line.erase(0, pos + delimiter.length());

            if (count==1){
                epoch = token;
            } else if (count==2){
                station = token;
            } else if (count==3){
                sat = token;
            } else if (count==4){
                x_stat = std::stod(token);
            } else if (count==5){
                y_stat = std::stod(token);
            } else if (count==6){
                z_stat = std::stod(token);
            } else if (count==7){
                x_sat = std::stod(token);
            } else if (count==8){
                y_sat = std::stod(token);
            } 
        }
        z_sat = std::stod(line);
        station_pos.set_x(x_stat);
        station_pos.set_y(y_stat);
        station_pos.set_z(z_stat);
        sat_pos.set_x(x_sat);
        sat_pos.set_y(y_sat);
        sat_pos.set_z(z_sat);

        Elevation new_elevation = Elevation(epoch,station,sat,station_pos,sat_pos);
        new_elevation.calculate_elevation();
        data.push_back(new_elevation);
    }

    return true;
}

int main(int argc, char** argv)
{

    if (argc!=3){
        std::cout<<"Usage: ./main input_file output_file\n";
        return 0;
    }

    std::string filename = argv[1];
    std::string output = argv[2];
    std::vector<Elevation> data;
    read_csv(filename, data);
    write_csv(output,data);
}