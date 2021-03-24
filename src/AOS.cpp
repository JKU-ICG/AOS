#include <glad/glad.h>
#include "gl_utils.h"
#include "AOS.h"
#include "image.h"
#include "learnopengl/model.h"


void renderQuad();


AOS::AOS(unsigned int width, unsigned int height, float fovDegree, int preallocate_images)
	:render_width(width), render_height(height), dem_model(NULL)
{

	printf("Entering C++ AOS constructor");
	// ToDo: init GL
	// find a way to init GL only if no other OpenGL context exists!

	auto gl_version = glGetString(GL_VERSION);
	if (gl_version == 0)
		printf("ERROR: no Opengl!");
		throw "Error: No OpenGL context!";


	// build and compile shaders
	// -------------------------
	//Shader shader("../3.1.3.shadow_mapping.vs", "../3.1.3.shadow_mapping.fs");
	//Shader simpleDepthShader("../3.1.3.shadow_mapping_depth.vs", "../3.1.3.shadow_mapping_depth.fs");
	showFboShader = new Shader("../shader/show_fbo.vs.glsl", "../shader/show_fbo.fs.glsl");
	projectShader = new Shader("../shader/deferred_project_image.vs.glsl", "../shader/deferred_project_image.fs.glsl");
	demShader = new Shader("../shader/project_image.vs.glsl", "../shader/show_fbo.fs.glsl");
	gBufferShader = new Shader("../shader/g_buffer.vs.glsl", "../shader/g_buffer.fs.glsl");
	CHECK_GL_ERROR

	projection_imgs = glm::perspective(glm::radians(fovDegree), view_aspect, near_plane, far_plane);

	
	// shader configuration
	// --------------------
	projectShader->use();
	projectShader->setInt("gPosition", 0);
	projectShader->setInt("imageTexture", 1);
	showFboShader->use();
	showFboShader->setInt("fboTexture", 0);

	// configure global opengl state
	// -----------------------------
	glDisable(GL_DEPTH_TEST);
	glEnable(GL_BLEND);
	glBlendFunc(GL_ONE, GL_ONE);

	// Setup Framebuffers and Textures
	initFrameBufferTexture(&fboIntegral, &tIntegral);
	initFrameBufferTexture(&fboGBuffer, &gPosition);
	fboImg  = make_image(render_width, render_height, 4); // needed to extract fbo
	gBufImg = make_image(render_width, render_height, 4); // needed to extract fbo

	CHECK_GL_ERROR

	glViewport(0, 0, render_width, render_height);
}

Image AOS::render(const glm::mat4 virtual_pose, const float virtualFovDegrees, const std::vector<unsigned int> ids)
{
	glViewport(0, 0, render_width, render_height);
	gBufferShader->use();
	auto projection = glm::perspective(glm::radians(virtualFovDegrees), (float)render_width / (float)render_height, near_plane, far_plane);
	// set uniforms that do no change
	gBufferShader->setMat4("projection", projection);
	gBufferShader->setMat4("view", virtual_pose);

	// 1. geometry pass: render scene's geometry/color data into gbuffer
	// -----------------------------------------------------------------
	glBindFramebuffer(GL_FRAMEBUFFER, fboGBuffer);
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

	glm::mat4 model = glm::mat4(1.0f);
	gBufferShader->setMat4("model", model);
	dem_model->Draw(*gBufferShader);

	// 2. render scene deferred and project views
	// -----------------------------------------------------------------
	glBindFramebuffer(GL_FRAMEBUFFER, fboIntegral); // enable results framebuffer
	glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT);

	projectShader->use();
	// bind g-Buffer textures
	glActiveTexture(GL_TEXTURE0);
	glBindTexture(GL_TEXTURE_2D, gPosition);

	// if empty create an ids array running from 0 to size
	std::vector<unsigned int> _ids;
	if (ids.empty()) {
		for (unsigned int i = 0; i < ogl_imgs.size(); i++)
			_ids.push_back(i);
	}
	else // otherwise use specified ids!
		_ids= std::vector<unsigned int>(ids);


	for (unsigned int idx : _ids)
	{
		auto projViewMatrix = projection_imgs * ogl_imgs[idx].pose;
		projectShader->setMat4("projViewMatrix", projViewMatrix);
		glActiveTexture(GL_TEXTURE1);
		glBindTexture(GL_TEXTURE_2D, ogl_imgs[idx].ogl_id);
		
		renderQuad(); //render quad
	}



	// read framebuffer to CPU
	glReadBuffer(GL_COLOR_ATTACHMENT0);
	glReadPixels(0, 0, render_width, render_height, GL_RGBA, GL_FLOAT, fboImg.data);
	// to access a single pixel use indexing like (j)width+i, where j is the row
	// calculate minimum and maximum of FBO. Note this is very slow!
	// if it takes too long, do not do this every frame! e.g. only once every second or so
	
	getMinMaxFromFBO((glm::vec4 *)fboImg.data, render_width * render_height, fboCount, fboMin, fboMax);
	//std::cout << "fbo_min: " << glm::to_string(fboMin).c_str() << std::endl;
	//std::cout << "fbo_max: " << glm::to_string(fboMax).c_str() << std::endl;


	glBindFramebuffer(GL_FRAMEBUFFER, 0); // disable framebuffer


	return fboImg;
}

AOS::~AOS()
{
	if (dem_model) {
		delete dem_model;
		dem_model = NULL;
	}
	delete showFboShader;
	delete projectShader;
	delete demShader;
	delete gBufferShader;

	free_image(gBufImg);
	free_image(fboImg);
}

void AOS::loadDEM(std::string obj_file)
{
	if (dem_model)
		delete dem_model;
	dem_model = new Model(obj_file);
}

void AOS::addView(Image img, glm::mat4 pose, std::string name)
{
	View view;
	view.pose = pose;
	view.name = name.empty() ? std::to_string(ogl_imgs.size()) : name;
	view.ogl_id = generateOGLTexture(img);
	ogl_imgs.push_back(view);
}

void AOS::removeView(unsigned int idx)
{
	View v = ogl_imgs[idx];
	deleteOGLTexture(v.ogl_id);
	ogl_imgs.erase(ogl_imgs.begin() + idx);
}

void AOS::replaceView(unsigned int idx, Image img, glm::mat4 pose, std::string name)
{
	View v = ogl_imgs[idx];
	v.pose = pose;
	v.name = name.empty() ? std::to_string(idx) : name;
	uploadOGLTexture(v.ogl_id, img);
	ogl_imgs[idx] = v; // update in vector
}

void AOS::display(bool normalize)
{
	//glViewport(0, 0, render_width, render_height);
	//glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

	// display framebuffer
	// ---------------------------------------------
	showFboShader->use();
	if (normalize && fboCount > 0 && fboMax.a > 0)
	{
		showFboShader->setFloat("fbo_min", fboMin.r);
		showFboShader->setFloat("fbo_max", fboMax.r);
	}
	else
	{
		showFboShader->setFloat("fbo_min", 0.0f);
		showFboShader->setFloat("fbo_max", 1.0f);
	}
	glActiveTexture(GL_TEXTURE0);
	glBindTexture(GL_TEXTURE_2D, tIntegral);
	renderQuad();
}

Image AOS::getXYZ()
{
	glBindFramebuffer(GL_FRAMEBUFFER, fboGBuffer);
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

	// read framebuffer to CPU
	glReadBuffer(GL_COLOR_ATTACHMENT0);
	glReadPixels(0, 0, render_width, render_height, GL_RGBA, GL_FLOAT, gBufImg.data);

	glBindFramebuffer(GL_FRAMEBUFFER, 0);

	return gBufImg;
}

unsigned int AOS::generateOGLTexture(Image img)
{
	unsigned int textureID;
	glGenTextures(1, &textureID);
	uploadOGLTexture(textureID, img);

	return textureID;
}

void AOS::uploadOGLTexture(unsigned int textureID, Image img)
{
	GLenum format, internal;
	if (img.c == 1) {
		internal = GL_R16F;
		format = GL_RED;
	}
	else if (img.c == 3) {
		internal = GL_RGB16F;
		format = GL_RGB;
	}
	else if (img.c == 4) {
		internal = GL_RGBA16F;
		format = GL_RGBA;
	} else
		throw "Error: number of channels not supported!";

	glBindTexture(GL_TEXTURE_2D, textureID);
	glTexImage2D(GL_TEXTURE_2D, 0, internal, img.w, img.h, 0, format, GL_FLOAT, img.data);
	//glGenerateMipmap(GL_TEXTURE_2D); // <- not supported in OpenGL ES!

	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE); // for this tutorial: use GL_CLAMP_TO_EDGE to prevent semi-transparent borders. Due to interpolation it takes texels from next repeat 
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR); // GL_LINEAR_MIPMAP_LINEAR <- not supported in OpenGL ES!
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
}

void AOS::deleteOGLTexture(unsigned int texID)
{
	glActiveTexture(texID);
	glBindTexture(GL_TEXTURE_2D, 0);
	glDeleteTextures(1, &texID);
}

void AOS::initFrameBufferTexture(unsigned int* fbo, unsigned int* texture)
{
	glGenFramebuffers(1, fbo);
	glBindFramebuffer(GL_FRAMEBUFFER, *fbo);
	// position color buffer
	glGenTextures(1, texture);
	glBindTexture(GL_TEXTURE_2D, *texture);
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, render_width, render_height, 0, GL_RGBA, GL_FLOAT, NULL);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
	glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, *texture, 0);
	if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
		std::cout << "Framebuffer not complete!" << std::endl;
		throw "Error: framebuffer not complete!";
	}
	glBindFramebuffer(GL_FRAMEBUFFER, 0);
}


// loop through all pixels of the fbo and compute the minimum/maximum 
unsigned int AOS::getMinMaxFromFBO(glm::vec4* fboData, const unsigned int fboSize, unsigned int& count, glm::vec4& minRGBA, glm::vec4& maxRGBA)
{
	minRGBA.r = minRGBA.g = minRGBA.b = minRGBA.a = numeric_limits<float>::max();
	maxRGBA.r = maxRGBA.g = maxRGBA.b = maxRGBA.a = numeric_limits<float>::min();
	count = 0;

	for (int i = 0; i < fboSize; i++)
	{
		auto px = fboData[i];

		if (px.a > 0)
		{
			px.r /= px.a; px.g /= px.a; px.b /= px.a;
			minRGBA = glm::min(minRGBA, px);
			maxRGBA = glm::max(maxRGBA, px);
			count++;
		}
	}

	return count;

}


// renderQuad() renders a 1x1 XY quad in NDC
// -----------------------------------------
unsigned int quadVAO = 0;
unsigned int quadVBO;
void renderQuad()
{
	if (quadVAO == 0)
	{
		float quadVertices[] = {
			// positions        // texture Coords
			-1.0f,  1.0f, 0.0f, 0.0f, 1.0f,
			-1.0f, -1.0f, 0.0f, 0.0f, 0.0f,
			 1.0f,  1.0f, 0.0f, 1.0f, 1.0f,
			 1.0f, -1.0f, 0.0f, 1.0f, 0.0f,
		};
		// setup plane VAO
		glGenVertexArrays(1, &quadVAO);
		glGenBuffers(1, &quadVBO);
		glBindVertexArray(quadVAO);
		glBindBuffer(GL_ARRAY_BUFFER, quadVBO);
		glBufferData(GL_ARRAY_BUFFER, sizeof(quadVertices), &quadVertices, GL_STATIC_DRAW);
		glEnableVertexAttribArray(0);
		glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)0);
		glEnableVertexAttribArray(1);
		glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)(3 * sizeof(float)));
	}
	glBindVertexArray(quadVAO);
	glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
	glBindVertexArray(0);
}
