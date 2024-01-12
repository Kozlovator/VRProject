#version 330 core
layout (location = 0) in vec3 in_position; // Position de la particule

uniform mat4 m_proj;  // Matrice de projection
uniform mat4 m_view;  // Matrice de vue
uniform mat4 m_model; // Matrice de modèle

void main() {
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
    gl_PointSize = 1.0; // Taille des points
}
