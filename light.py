import glm

class Light:
    def __init__(self, position=(10, 0, -20), color=(1, 1, 1)):
        self.position = glm.vec3(position)
        self.color = glm.vec3(color)
        # intensities
        self.Ia = 0.03 * self.color  # ambient
        self.Id = 0.8 * self.color  # diffuse
        self.Is = 0.6 * self.color  # specular