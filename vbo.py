import numpy as np
import moderngl as mgl
import pywavefront


class VBO:
    def __init__(self, ctx):
        self.vbos = {}
        self.vbos['earth'] = EarthVBO(ctx)
        self.vbos['sun'] = SunVBO(ctx)
        self.vbos['skybox'] = SkyboxVBO(ctx)
        self.vbos['particle'] = ParticleVBO(ctx)

    def destroy(self):
        [vbo.destroy() for vbo in self.vbos.values()]

class BaseVBO:
    def __init__(self, ctx, init_vbo=True):
        self.ctx = ctx
        if init_vbo:
            self.vbo = self.get_vbo()
        self.format: str = None
        self.attribs: list = None

    def get_vertex_data(self): ...

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo

    def destroy(self):
        self.vbo.release()


class EarthVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '2f 3f 3f'
        self.attribs = ['in_texcoord_0', 'in_normal', 'in_position']

    def get_vertex_data(self):
        earth_model = pywavefront.Wavefront('objects/earth/world.obj', cache=True, parse=True)
        obj = earth_model.materials.popitem()[1]
        vertex_data = obj.vertices
        vertex_data = np.array(vertex_data, dtype='f4')
        return vertex_data

class SunVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '2f 3f 3f'
        self.attribs = ['in_texcoord_0', 'in_normal', 'in_position']

    def get_vertex_data(self):
        earth_model = pywavefront.Wavefront('objects/sun/sun.obj', cache=True, parse=True)
        obj = earth_model.materials.popitem()[1]
        vertex_data = obj.vertices
        vertex_data = np.array(vertex_data, dtype='f4')
        return vertex_data


class SkyboxVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f'  # Format pour les coordonnées x, y, z
        self.attribs = ['in_position']

    def get_vertex_data(self):
        skybox_vertices = np.array([
            # right
            -1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0,
            1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0,
            # left
            -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, -1.0,
            -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0,
            # top
            1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0,
            # bottom
            -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0,
            # back
            -1.0, -1.0, -1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0,
            1.0, -1.0, -1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0,
            # front
            -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0,
        ], dtype='f4')
        return skybox_vertices.tobytes()

class ParticleVBO(BaseVBO):
    def __init__(self, ctx, num_particles=1):
        super().__init__(ctx, init_vbo=False)
        self.format = '3f'  # Format pour les coordonnées x, y, z
        self.attribs = ['in_position']  # Nom de l'attribut dans le shader
        self.num_particles = num_particles
        self.vbo = self.create_particle_vbo()

    def create_particle_vbo(self):
        # Générer une seule position pour chaque particule
        particle_positions = np.random.uniform(-1, 1, size=(self.num_particles, 3))
        return self.ctx.buffer(particle_positions.astype('f4').tobytes())
