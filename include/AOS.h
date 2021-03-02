#ifndef AOS_H
#define AOS_H

#include "image.h"
#include <glm/glm.hpp>
#include <string>
#include <vector>

//#include "image.h"

// predeclarations
class Model;
class Shader;


typedef struct {
	//Image* img;
	glm::mat4 pose;
	unsigned int ogl_id; // opengl texture id
	std::string name;
} View;

// Airborne Optical Sectioning light field renderer:
class AOS
{
private:
	std::vector<View> ogl_imgs;
	unsigned int render_width, render_height;
	glm::mat4 projection_imgs;
	const float near_plane = 0.1f, far_plane = 1000.0f;
	const float view_aspect = 1.0f; // aspect ratio of views

	// digital elevation model or focal surface
	Model *dem_model = NULL;

	// FBOs
	unsigned int fboIntegral, tIntegral; // fbo and texture for integral
	unsigned int fboGBuffer, gPosition; // fbo and texture for deferred shading
	unsigned int fboCount = 0; glm::vec4 fboMin; glm::vec4 fboMax;
	Image fboImg;

	// shaders
	Shader* showFboShader; // ("../show_fbo.vs.glsl", "../show_fbo.fs.glsl");
	Shader* projectShader; // ("../deferred_project_image.vs.glsl", "../deferred_project_image.fs.glsl");
	Shader* demShader; // ("../project_image.vs.glsl", "../show_fbo.fs.glsl");
	Shader* gBufferShader; // ("../g_buffer.vs.glsl", "../g_buffer.fs.glsl");

public:
	AOS(unsigned int width, unsigned int height, float fovDegree = 50.815436217896945f, int preallocate_images = -1);
	~AOS();
	void loadDEM(std::string obj_file);
	void addView(Image img, glm::mat4 pose, std::string name = "");
	//Image getImage(unsigned int idx);
	glm::mat4 getPose(unsigned int idx) { return ogl_imgs[idx].pose; }
	void removeView(unsigned int idx);
	void replaceView(unsigned int idx, Image img, glm::mat4 pose, std::string name = "");

	Image render(const glm::mat4 virtual_pose, const float virtual_fovDegree, const std::vector<unsigned int> ids = {});
	Image getXYZ(glm::vec4 virtual_pose);
	void display(bool normalize = true);

	//void loadViews(std::string json_file, std::string imgs_path = "") {};
	auto getViews() { return ogl_imgs.size(); }
	auto getSize() { return getViews(); } // legacy

private:
	unsigned int getOGLid(unsigned int idx) { return ogl_imgs[idx].ogl_id; }
	unsigned int generateOGLTexture(Image img);
	void uploadOGLTexture(unsigned int textureID, Image img);
	void deleteOGLTexture(unsigned int textureID);
	void initFrameBufferTexture(unsigned int* fbo, unsigned int* texture);
	static unsigned int getMinMaxFromFBO(glm::vec4* fboData, const unsigned int fboSize, unsigned int& count, glm::vec4& minRGBA, glm::vec4& maxRGBA);
};


#endif