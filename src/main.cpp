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

#include <iostream>
#include <algorithm>    // std::min
#include <chrono> // for timings

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
    int display_w = SCR_WIDTH, display_h = SCR_HEIGHT;


    InitWindowAndGUI(display_w, display_h, APP_NAME);

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

    lf = new AOS(SCR_WIDTH, SCR_HEIGHT);
	CHECK_GL_ERROR

	// load the DEM 
	// -----------------------
	//auto dem = Model("../data/dem.obj");
	//auto demTexture = loadImageSTBI("../data/dem.png", true); // tell stb_image.h to flip loaded texture's on the y-axis
	//float demAlpha = .25; // .25;
    lf->loadDEM("../data/dem.obj");
	CHECK_GL_ERROR


	// load the light field (matrices, textures, names ...)
	// -----------------------
	AOSGenerator generator;
	//generator.Generate( lf, "../data/Hellmonsoedt_pose_corr.json", "../data/Hellmonsoedt_ldr_r512/");
	// faster, because less images: 	
	generator.Generate( lf, "../data/Hellmonsoedt_pose_corr_30.json", "../data/Hellmonsoedt_ldr_r512/");
	CHECK_GL_ERROR



 

    // start with full aperture
    std::vector<unsigned int> render_ids;
    for (unsigned int i = 0; i < lf->getSize(); i++)
            render_ids.push_back(i);

    // render loop
    // -----------
    while (!glfwWindowShouldClose(window))
    {
        auto start_loop = std::chrono::steady_clock::now();
        // per-frame time logic
        // --------------------
        float currentFrame = glfwGetTime();
        deltaTime = currentFrame - lastFrame;
        lastFrame = currentFrame;
		showFPS(window);

        // input
        // -----
        processInput(window);
        // GUI
        // ---------------------------------------------------
        if (gui) {
            // Start the Dear ImGui frame
            ImGui_ImplOpenGL3_NewFrame();
            ImGui_ImplGlfw_NewFrame();
            ImGui::NewFrame();

            // some settings
            static bool pinholeActive = false;

            // 2. Show a simple window that we create ourselves. We use a Begin/End pair to created a named window.
            {   char buffer[512];
                sprintf_s(buffer, 512, "%s (fps: %.1f)", APP_NAME, ImGui::GetIO().Framerate);
                ImGui::Begin(APP_NAME);
                ImGui::Text("FPS: %.1f", ImGui::GetIO().Framerate);
                //ImGui::SliderFloat("gamma", &gamma, 0.1f, 5.0f);   // Edit 1 float using a slider from 0.0f to 1.0f

                if (ImGui::TreeNode("Virtual Camera"))
                {
                    ImGui::InputFloat3("Position", &(camera.Position.x));
                    ImGui::InputFloat3("Forward", &(camera.Front.x));
                    ImGui::InputFloat3("Up", &(camera.Up.x));
                    auto fovRad = glm::radians(camera.Zoom);
                    ImGui::SliderAngle("FOV", &fovRad, 1, 180);
                    camera.Zoom = glm::degrees(fovRad);
                    
                    auto prevView = currView;
                    ImGui::InputInt("Jump to", &currView);
                    if (prevView != currView) {
                        if (currView < 0) currView = 0;
                        if (currView >= lf->getSize()) currView = lf->getSize() - 1;
                        // jump to view!
                        camera.Position = lf->getPosition(currView);
                        camera.Front = lf->getForward(currView);
                        camera.Up = lf->getUp(currView);
                        camera.updateYawPitch();
                    }


                    
                    ImGui::TreePop();
                }
                
                if (ImGui::TreeNode("Views"))
                {
                    ImGui::Text("aperture: ");  ImGui::SameLine(); 
                    sprintf_s(buffer, 512, "[%c] pinhole", pinholeActive ? 'x' : ' ');
                    if (ImGui::Button(buffer))
                        pinholeActive = !pinholeActive;
                        
                    // keep current view as pinhole
                    if (pinholeActive) {
                        render_ids.clear();
                        render_ids.push_back(currView);
                    }
                    
                    ImGui::SameLine(); 
                    if (ImGui::Button("open")) {
                        pinholeActive = false;
                        fillIdx(render_ids, lf->getSize());
                    }
                    std::vector<bool> selected;
                    idxToBoolArray(render_ids, selected, lf->getSize());
                    ImGui::BeginChild("Views scrolling");
                    for (int n = 0; n < lf->getSize(); n++) {
                        sprintf_s( buffer, 512, "[%c] %04d: %s ", selected[n]?'x':' ', n, lf->getName(n).c_str() );
                        bool sel = selected[n];
                        ImGui::Selectable(buffer, &sel );
                        selected[n] = sel;
                    }
                    ImGui::EndChild();
                    ImGui::TreePop();
                    boolArrayToIdx(selected, render_ids);
                }              

                ImGui::End();
            }

            ImGui::Render();
        }

        // LFR Render
        // ----------
        lf->render(camera.GetViewMatrix(), camera.Zoom, render_ids);

        // ----- render results
        int display_w, display_h;
        glfwGetFramebufferSize(window, &display_w, &display_h);
        glViewport(0, 0, display_w, display_h);
        glClearColor(0.0, 0.0, 0.0, 0.0);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );
        lf->display();

        // glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
        // -------------------------------------------------------------------------------
        if (gui) ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
        glfwSwapBuffers(window);
        glfwPollEvents();

        // TIMINGs
        auto end_loop = std::chrono::steady_clock::now();
        std::chrono::duration<double> duration_loop = end_loop - start_loop; // duration
        // printf("TIMINGS (sec) - entire loop %.6f\n", duration_loop.count() );
    }

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
