#version 310 es
#extension GL_EXT_shader_io_blocks : enable
precision highp float;
precision highp int;
precision mediump image2DArray;


out vec4 FragColor;

in vec2 TexCoords;

uniform sampler2D gPosition;
uniform sampler2D imageTexture;
//uniform sampler2D shadowMap;

uniform mat4 lightSpaceMatrix;


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
	// retrieve data from gbuffer
    vec4 FragPos = texture(gPosition, TexCoords).rgba;
	if( FragPos.a < 1.0 ) discard; // outside of DEM!

    vec4 FragPosLightSpace = lightSpaceMatrix * vec4(FragPos.xyz, 1.0);
    
    FragColor = vec4(ProjectImage(FragPosLightSpace));
}