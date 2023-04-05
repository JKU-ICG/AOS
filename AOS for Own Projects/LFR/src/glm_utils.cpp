#include <glm/glm.hpp>
// #include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#define GLM_ENABLE_EXPERIMENTAL
#include <glm/gtx/string_cast.hpp>
#include <stdio.h>
#include <iostream>

// Fast copy data from a contiguous byte array into glm::mat4 (a 4x4 array).
glm::mat4 make_mat4_from_float(char* pdata)
{
    glm::mat4 convertedmat = glm::make_mat4((float*)pdata);
    //std::cout << "pose data converted from character array " << glm::to_string(convertedmat).c_str() << std::endl;
    return glm::make_mat4((float*)pdata);
}

// Fast copy data from a contiguous byte array into glm::mat4 (a 4x4 array).
glm::vec3 make_vec3_from_float(char* pdata)
{
    return glm::make_vec3((float*)pdata);
}

glm::mat4 make_mat4_from_floatarr(float* pdata)
{

    auto glmMat = glm::mat4( 1.0 );
    glmMat = glm::transpose(glm::make_mat4(pdata)); //glm::transpose
    //glm::mat4 convertedmat = glm::make_mat4((float*)pdata);
    //std::cout << "pose data converted from float array " << glm::to_string(glmMat).c_str() << std::endl;
    return glmMat;
    //return glm::make_mat4((float*)pdata);
}

void get_float_ptr_mat(glm::mat4* m, float* farray)
{
    float *farray2 = glm::value_ptr(*m);
    //std::cout << "size  " << sizeof(farray2) << std::endl;
    for (int i = 0; i <=16; i++) {
        farray[i] = farray2[i];
        //std::cout << "farray2[i] " << farray2[i] << std::endl;
    }
    //return &((*m)[0][0]); // adress of float with index 0
}


void get_float_ptr_vec(glm::vec3* v, float* farray)
{
    float *farray2 = glm::value_ptr(*v);
    for (int i = 0; i <=3; i++) {
        farray[i] = farray2[i];
        //std::cout << "farray2[i] " << farray2[i] << std::endl;
    }
    //return &(v->x); // adress of float with index 0
}



