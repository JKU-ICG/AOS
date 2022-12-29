
#include <glad/glad.h> // holds all OpenGL type declarations
#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>

#include <string>
#include <iostream>
#include "image.h"
#include "utils.h"
#include <stdio.h>
// utility function to instantiate a GLFW3 window
// ---------------------------------------------------
GLFWwindow* InitGlfwWindow(const int width, const int height, const char* appname = "OpenGL")
{
    // glfw: initialize and configure
    // ------------------------------
    glfwInit();

    glfwWindowHint(GLFW_CLIENT_API, GLFW_OPENGL_ES_API);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 1);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_SAMPLES, 4);
    glfwWindowHint(GLFW_RED_BITS, 8);
    glfwWindowHint(GLFW_GREEN_BITS, 8);
    glfwWindowHint(GLFW_BLUE_BITS, 8);
    glfwWindowHint(GLFW_ALPHA_BITS, 8);
    glfwWindowHint(GLFW_STENCIL_BITS, 8);
    glfwWindowHint(GLFW_DEPTH_BITS, 24);
    glfwWindowHint(GLFW_RESIZABLE, GL_TRUE);

#ifdef __APPLE__
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
#endif

    // glfw window creation
    // --------------------
    GLFWwindow* window = glfwCreateWindow(width, height, appname, NULL, NULL);
    if (window == NULL)
    {
        std::cout << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return nullptr;
    }
    glfwMakeContextCurrent(window);


    // tell GLFW to capture our mouse
    //glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
if (!gladLoadGLES2Loader((GLADloadproc)glfwGetProcAddress))
{
    std::cout << "Failed to initialize GLAD" << std::endl;
    return nullptr;
}
/*
#ifdef OPENGLES2
    // glad: load all OpenGL function pointers
    // ---------------------------------------
    if (!gladLoadGLES2Loader((GLADloadproc)glfwGetProcAddress))
    {
        std::cout << "Failed to initialize GLAD" << std::endl;
        return nullptr;
    }
#else
    
    // glad: load all OpenGL function pointers
    // ---------------------------------------
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress))
    {
        std::cout << "Failed to initialize GLAD" << std::endl;
        return nullptr;
    }
#endif
*/
    return window;
}

// utility function to derminate the window
// ---------------------------------------------------
void DestroyGlfwWindow(GLFWwindow* window)
{
    //if (screen) delete screen;
    if (window)
    {
        glfwTerminate(); //delete window;
    }
    /**
     * WGL and GLX have an unload function to free the module handle.
     * Call the unload function after your last GLX or WGL API call.
     */
    void gladUnloadGLX(void);
    void gladUnloadWGL(void);
}

// Fast copy data from a contiguous byte array into the Image.
void py_copy_image_from_bytes(Image im, char *pdata)
{
    unsigned char *data = (unsigned char*)pdata;
    int i, k, j;
    int w = im.w;
    int h = im.h;
    int c = im.c;
    for (k = 0; k < c; ++k) {
        for (j = 0; j < h; ++j) {
            for (i = 0; i < w; ++i) {
                int dst_index = i + w * j + w * h*k;
                int src_index = k + c * i + c * w*j;
                im.data[dst_index] = (float)data[src_index] / 255.;
            }
        }
    }
}

// Fast copy data from a contiguous byte array into the Image.
void py_copy_image_from_float(Image im, char *pdata)
{
    float *data = (float *)pdata;
    int i, k, j;
    int w = im.w;
    int h = im.h;
    int c = im.c;
    for (k = 0; k < c; ++k) {
        for (j = 0; j < h; ++j) {
            for (i = 0; i < w; ++i) {
                int dst_index = i + w * j + w * h*k;
                int src_index = k + c * i + c * w*j;
                im.data[dst_index] = (float)data[src_index];
            }
        }
    }
}

void py_copy_image_to_float(Image im, float *pdata)
{
    float *data = (float *)pdata;
    int i, k, j;
    int w = im.w;
    int h = im.h;
    int c = im.c;
    for (k = 0; k < c; ++k) {
        for (j = 0; j < h; ++j) {
            for (i = 0; i < w; ++i) {
                int dst_index = i + w * j + w * h*k;
                int src_index = k + c * i + c * w*j;
                int newsrc_index = k + c * j + c * h*i;
                //data[dst_index] = (float)im.data[dst_index];
                data[src_index] = (float)im.data[dst_index];
                //data[src_index] = (float)im.data[src_index];
                //data[dst_index] = (float)im.data[src_index];
                //data[newsrc_index] = (float)im.data[dst_index];
            }
        }
    }
}

Image py_make_image(int w, int h, int c)
{
    Image out = make_empty_image(w,h,c);
    out.data = (float*)xcalloc(h * w * c, sizeof(float));
    return out;
}

void py_free_image(Image m)
{
    if(m.data){
        free(m.data);
    }
}

Image py_float_to_image(int w, int h, int c, float *data)
{
    Image out = make_empty_image(w,h,c);
    out.data = data;
    return out;
}

