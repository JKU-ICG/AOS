
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

void AOSGenerator::Generate(AOS* aos, const std::string& jsonPoseFile, const std::string& imgFilePath, const std::string& maskFile, bool replaceExt)
{
	std::ifstream poseStream(jsonPoseFile);
	if ( poseStream.fail() )
	{
		char buffer[1024]; strerror_s(buffer, sizeof(buffer), errno);
		std::cout << "Could not read " << jsonPoseFile << std::endl;
		std::cout << "Error: " << buffer << std::endl;
	}
	json j;
	poseStream >> j; // parse json
	poseStream.close();

	Image alpha = make_empty_image();


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
			if(replaceExt) name.replace(fname.find(".tiff"), strlen(".tiff"), ".png"); // this is a hack: if images are png images but they are named *.tiff in the poses file!
			Image img = load_image( (imgFilePath + "/" + name).c_str(), 0, 0, 3 ); // make sure to load 3 channels!
			if (!is_empty_image(img))
			{
				if (is_empty_image(alpha)) // lazy init the mask image
				{
					if (maskFile.size() > 0)
						alpha = load_image(maskFile.c_str(), 0, 0, 1); // load a single-channel alpha image 
					
					if (is_empty_image(alpha))
					{
						alpha = make_uniform_image(img.w, img.h, 1, 1.0f); // all ones image
						std::cout << "Could not read mask image: " << maskFile << std::endl;
					}
				}
				Image imgs[] = { img,alpha };
				Image tmp = merge_images_channels( imgs, 2);
				aos->addView(tmp, pose, name);
				free_image(tmp);
			}
			free_image(img);

#ifdef DEBUG_OUTPUT
			// DEBUG
			std::cout << "---------------------------------" << std::endl;
			std::cout << ">> AOSGenerator::Generate << " << std::endl;
			std::cout << "imgfilename: " << jimg[i]["imagefile"] << std::endl;
			std::cout << "JSON-matrix: " << jimg[i]["M3x4"] << std::endl;
			//std::cout << "matrix(parsed): " << glm::to_string(pose) << std::endl;
			auto translation = glm::vec3(glm::inverse(m)[3]);
			std::cout << "position: " << glm::to_string(translation) << "\n";
			std::cout << "pose-matrix: " << glm::to_string(aos->getPose(aos->getViews() - 1)) << std::endl;
			std::cout << "---------------------------------" << std::endl;
#endif
		}

	}

	free_image(alpha);

}
