#version 330 core

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec3 in_position;
layout (location = 3) in vec3 in_tangent;
// La ligne suivante peut être supprimée car le bitangent sera recalculé
// layout (location = 4) in vec3 in_bitangent;

out vec2 uv_0;
out vec3 fragPos;
out mat3 TBN;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

void main() {
    uv_0 = in_texcoord_0;
    fragPos = vec3(m_model * vec4(in_position, 1.0));

    vec3 T = normalize(mat3(m_model) * in_tangent);
    vec3 N = normalize(mat3(m_model) * in_normal);

    // Re-orthogonaliser T par rapport à N
    T = normalize(T - dot(T, N) * N);

    // Recalculer B en utilisant le produit vectoriel de N et T
    vec3 B = cross(N, T);

    TBN = mat3(T, B, N);

    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}

