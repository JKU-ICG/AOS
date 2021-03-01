#ifndef AOS_H
#define AOS_H

#include <glm/glm.hpp>
#include <string>
#include <vector>

//#include "image.h"

// predeclarations
class Model;

typedef struct {
	int w; // width
	int h; // heigth
	int c; // number of channels
	float* data; // data
} Image;

typedef struct {
	//Image* img;
	glm::vec4 pose;
	unsigned int ogl_id; // opengl texture id
	std::string name;
} View;

// Airborne Optical Sectioning light field renderer:
class AOS
{
private:
	std::vector<View> ogl_imgs;
	unsigned int render_width, render_height;

	Model *dem_model = NULL;

public:
	AOS(unsigned int width, unsigned int height, int preallocate_images = -1);
	~AOS();
	void loadDEM(std::string obj_file);
	void addView(Image* img, glm::vec4 pose, std::string name = "");
	void getImage(unsigned int idx);
	glm::vec4 getPose(unsigned int idx);
	void removeView(unsigned int idx);
	void replaceView(unsigned int idx, Image* img, glm::vec4 pose, std::string name = "");

	Image render(glm::vec4 virtual_pose, std::vector<unsigned int> ids = {}, bool normalize = true);
	Image getXYZ(glm::vec4 virtual_pose);

	void loadViews(std::string json_file, std::string imgs_path = "") {};

private:
	unsigned int getOGLid(unsigned int idx) { return ogl_imgs[idx].ogl_id; }

};


#endif