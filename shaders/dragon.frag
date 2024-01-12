#version 330 core

in vec2 texCoord;
out vec4 FragColor;

uniform sampler2D texture_diffuse; // Assuming one diffuse texture for simplicity

void main()
{
    FragColor = texture(texture_diffuse, texCoord);
}
