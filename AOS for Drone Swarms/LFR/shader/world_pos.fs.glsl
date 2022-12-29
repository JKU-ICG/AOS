R"(
#version 310 es
#extension GL_EXT_shader_io_blocks : enable
precision highp float;
precision highp int;
precision mediump image2DArray;


out vec4 FragColor;

in VS_OUT{
	vec3 FragPos;
	vec3 Normal;
	vec2 TexCoords;
	vec4 FragPosLightSpace;
} fs_in;

uniform sampler2D depthMap;
uniform float near_plane;
uniform float far_plane;

uniform float fbo_min;
uniform float fbo_max;


void main()
{         
	//vec2 uv = fs_in.TexCoords.xy;
    vec4 color = texture(depthMap, fs_in.TexCoords);


    FragColor = vec4(color.rgb, 1.0);

	// DEBUG:
	//FragColor.xy = TexCoords.xy;
}
)"