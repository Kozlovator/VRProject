import os

import moderngl as mgl
import numpy as np
import glm
import struct
import moderngl
import random
#from ColladaLoader import ColladaLoader  # Importe spécifiquement la classe ColladaLoader
import pygame as pg

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

        super().update()

    def on_init(self):
        # texture
        self.texture = self.app.mesh.texture.textures[self.tex_id]
        self.program['u_texture_0'] = 0
        self.texture.use()

        self.normal_map = self.app.mesh.texture.textures['earth_normal']
        self.program['earthNormalMap'] = 1
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

"""class AnimModel:
    def __init__(self, app, collada_file, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        self.app = app
        self.pos = pos
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = scale
        self.m_model = self.get_model_matrix()
        self.camera = self.app.camera

        # Chargement des données COLLADA
        self.collada_file = collada_file
        self.loader = ColladaLoader(collada_file)
        self.geometry = self.loader.get_geometry()
        self.skinning_data = self.loader.get_skinning_data()
        self.animations = self.loader.get_animations()
        self.textures = self.loader.get_textures()
        self.program = self.load_shader_program("shaders/dragon.vert", "shaders/dragon.frag")

        # Initialisation des données de rendu (VAO, VBO, textures, etc.)
        self.init_render_data()

    @staticmethod
    def load_shader_source(file_path):
        with open(file_path, 'r') as file:
            return file.read()

    def load_shader_program(self, vertex_shader_path, fragment_shader_path):
        # Load shader sources
        vertex_shader_source = self.load_shader_source(vertex_shader_path)
        fragment_shader_source = self.load_shader_source(fragment_shader_path)

        # Create the program with both shaders
        program = self.app.ctx.program(vertex_shader=vertex_shader_source,
                                       fragment_shader=fragment_shader_source)
        return program

    def get_model_matrix(self):
        m_model = glm.mat4()
        m_model = glm.translate(m_model, self.pos)
        m_model = glm.rotate(m_model, self.rot.z, glm.vec3(0, 0, 1))
        m_model = glm.rotate(m_model, self.rot.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.rot.x, glm.vec3(1, 0, 0))
        m_model = glm.scale(m_model, self.scale)
        return m_model

    def init_render_data(self):
        self.texture_objects = {}
        for tex_path in self.textures:
            tex_name = os.path.basename(tex_path)
            self.texture_objects[tex_name] = self.load_texture(tex_path)

        # Charger les VBOs et VAOs pour chaque géométrie
        self.vbos = {}
        self.vaos = {}
        for geometry in self.geometry:
            vbo = self.app.ctx.buffer(geometry['vertices'])
            self.vbos[geometry['id']] = vbo

            vao = self.app.ctx.vertex_array(
                self.program,
                [(vbo, '3f 3f 2f', 'inPosition', 'inNormal', 'inTexCoord')]
            )
            self.vaos[geometry['id']] = vao

    def load_texture(self, path):
        # Charger une texture en utilisant Pygame et créer un objet texture ModernGL
        pg_img = pg.image.load(path).convert()
        pg_img = pg.transform.flip(pg_img, False, True) 
        data = pg.image.tostring(pg_img, 'RGB', True) 

        # Créer une texture ModernGL
        texture = self.app.ctx.texture(pg_img.get_size(), 3, data)
        texture.build_mipmaps()  # Générer des mipmaps pour la texture
        return texture

    def update(self):
        pass

    def render(self):
        pass

class Dragon(AnimModel):
    def __init__(self, app, collada_file, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        super().__init__(app, collada_file, pos, rot, scale)

    def load_model(self):
        # Charger les données du modèle à partir du fichier COLLADA
        self.geometry = self.loader.get_geometry()
        self.skinning_data = self.loader.get_skinning_data()
        self.animations = self.loader.get_animations()
        self.textures = self.loader.get_textures()

        # Charger les textures dans la mémoire du GPU
        self.texture_objects = {}
        for tex_name, tex_path in self.textures.items():
            self.texture_objects[tex_name] = self.load_texture(tex_path)

        # Initialiser les données de rendu pour chaque géométrie
        self.vbos = {}
        self.vaos = {}
        for geometry in self.geometry:
            # Créer et remplir le VBO
            vbo = self.app.ctx.buffer(geometry['vertices'].tobytes())
            self.vbos[geometry['id']] = vbo

            # Créer le VAO et l'associer au VBO
            vao = self.app.ctx.vertex_array(self.program, [(vbo, '3f 3f 2f', 'in_vert', 'in_norm', 'in_text')])
            self.vaos[geometry['id']] = vao

    def setup_animation(self):
        if not self.animations:
            print("Erreur : Aucune donnée d'animation trouvée pour le dragon.")
            return

        # Initialiser les données pour gérer l'état de l'animation
        # Par exemple, vous pouvez initialiser des variables pour l'animation courante, la position temporelle actuelle, etc.
        self.current_animation = self.animations[0]
        self.current_time = 0  # Initialiser le temps courant de l'animation à 0

        # Initialiser les matrices de jointure pour chaque joint
        self.joint_matrices = [glm.mat4() for _ in range(len(self.skinning_data['joints']))]

        # Configurer les uniformes de jointure dans le programme shader si nécessaire
        for i in range(len(self.joint_matrices)):
            uniform_location = f'jointTransforms[{i}]'
            if uniform_location in self.program:
                self.program[uniform_location].write(self.joint_matrices[i].tobytes())

    def update(self):
        # Mise à jour du temps de l'animation
        self.current_time += self.app.delta_time

        # Sélectionner l'animation courante (ici, prenons la première pour l'exemple)
        current_animation = self.animations[0]

        # Calculer la durée de l'animation et ajuster current_time en conséquence
        animation_duration = current_animation.length
        self.current_time %= animation_duration

        # Calculer les transformations de joint pour l'animation courante et le temps actuel
        joint_transforms = self.calculate_joint_transforms(current_animation, self.current_time)

        # Transmettre les matrices de jointure au shader
        for i, joint_transform in enumerate(joint_transforms):
            uniform_location = f'jointTransforms[{i}]'
            if uniform_location in self.program:
                self.program[uniform_location].write(joint_transform.tobytes())
        super().update()

    def calculate_joint_transforms(self, animation, time):
        joint_transforms = []

        # Parcourir tous les joints
        for joint_id, joint_data in self.skinning_data['joints'].items():
            # Obtenir les keyframes de l'animation pour ce joint
            keyframes = animation[joint_id] 

            # Trouver les keyframes avant et après le temps actuel
            prev_frame, next_frame = self.find_frames(keyframes, time)

            # Calculer la progression entre ces keyframes
            progression = self.calculate_progression(prev_frame, next_frame, time)

            # Interpoler les transformations entre les keyframes
            interpolated_transform = self.interpolate_transforms(prev_frame, next_frame, progression)

            # Appliquer la transformation du parent si nécessaire (dépend de la structure de vos données)
            # Par exemple: interpolated_transform = parent_transform * interpolated_transform

            # Convertir la transformation en une matrice 4x4 et ajoutez-la à la liste des transformations
            joint_transforms.append(interpolated_transform.to_matrix())

        return joint_transforms

    def find_frames(self, keyframes, time):
        prev_frame = keyframes[0]
        next_frame = keyframes[1]
        for frame in keyframes:
            if frame.time > time:
                next_frame = frame
                break
            prev_frame = frame
        return prev_frame, next_frame

    def calculate_progression(self, prev_frame, next_frame, current_time):
        total_time = next_frame.time - prev_frame.time
        current_time = current_time - prev_frame.time
        progression = current_time / total_time
        return progression


    def interpolate_transforms(self, prev_frame, next_frame, progression):
        interpolated_pos = prev_frame.pos + (next_frame.pos - prev_frame.pos) * progression
        interpolated_rot = glm.slerp(prev_frame.rot, next_frame.rot, progression)
        interpolated_scale = prev_frame.scale + (next_frame.scale - prev_frame.scale) * progression
        return Transform(interpolated_pos, interpolated_rot, interpolated_scale)

    def render(self):
        # Activer le shader
        self.app.ctx.use_program(self.program)

        # Configurer les uniformes de transformation et autres paramètres nécessaires
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)

        # Configurer les uniformes de lumière, caméra, etc.
        self.program['light.position'].write(self.app.light.position)
        
        # Bind la texture si nécessaire
        for tex_name, tex_object in self.texture_objects.items():
            tex_object.use()  # suppose que chaque objet a une seule texture pour l'exemple

        # Dessiner chaque géométrie avec son VAO
        for geo_id, vao in self.vaos.items():
            vao.render()

class Transform:
    def __init__(self, position=glm.vec3(), rotation=glm.quat(), scale=glm.vec3(1, 1, 1)):
        self.position = position
        self.rotation = rotation
        self.scale = scale

    def to_matrix(self):
        # Retourne la matrice de transformation 4x4 correspondante
        translation_matrix = glm.translate(glm.mat4(1), self.position)
        rotation_matrix = glm.mat4_cast(self.rotation)
        scale_matrix = glm.scale(glm.mat4(1), self.scale)
        return translation_matrix * rotation_matrix * scale_matrix
"""
