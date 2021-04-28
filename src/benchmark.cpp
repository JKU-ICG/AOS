#include <glad/glad.h>
#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>
//#include <stb_image.h>
#define GLM_ENABLE_EXPERIMENTAL
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <glm/gtx/string_cast.hpp>

#include <learnopengl/shader.h>
#include <learnopengl/camera.h>
#include <learnopengl/model.h>
#include <util/window.h>

#include "AOSGenerator.h"
#include "AOS.h"
#include "gl_utils.h"

#include <nlohmann/json.hpp> 

#include <iostream>
#include <algorithm>    // std::min
#include <chrono> // for timings
using std::chrono::high_resolution_clock; // timings
using std::chrono::duration_cast; // timings
using std::chrono::duration; // timings
using std::chrono::milliseconds; // timings

using json = nlohmann::json;

void framebuffer_size_callback(GLFWwindow* window, int width, int height);
void mouse_callback(GLFWwindow* window, double xpos, double ypos);
void mouse_button_callback(GLFWwindow* window, int button, int action, int mods);
void scroll_callback(GLFWwindow* window, double xoffset, double yoffset);
void processInput(GLFWwindow *window);
void boolArrayToIdx(const std::vector<bool>& selected, std::vector<unsigned int>& render_ids);
void idxToBoolArray(const std::vector<unsigned int>& render_ids, std::vector<bool>& selected, unsigned int array_size);
void fillIdx(std::vector<unsigned int>& render_ids, unsigned int array_size);

// settings
int SCR_WIDTH = 512;
int SCR_HEIGHT = 512;
const char APP_NAME[] = "LFR";

// camera
Camera camera(glm::vec3(0.0f, 0.0f, 3.0f));
float lastX = SCR_WIDTH / 2.0;
float lastY = SCR_HEIGHT / 2.0;
bool firstMouse = true;
bool leftButtonDown = false;
bool middleButtonDown = false;
bool rightButtonDown = false;


// timing
float deltaTime = 0.0f;
float lastFrame = 0.0f;


// meshes
unsigned int planeVAO;

// lightfield
AOS *lf;

// current view
int currView = 0;


// fps related variables:
float fpsDelta = 0.0f;
unsigned long fpsNumberOfFrames = 0;
// updates the FPS in the title, every second
void showFPS(GLFWwindow *pWindow)
{
	// Measure speed
	fpsDelta += deltaTime;
	fpsNumberOfFrames++;
	if(fpsDelta >= 1.0) { // If last cout was more than 1 sec ago
		//cout << 1000.0 / double(nbFrames) << endl;

		double fps = double(fpsNumberOfFrames) / fpsDelta;

		std::stringstream ss;
		ss << APP_NAME <<  " [" << fps << " FPS]";

		glfwSetWindowTitle(pWindow, ss.str().c_str());
		fpsDelta = 0;
		fpsNumberOfFrames = 0;
	}
}

int main()
{
    int display_w = 1024, display_h = 1024;


    InitWindow(display_w, display_h, APP_NAME);

    // tell GLFW to capture our mouse
    // glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);


    SetCursorPosCallback(mouse_callback);
    SetMouseButtonCallback(mouse_button_callback);
    SetScrollCallback(scroll_callback);
    SetFramebufferSizeCallback(framebuffer_size_callback);



	int texture_units;
	glGetIntegerv(GL_MAX_TEXTURE_IMAGE_UNITS, &texture_units);
	//std::cout << texture_units << " texture units available!" << std::endl;
	// https://stackoverflow.com/questions/46426331/number-of-texture-units-gl-texturei-in-opengl-4-implementation-in-visual-studi

    auto fov = 43.10803984095769;
    lf = new AOS(SCR_WIDTH, SCR_HEIGHT, fov);
    CHECK_GL_ERROR

    // load the DEM 
    // -----------------------
    // auto dem = Model("../data/dem.obj");
    //auto demTexture = loadImageSTBI("../data/dem.png", true); // tell stb_image.h to flip loaded texture's on the y-axis
    //float demAlpha = .25; // .25;
    lf->loadDEM("../data/dem.obj");
    //lf->loadDEM("D:\\ResilioSync\\ANAOS\\SITES\\Test20210415_Conifer_f1\\LFR\\dem.obj");
	CHECK_GL_ERROR


	// load the light field (matrices, textures, names ...)
	// -----------------------
	AOSGenerator generator;
	generator.Generate( lf, "../data/Hellmonsoedt_pose_corr.json", "../data/Hellmonsoedt_ldr_r512/", true);
    //generator.Generate( lf, "D:\\ResilioSync\\ANAOS\\SITES\\Test20210415_Conifer_f1\\FlightPoses\\CompletePath.json", 
    //    "D:\\ResilioSync\\ANAOS\\SITES\\Test20210415_Conifer_f1\\r512\\");
	// faster, because less images: 	
	//generator.Generate( lf, "../data/Test20201022F1/SimulationPoses/4.json", "../data/Test20201022F1/UndistortedLDRImages/4/");
    CHECK_GL_ERROR


    // store as json
    auto j = json::array();


    for (unsigned int i_dem = 0; i_dem < 3; i_dem++)
    {
        switch (i_dem) {
            case 0: 
                lf->loadDEM("../data/dem_f0.1.obj");
                break;
            case 1:
                lf->loadDEM("../data/dem.obj");
                break;
            case 2:
                lf->loadDEM("../data/dem_f2.obj");
                break;
        }


        // count the vertices in the DEM
        auto dem = lf->getDEM();
        auto num_meshes = dem->meshes.size();
        int num_vertices = 0;
        for (unsigned int i = 0; i < dem->meshes.size(); i++)
            num_vertices += dem->meshes[i].vertices.size();



        // start with full aperture
        std::vector<unsigned int> render_ids;
        for (unsigned int i = 0; i < lf->getSize(); i++)
        {
            render_ids.push_back(i);

            // render once
            // -----------
            {
                const int num_trails = 100;


                auto currView = 1;
                camera.Position = lf->getPosition(currView);
                camera.Front = lf->getForward(currView);
                camera.Up = lf->getUp(currView);

                auto vpose = camera.GetViewMatrix();

                double ms_forward, ms_deferred;
                {
                    // forward
                    auto t1 = high_resolution_clock::now();
                    for (int i = 0; i < num_trails; ++i)
                    {
                        auto img = lf->renderForward(vpose, fov, render_ids);
                    }
                    auto t2 = high_resolution_clock::now();

                    /* Getting number of milliseconds as a double. */
                    duration<double, std::milli> ms_double = t2 - t1;
                    ms_forward = ms_double.count() / num_trails;
                    //std::cout << "forward rendering: " << ms_double.count()/num_trails << "ms" << std::endl ;
                }
                {
                    // deferred
                    auto t1 = high_resolution_clock::now();
                    for (int i = 0; i < num_trails; ++i)
                    {
                        auto img = lf->render(vpose, fov, render_ids);
                    }
                    auto t2 = high_resolution_clock::now();

                    /* Getting number of milliseconds as a double. */
                    duration<double, std::milli> ms_double = t2 - t1;
                    ms_deferred = ms_double.count() / num_trails;
                    //std::cout << "deferred rendering: " << ms_double.count()/num_trails << "ms" << std::endl;
                }
                std::cout << "vertices: " << num_vertices << "; images: " << render_ids.size() << "; forward/deferred rendering: " << ms_forward << " / " << ms_deferred << "ms" << " (x" << ms_forward / ms_deferred << ") " << std::endl;

                // store in json
                j.push_back({ { "vertices", num_vertices}, {"images", render_ids.size()}, {"ms_forward", ms_forward}, {"ms_deferred", ms_deferred}, {"factor", ms_forward / ms_deferred} });
            }
        }
    }

    // write prettified JSON to another file
    std::ofstream o("benchmark.json");
    o << std::setw(4) << j << std::endl;

    // optional: de-allocate all resources once they've outlived their purpose:
    // ------------------------------------------------------------------------
    // -------------------------------------------------------------------------------

    glfwTerminate();
    return 0;
}



// process all input: query GLFW whether relevant keys are pressed/released this frame and react accordingly
// ---------------------------------------------------------------------------------------------------------
void processInput(GLFWwindow *window)
{
    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS)
        glfwSetWindowShouldClose(window, true);
    if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS)
        camera.ProcessKeyboard(FORWARD, deltaTime);
    if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS)
        camera.ProcessKeyboard(BACKWARD, deltaTime);
    if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS)
        camera.ProcessKeyboard(LEFT, deltaTime);
    if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS)
        camera.ProcessKeyboard(RIGHT, deltaTime);
	if (glfwGetKey(window, GLFW_KEY_LEFT) == GLFW_PRESS)
		currView = glm::max( (int)currView - 1, 0);
	if (glfwGetKey(window, GLFW_KEY_RIGHT) == GLFW_PRESS)
		currView = glm::min( currView + 1, (int) lf->getViews()-1 );
}

/// glfw: whenever the window size changed (by OS or user resize) this callback function executes
// ---------------------------------------------------------------------------------------------
void framebuffer_size_callback(GLFWwindow* window, int width, int height)
{
    // make sure the viewport matches the new window dimensions; note that width and 
    // height will be significantly larger than specified on retina displays.
    if (width > 0 && height > 0)
    {
        glViewport(0, 0, width, height);
        SCR_WIDTH = width; SCR_HEIGHT = height;
    }
}


// glfw: whenever the mouse moves, this callback is called
// -------------------------------------------------------
void mouse_callback(GLFWwindow* window, double xpos, double ypos)
{
    if (firstMouse)
    {
        lastX = xpos;
        lastY = ypos;
        firstMouse = false;
    }

    float xoffset = xpos - lastX;
    float yoffset = lastY - ypos; // reversed since y-coordinates go from bottom to top

    lastX = xpos;
    lastY = ypos;

    if (leftButtonDown)
        camera.ProcessMouseMovement(xoffset, yoffset);
}

// glfw: whenever any mouse button is pressed, this callback is called
// ----------------------------------------------------------------------
void mouse_button_callback(GLFWwindow* window, int button, int action, int mods)
{
    if (action == GLFW_PRESS) {
        if (button == GLFW_MOUSE_BUTTON_LEFT)   leftButtonDown = true;
        if (button == GLFW_MOUSE_BUTTON_MIDDLE) middleButtonDown = true;
        if (button == GLFW_MOUSE_BUTTON_RIGHT)  rightButtonDown = true;
    }
    else if (action == GLFW_RELEASE) {
        if (button == GLFW_MOUSE_BUTTON_LEFT)   leftButtonDown = false;
        if (button == GLFW_MOUSE_BUTTON_MIDDLE) middleButtonDown = false;
        if (button == GLFW_MOUSE_BUTTON_RIGHT)  rightButtonDown = false;
    }
}

// glfw: whenever the mouse scroll wheel scrolls, this callback is called
// ----------------------------------------------------------------------
void scroll_callback(GLFWwindow* window, double xoffset, double yoffset)
{
    camera.ProcessMouseScroll(yoffset);
}


void boolArrayToIdx(const std::vector<bool> &selected, std::vector<unsigned int>& render_ids)
{
    render_ids.clear();
    for (unsigned int i = 0; i < selected.size(); i++)
    {
        if(selected[i])
            render_ids.push_back(i);
    }
}


void idxToBoolArray(const std::vector<unsigned int>& render_ids, std::vector<bool>& selected, unsigned int array_size)
{
    selected = std::vector<bool>(array_size);

    std::fill(selected.begin(), selected.end(), false);

    for (auto idx : render_ids)
        selected[idx] = true;
}

void fillIdx(std::vector<unsigned int>& render_ids, unsigned int array_size)
{
    render_ids.clear();
    for (unsigned int i = 0; i < array_size; i++)
    {
        render_ids.push_back(i);
    }
}



/* Look into:
	command line arguments: https://github.com/CLIUtils/CLI11#install 
	OBJ loading: https://github.com/tinyobjloader/tinyobjloader or keep Assimp
	JSON: https://github.com/nlohmann/json#cmake
	Image loading: stb_image does not support TIFF so maybe use FreeImage or SDL

	Try to avoid BOOST (too large and heavy)


*/
