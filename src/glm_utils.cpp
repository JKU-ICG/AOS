#include <glm/glm.hpp>
// #include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>



// Fast copy data from a contiguous byte array into glm::mat4 (a 4x4 array).
glm::mat4 make_mat4_from_float(char* pdata)
{
       return glm::make_mat4((float*)pdata);
}

// Fast copy data from a contiguous byte array into glm::mat4 (a 4x4 array).
glm::vec3 make_vec3_from_float(char* pdata)
{
    return glm::make_vec3((float*)pdata);
}

