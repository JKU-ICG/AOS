#version 310 es
#extension GL_EXT_shader_io_blocks : enable
precision highp float;
precision highp int;
precision mediump image2DArray;
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoords;

out vec3 FragPos;
out vec2 TexCoords;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    vec4 worldPos = model * vec4(aPos, 1.0);
    FragPos = worldPos.xyz; 
    TexCoords = aTexCoords;
    
    gl_Position = projection * view * worldPos;
}