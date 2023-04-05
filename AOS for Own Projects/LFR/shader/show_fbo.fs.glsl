#version 310 es
#extension GL_EXT_shader_io_blocks : enable
precision highp float;
precision highp int;
precision mediump image2DArray;


out vec4 FragColor;

in vec2 TexCoords;

uniform sampler2D fboTexture;
uniform float near_plane;
uniform float far_plane;

uniform float fbo_min;
uniform float fbo_max;

uniform bool flipX;
uniform bool flipY;


void main()
{         
	vec2 uv = TexCoords.xy;

	if(flipX) uv.x = 1.0f - uv.x;
	if(flipY) uv.y = 1.0f - uv.y;

    vec4 color = texture(fboTexture, uv);
    // FragColor = vec4(vec3(LinearizeDepth(depthValue) / far_plane), 1.0); // perspective
	if( color.a > 0.0f )
	{
		color.rgb /= color.a; // normalize & avoid division by zero!
		// tonemap:
		color.rgb =  (color.rgb -fbo_min) / (fbo_max - fbo_min);
	}

    FragColor = vec4(color.rgb, 1.0); 

	// DEBUG:
	//FragColor.xy = TexCoords.xy;
}