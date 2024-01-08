#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
in vec3 normal;  // Normale de sommet n'est plus nécessaire
in vec3 fragPos;

struct Light {
    vec3 position;
    vec3 Ia;
    vec3 Id;
    vec3 Is;
};

uniform Light light;
uniform sampler2D u_texture_0;  // Texture de la Terre
uniform sampler2D earthNormalMap; // Uniforme pour la normal map
uniform vec3 camPos;

vec3 getLight(vec3 color, vec3 Normal) {

    // ambient light
    vec3 ambient = light.Ia;

    // diffuse light
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(0, dot(lightDir, Normal));
    vec3 diffuse = diff * light.Id;

    // specular light
    vec3 viewDir = normalize(camPos - fragPos);
    vec3 reflectDir = reflect(-lightDir, Normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0), 32);
    vec3 specular = spec * light.Is;

    return color * (ambient + diffuse + specular);
}

void main() {
    float gamma = 2.2;
    vec3 color = texture(u_texture_0, uv_0).rgb;
    color = pow(color, vec3(gamma));

    // Utilisation uniquement de la normal map pour la normale
    vec3 normalMap = texture(earthNormalMap, uv_0).rgb;
    normalMap = normalMap * 2.0 - 1.0; // Convertir de [0,1] à [-1,1]
    vec3 adjustedNormal = normalize(normalMap * normal); // Combinaison des normales
    color = getLight(color, adjustedNormal );

    color = pow(color, 1 / vec3(gamma));
    fragColor = vec4(color, 1.0);
}
