#version 330 core

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 2) in vec3 in_normal;
layout (location = 2) in vec3 in_position;

out vec2 uv_0;
out vec3 Normal;
out vec3 FragPos;

uniform mat4 m_model;
uniform mat4 m_view;
uniform mat4 m_proj;

void main()
{
    uv_0 = in_texcoord_0;
    Normal = mat3(transpose(inverse(m_model))) * in_normal;
    FragPos = vec3(m_model * vec4(in_position, 1.0));

    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}
