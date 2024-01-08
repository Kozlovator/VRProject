#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec3 inNormal;
layout (location = 2) in vec2 inTexCoord;
layout (location = 3) in ivec4 jointIndices;
layout (location = 4) in vec4 weights;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;
uniform mat4 jointTransforms[100]; // Ajustez la taille selon vos besoins

out vec2 texCoord;

void main() {
    mat4 skinningMatrix = mat4(0.0);
    for(int i = 0; i < 4; i++) {
        skinningMatrix += weights[i] * jointTransforms[jointIndices[i]];
    }

    vec4 worldPosition = skinningMatrix * vec4(inPosition, 1.0);
    gl_Position = projection * view * model * worldPosition;
    texCoord = inTexCoord;
}