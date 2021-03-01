#include "AOS.h"
#include "learnopengl/model.h"
#include "AOS.h"


AOS::AOS(unsigned int width, unsigned int height, int preallocate_images)
{
}

AOS::~AOS()
{
	if (dem_model) {
		delete dem_model;
		dem_model = NULL;
	}
}

void AOS::loadDEM(std::string obj_file)
{
	dem_model = new Model(obj_file);
}

void AOS::addView(Image* img, glm::vec4 pose, std::string name)
{
}

void AOS::getImage(unsigned int idx)
{
	
}

glm::vec4 AOS::getPose(unsigned int idx)
{
	return ogl_imgs[idx].pose;
}

void AOS::removeView(unsigned int idx)
{
}

void AOS::replaceView(unsigned int idx, Image* img, glm::vec4 pose, std::string name)
{
}
