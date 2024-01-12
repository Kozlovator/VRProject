import moderngl as mgl
import numpy as np
import glm
import struct
import moderngl
import random


class BaseModel:
    def __init__(self, app, vao_name, tex_id, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        self.app = app
        self.pos = pos
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = scale
        self.m_model = self.get_model_matrix()
        self.tex_id = tex_id
        self.vao = app.mesh.vao.vaos[vao_name]
        self.program = self.vao.program
        self.camera = self.app.camera

    def update(self): ...

    def get_model_matrix(self):
        m_model = glm.mat4()
        # translate
        m_model = glm.translate(m_model, self.pos)
        # rotate
        m_model = glm.rotate(m_model, self.rot.z, glm.vec3(0, 0, 1))
        m_model = glm.rotate(m_model, self.rot.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.rot.x, glm.vec3(1, 0, 0))
        # scale
        m_model = glm.scale(m_model, self.scale)
        return m_model

    def render(self):
        self.update()
        self.vao.render()


class Earth(BaseModel):
    def __init__(self, app, particle_system,vao_name='earth', tex_id='earth',
                 pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), orbit_center=(0, 0, 0), orbit_radius=5, orbit_speed=0.01):
        super().__init__(app, vao_name, tex_id, pos, rot, scale)
        self.particle_system = particle_system
        self.orbit_center = orbit_center
        self.orbit_radius = orbit_radius
        self.orbit_speed = orbit_speed
        self.orbit_angle = 0

        #faire tourner la terre sur elle meme
        self.rotation_speed = 0.003  # Vitesse de rotation de la Terre
        self.rotation_angle = 0  # Angle de rotation initial

        self.earth_radius = 1.0
        self.previous_pos = glm.vec3(pos)


        self.on_init()

    def update(self):
        # Mise à jour de la position orbitale
        self.orbit_angle += self.orbit_speed
        new_x = self.orbit_center[0] + self.orbit_radius * np.cos(self.orbit_angle)
        new_z = self.orbit_center[2] + self.orbit_radius * np.sin(self.orbit_angle)

        # Mettre à jour la position
        self.pos = (new_x, self.pos[1], new_z)

        self.rotation_angle += self.rotation_speed
        self.rot.y = self.rotation_angle

        # Mise à jour de la matrice de modèle
        self.m_model = self.get_model_matrix()

        # Configuration de la texture et des shaders
        self.texture.use()
        self.program['camPos'].write(self.camera.position)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        direction = glm.normalize(self.pos - self.previous_pos)
        particle_spawn_offset = self.earth_radius

        # Ajouter de la variation pour simuler un effet de nuage
        for _ in range(10):  # Créer plusieurs particules par mise à jour
            variation = glm.vec3(
                random.uniform(-1.7, 1.7),
                random.uniform(-2.2, 1.2),
                random.uniform(-1.7, 1.7)
            ) * 0.5  # Ajuster ce multiplicateur pour contrôler la dispersion

            particle_spawn_position = self.pos - direction * particle_spawn_offset + variation

            if self.particle_system:
                self.particle_system.create_particle(particle_spawn_position, (0, 1, 0))

        self.previous_pos = glm.vec3(self.pos)

        #super().update()

    def on_init(self):
        # texture
        self.texture = self.app.mesh.texture.textures[self.tex_id]
        self.program['u_texture_0'] = 0
        self.texture.use()

        self.normal_map = self.app.mesh.texture.textures['u_normal_map']
        self.program['u_normal_map'] = 1
        self.normal_map.use(location=1)

        # mvp
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        # light
        self.program['light.position'].write(self.app.light.position)
        self.program['light.Ia'].write(self.app.light.Ia)
        self.program['light.Id'].write(self.app.light.Id)
        self.program['light.Is'].write(self.app.light.Is)

class Sun(BaseModel):
    def __init__(self, app, vao_name='sun', tex_id='sun',
                 pos=(0, 0, 0), rot=(0, 0, 0), scale=(10, 10, 10)):
        super().__init__(app, vao_name, tex_id, pos, rot, scale)
        self.on_init()

    def update(self):

        self.texture.use()
        # Mise à jour des matrices de transformation
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)

    def on_init(self):
        # Initialisation de la texture
        self.texture = self.app.mesh.texture.textures[self.tex_id]
        self.program['u_texture_0'] = 0
        self.texture.use()
        # Initialisation des matrices MVP
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)

class ParticleModel(BaseModel):
    def __init__(self, app, vao_name='particle', pos=(0, 0, 0), scale=(1, 1, 1), color=(1, 1, 1)):
        super().__init__(app, vao_name, None, pos, (0, 0, 0), scale)
        self.color_start = glm.vec3(1, 1, 1)
        self.color_end = glm.vec3(1, 0, 0)
        self.current_color = glm.vec3(1, 1, 1)
        self.is_lit = True
        self.timer = 5.0
        self.alive = True  # Ajout de l'attribut alive
        self.lifetime = 10000.0  # Ajout de la durée de vie

        self.lerp_time = 0.0
        self.lerp_duration = 10000  # Durée de l'interpolation

    def update(self, delta_time=10):
        self.lerp_time += delta_time
        t =  self.lerp_time / self.lerp_duration
        if t > 1.0:
            t = 0.0
            self.lerp_time = 0.0
        self.current_color = glm.mix(self.color_start, self.color_end, t)
        self.lifetime -= delta_time  # Diminuer la durée de vie
        if self.lifetime <= 0:
            self.alive = False  # Désactiver la particule

    def render(self):
        self.app.mesh.vao.vaos['particle'].render(moderngl.POINTS)
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)

        #current_color = (0.0, 1.0, 0.0) if self.is_lit else (0.0, 0.0, 0.0)
        # Convertissez le tuple en bytes
        color_bytes = struct.pack('3f', *self.current_color)
        self.program['particleColor'].write(color_bytes)

    def on_init(self):

        pass