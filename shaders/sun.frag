#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
uniform sampler2D u_texture_0;  // Texture du soleil

void main() {
    vec4 texColor = texture(u_texture_0, uv_0);
    float brightnessFactor = 1.5;  // Ajustez cette valeur pour changer la luminosité
    fragColor = vec4(texColor.rgb * brightnessFactor, texColor.a);
}
