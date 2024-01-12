#version 330 core
out vec4 FragColor;

uniform vec3 particleColor;  // Couleur de la particule
uniform bool isLit;         // État d'illumination de la particule

void main() {
    if (isLit) {
        FragColor = vec4(particleColor, 1.0);  // Particule allumée
    } else {
        FragColor = vec4(particleColor, 0.3);  // Particule éteinte ou en faible luminosité
    }
}