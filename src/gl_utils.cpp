#include "gl_utils.h"

void check_gl_error_and_print()
{
	GLenum error = glGetError();
	if (error != GL_NO_ERROR)
		printf("GL error: 0x%04x\n", error);
}
