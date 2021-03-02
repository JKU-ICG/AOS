#version 310 es
#extension GL_EXT_shader_io_blocks : enable
precision highp float;
precision highp int;
precision mediump image2DArray;


out vec4 FragColor;

in VS_OUT {
    vec3 FragPos;
    vec3 Normal;
    vec2 TexCoords;
    vec4 FragPosLightSpace;
} fs_in;

uniform sampler2D imageTexture;
//uniform sampler2D shadowMap;


vec4 ProjectImage(vec4 fragPosLightSpace)
{
    // perform perspective divide
    vec3 projCoords = fragPosLightSpace.xyz / fragPosLightSpace.w;
    // transform to [0,1] range
    projCoords = projCoords * 0.5 + 0.5;
    // get closest depth value from light's perspective (using [0,1] range fragPosLight as coords)
	if (projCoords.x>=0.0f && projCoords.x <= 1.0f && projCoords.y >= 0.0f && projCoords.y <= 1.0f)
	{
		// for some reason the images need to be flipped!
		return vec4(texture(imageTexture, vec2(1.0f-projCoords.x,1.0f-projCoords.y)).rrr, 1.0f);
	}
	else
	{
		return vec4(0.0f);
	}
       
}

void main()
{           
	//FragColor = vec4(fs_in.FragPos.rgb, 1.0); return;
    
    FragColor = vec4(ProjectImage(fs_in.FragPosLightSpace));
}