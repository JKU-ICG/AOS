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
#include <iostream>
#include <string>

#include <CLI/CLI.hpp> // for argument parsing

void framebuffer_size_callback(GLFWwindow* window, int width, int height);
void mouse_callback(GLFWwindow* window, double xpos, double ypos);
void mouse_button_callback(GLFWwindow* window, int button, int action, int mods);
void scroll_callback(GLFWwindow* window, double xoffset, double yoffset);
void processInput(GLFWwindow *window);
void boolArrayToIdx(const std::vector<bool>& selected, std::vector<unsigned int>& render_ids);
void idxToBoolArray(const std::vector<unsigned int>& render_ids, std::vector<bool>& selected, unsigned int array_size);
void fillIdx(std::vector<unsigned int>& render_ids, unsigned int array_size);

// settings
int SCR_WIDTH = 1024;
int SCR_HEIGHT = 1024;
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
        int w,h;
        glfwGetWindowSize(pWindow, &w, &h);
		ss << APP_NAME <<  " [" << fps << " FPS; " << w << "x" << h << "]";
		glfwSetWindowTitle(pWindow, ss.str().c_str());
		fpsDelta = 0;
		fpsNumberOfFrames = 0;
	}
}

// from: https://github.com/ocornut/imgui/blob/master/imgui_demo.cpp
// Helper to display a little (?) mark which shows a tooltip when hovered.
// In your own code you may want to display an actual icon if you are using a merged icon fonts (see docs/FONTS.md)
static void HelpMarker(const char* desc)
{
    ImGui::TextDisabled("(?)");
    if (ImGui::IsItemHovered())
    {
        ImGui::BeginTooltip();
        ImGui::PushTextWrapPos(ImGui::GetFontSize() * 35.0f);
        ImGui::TextUnformatted(desc);
        ImGui::PopTextWrapPos();
        ImGui::EndTooltip();
    }
}

int main(int argc, char** argv) 
{
    
    // Options (&defaults):
    std::string demFile = "../data/zero_plane.obj";
    float fovDegree = 43.10803984095769F; // degrees
    std::string posesFile = "../data/F0/poses/poses_first30.json";
    std::string imgFolder = "../data/F0/images_ldr/";
    std::string maskImage = "";
    float demTranslationZ = 0.0f;
    bool tmp_replaceTiff = false;
    bool normalize = false; bool colormap = false;
    glm::vec<3, int> colormapRGB({ 7, 5, 15 }); // typical values are here: https://github.com/kbinani/colormap-shaders#gnuplot

    // Command line parsing
    CLI::App app{ APP_NAME };
    app.add_option("--fov",  fovDegree, "Field of view of the cameras in degrees.");
    app.add_option("--dem",  demFile, "The path to the digital elevation model (DEM).");
    app.add_option("--pose", posesFile, "The path to the poses in a json format.");
    app.add_option("--img",  imgFolder, "The path to the images in POSES.");
    app.add_option("-r,--replaceTiff",  tmp_replaceTiff, "Replace .tiff with .png in the POSES file.");
    app.add_option("-z,--ztranslDEM",  demTranslationZ, "Translate the DEM on the z axis.");
    app.add_option("-v,--view",  currView, "view index for startup");
    app.add_option("--mask", maskImage, "The path to the alpha mask image.");
    CLI11_PARSE(app, argc, argv);

    bool replaceTiff = tmp_replaceTiff || (0==imgFolder.compare("../data/F0/images_ldr/")); // this makes sure that replaceTiff is true with the F0 ldr scene


    std::cout << "Settings " << std::endl;
    std::cout << "  field of view: " << fovDegree << " (degrees) " << std::endl;
    std::cout << "  digital elevation model file: " << demFile << " " << std::endl;
    std::cout << "  pose file: " << posesFile << " " << std::endl;
    std::cout << "  image folder: " << imgFolder << " " << std::endl;
    if(maskImage.size()>0) 
        std::cout << "  mask image: " << maskImage << " " << std::endl;
    std::cout << "  replace tiff: " << (replaceTiff ? "yes" : "no") << " " << std::endl;
    std::cout << "  z translation of the DEM: " << demTranslationZ << " " << std::endl;
    std::cout << "  startup view: " << currView << " " << std::endl;






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
	std::cout << texture_units << " texture units available!" << std::endl;
	// https://stackoverflow.com/questions/46426331/number-of-texture-units-gl-texturei-in-opengl-4-implementation-in-visual-studi

    lf = new AOS(SCR_WIDTH, SCR_HEIGHT, fovDegree); 
    CHECK_GL_ERROR

    // load the DEM 
    // -----------------------
    // auto dem = Model("../data/dem.obj");
    //auto demTexture = loadImageSTBI("../data/dem.png", true); // tell stb_image.h to flip loaded texture's on the y-axis
    //float demAlpha = .25; // .25;
    //lf->loadDEM("../data/F0/DEM/dem.obj");
    lf->loadDEM(demFile);
    //lf->loadDEM("D:\\ResilioSync\\ANAOS\\SITES\\Test20210415_Conifer_f1\\LFR\\dem.obj");
	CHECK_GL_ERROR
    std::cout << "DEM loaded!" << std::endl;


	// load the light field (matrices, textures, names ...)
	// -----------------------
	AOSGenerator generator;
    generator.Generate(lf, posesFile, imgFolder, maskImage, replaceTiff);
	CHECK_GL_ERROR
    std::cout << "LF with " << lf->getViews() << " views loaded!" << std::endl;



 

    // start with full aperture
    std::vector<unsigned int> render_ids;
    for (unsigned int i = 0; i < lf->getSize(); i++)
            render_ids.push_back(i);


    // set the startup view
    camera.Position = lf->getPosition(currView);
    camera.Front = lf->getForward(currView);
    camera.Up = lf->getUp(currView);
    
    // set startup DEM transformation
    lf->setDEMTransformation( glm::vec3(0,0,demTranslationZ), glm::vec3(0) );

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
                static bool open_window = true;
                ImGui::Begin(APP_NAME, &open_window, ImGuiWindowFlags_NoBackground );
                ImGui::Text("FPS: %.1f", ImGui::GetIO().Framerate);
                //ImGui::SliderFloat("gamma", &gamma, 0.1f, 5.0f);   // Edit 1 float using a slider from 0.0f to 1.0f

                if (ImGui::TreeNode("Display"))
                {
                    ImGui::Checkbox("normalize", &normalize);
                    ImGui::SameLine(); HelpMarker("Normalize image based on min/max in view. Not useful for color images. Brighntess will change when the camera moves, if enabled. ");
                    ImGui::Checkbox("use colormap", &colormap);
                    ImGui::SameLine(); HelpMarker("Display grayscale image (or the red channel) with gnuplot's rgbformulae.");
                    if (colormap)
                    {
                        ImGui::InputInt3("RGB formula", &colormapRGB.r);
                    }

                    ImGui::TreePop();
                }

                if (ImGui::TreeNode("Virtual Camera"))
                {
                    ImGui::InputFloat3("Position", &(camera.Position.x));
                    ImGui::InputFloat3("Forward", &(camera.Front.x));
                    ImGui::InputFloat3("Up", &(camera.Up.x));
                    auto fovRad = glm::radians(camera.Zoom);
                    ImGui::SliderAngle("FOV", &fovRad, 1, 180);
                    camera.Zoom = glm::degrees(fovRad);
                    float nfp[] = { lf->getNearPlane(), lf->getFarPlane() };
                    ImGui::InputFloat2("Near/Far Plane", nfp);
                    lf->setNearPlane(nfp[0]); lf->setFarPlane(nfp[1]);


                    
                    auto prevView = currView;
                    ImGui::InputInt("Jump to", &currView);
                    if (prevView != currView) {
                        if (currView < 0) currView = 0;
                        if (currView >= lf->getSize()) currView = lf->getSize() - 1;
                        // jump to view!
                        camera.Position = lf->getPosition(currView);
                        camera.Front = lf->getForward(currView);
                        camera.Up = lf->getUp(currView);
                        //camera.updateYawPitch();
                    }
                    sprintf_s(buffer, 512, "[%c] pinhole", pinholeActive ? 'x' : ' ');
                    if (ImGui::Button(buffer))
                        pinholeActive = !pinholeActive;
                    ImGui::SameLine();
                    if (ImGui::Button("open")) {
                        pinholeActive = false;
                        fillIdx(render_ids, lf->getSize());
                    }
                    ImGui::SameLine();  ImGui::Text("aperture");


                    
                    ImGui::TreePop();
                }
                // keep current view as pinhole
                if (pinholeActive) {
                    render_ids.clear();
                    render_ids.push_back(currView);
                }
                
                if (ImGui::TreeNode("Single Images"))
                {
                    std::vector<bool> selected;
                    idxToBoolArray(render_ids, selected, lf->getSize());
                    ImGui::BeginChild("Views scrolling", ImVec2(0,-200)); // begin scrolling
                    for (int n = 0; n < lf->getSize(); n++) {
                        sprintf_s( buffer, 512, "[%c] %04d: %s ", selected[n]?'X':' ', n, lf->getName(n).c_str() );
                        bool sel = selected[n];
                        ImGui::Selectable(buffer, &sel );
                        selected[n] = sel;
                    }
                    ImGui::EndChild(); // end scrolling
                    if (ImGui::TreeNode("Corrections"))
                    {
                        static auto translate = glm::vec3(0);
                        static auto rotate = glm::vec3(0);
                        /*static auto correct_all = true;
                        static auto correct_id = currView;

                        ImGui::Text("affect"); ImGui::SameLine();
                        ImGui::Checkbox("all images ", &correct_all);
                        if(!correct_all){
                            ImGui::SameLine();
                            ImGui::InputInt("single image", &correct_id);
                        }*/
                        ImGui::SliderFloat3("Translation", &(translate.x),-10,10);
                        ImGui::SliderFloat3("Rotation", &(rotate.x), -180, 180, "%.1f (deg)" );

                        if (ImGui::Button("reset")) {
                            translate = glm::vec3(0);
                            rotate = glm::vec3(0);
                        }

                        // update correction matrizes
                        for (unsigned int i = 0; i < lf->getSize(); i++)
                            lf->setPoseCorrection( i, translate,  glm::radians(rotate) );


                        ImGui::TreePop();
                    }

                    ImGui::TreePop();
                    boolArrayToIdx(selected, render_ids);
                }   

                if (ImGui::TreeNode("DEM"))
                {
                    static auto dem_translate = glm::vec3(0,0,demTranslationZ);
                    static auto dem_rotate = glm::vec3(0);
                    auto dem = lf->getDEM();
                    auto num_meshes = dem->meshes.size();
                    int num_vertices = 0;
                    for (unsigned int i = 0; i < dem->meshes.size(); i++)
                        num_vertices += dem->meshes[i].vertices.size();
                    sprintf_s(buffer, 512, "%s (%d meshes with %d vertices)", "DEM", num_meshes, num_vertices );
                    ImGui::Text(buffer);
                    ImGui::SliderFloat2("Translation (x,y)", &(dem_translate.x),-100,100);
                    { // same line
                        ImGui::InputFloat("##demz", &(dem_translate.z)); 
                        ImGui::SameLine();
                        if (ImGui::Button("-")) { dem_translate.z -= 1; }
                        ImGui::SameLine();
                        if (ImGui::Button("+")) { dem_translate.z += 1; }
                        ImGui::SameLine();  ImGui::Text("(z)");
                    }
                    ImGui::SliderFloat3("Rotation", &(dem_rotate.x), -180, 180, "%.1f (deg)" );
                    if (ImGui::Button("reset")) {
                        dem_translate = glm::vec3(0, 0, demTranslationZ);
                        dem_rotate = glm::vec3(0);
                    }

                    lf->setDEMTransformation(dem_translate, glm::radians(dem_rotate) );

                    ImGui::TreePop();
                }

                ImGui::End();
            }

            ImGui::Render();
        }

        // LFR Render
        // ----------
        //lf->renderForward(camera.GetViewMatrix(), camera.Zoom, render_ids); // forward rendering

        lf->render(camera.GetViewMatrix(), camera.Zoom, render_ids); // deferred rendering

        // ----- render results
        int display_w, display_h;
        glfwGetFramebufferSize(window, &display_w, &display_h);
        glViewport(0, 0, display_w, display_h);
        glClearColor(0.0, 0.0, 0.0, 0.0);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );
        lf->display(normalize, false, false, colormap, colormapRGB);

        UpdateWindow();

        // TIMINGs
        auto end_loop = std::chrono::steady_clock::now();
        std::chrono::duration<double> duration_loop = end_loop - start_loop; // duration
        // printf("TIMINGS (sec) - entire loop %.6f\n", duration_loop.count() );
    }

    // optional: de-allocate all resources once they've outlived their purpose:
    // ------------------------------------------------------------------------
    // -------------------------------------------------------------------------------

    DestroyWindow();
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

