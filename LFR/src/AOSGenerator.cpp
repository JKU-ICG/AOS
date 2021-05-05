
#include <glad/glad.h> // <-- try to get rid of it here!
#include "image.h"
#include "AOSGenerator.h"
#include "AOS.h"
#include "image.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <string>
#include <nlohmann/json.hpp> 
#include <glm/glm.hpp>
#include <glm/gtc/type_ptr.hpp>
//#include <FreeImage.h>

using namespace nlohmann; // for parsing JSON files


#define _USE_MATH_DEFINES
#include <cmath>

AOSGenerator::AOSGenerator(void)
{
}

AOSGenerator::~AOSGenerator(void)
{
}

glm::mat4 ParseMatrix(json::value_type jMat) // Matrice 3x4
{
	double data[16] = { 1,0,0,0,
						0,1,0,0,
						0,0,1,0,
						0,0,0,1 };
	assert(jMat.size() == 3);


	for (int ir = 0; ir < jMat.size(); ir++)
	{
		assert(jMat[ir].size() == 4);
		for (int ic = 0; ic < jMat[ir].size(); ic++)
		{
			if (jMat[ir][ic].is_string())
			{
				auto v = jMat[ir][ic].get<std::string>();
				data[ic * 4 + ir] = stod(v);
			}
			else if (jMat[ir][ic].is_number())
			{
				data[ic * 4 + ir] = jMat[ir][ic];
			}
			else
			{
				throw "unknown data type in matrix!";
			}
		}

	}


	return glm::make_mat4(data);

}

void AOSGenerator::Generate(AOS* aos, const std::string& jsonPoseFile, const std::string& imgFilePath, bool replaceExt)
{
	std::ifstream poseStream(jsonPoseFile);
	json j;
	poseStream >> j; // parse json
	poseStream.close();

	//std::cout << "images size: " << j["images"].size() << std::endl;
	if (j["images"].size() > 0)
	{
		//lf = new Lightfield(j["images"].size());
		auto jimg = j["images"];
		for (auto i = 0; i < jimg.size(); ++i) {
			auto m = ParseMatrix(jimg[i]["M3x4"]);

			std::string fname = (jimg[i]["imagefile"]);
			auto pose = m;

			std::string name = fname;
			if(replaceExt) name.replace(fname.find(".tiff"), strlen(".tiff"), ".png");
			Image img = load_image( (imgFilePath + "/" + name).c_str() );
			if( !is_empty_image(img) )
				aos->addView(img, pose, name);
			free_image(img);

			// DEBUG
			// std::cout << "imgfilename: " << jimg[i]["imagefile"] << std::endl;
			// std::cout << "matrix: " << jimg[i]["M3x4"] << std::endl;
			// auto translation = glm::vec3(glm::inverse(m)[3]);
			// std::cout << "translation: " << translation.x << ", " << translation.y << ", " << translation.z << "\n";
		}

	}

}
