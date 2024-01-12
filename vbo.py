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
        self.format = '2f 3f 3f 3f'  # Mettre à jour pour inclure tangentes et bitangentes
        self.attribs = ['in_texcoord_0', 'in_normal', 'in_position', 'in_tangent']

    def get_vertex_data(self):
        earth_model = pywavefront.Wavefront('objects/earth/world.obj', cache=True, parse=True)
        obj = earth_model.materials.popitem()[1]

        # Séparer les données de sommets, UVs, et normales
        vertices, uvs, normals = self.separate_vertex_data(obj.vertices)
        print("Vertices:", type(vertices), len(vertices), vertices[:3])  # Affiche les 3 premiers vertices
        print("UVs:", type(uvs), len(uvs), uvs[:3])  # Affiche les 3 premiers UVs
        print("Normals:", type(normals), len(normals), normals[:3])
        # Calculer les tangentes et bitangentes
        tangents = self.calculate_tangents_bitangents(vertices, uvs, normals)
        print("Tangents:", type(tangents), len(tangents), tangents[:3])  # Affiche les 3 premières tangentes
        #print("Bitangents:", type(bitangents), len(bitangents), bitangents[:3])  # Affiche les 3 premières bitangentes

        # Combiner toutes les informations en un seul tableau
        vertex_data = []
        for v, uv, n, t in zip(vertices, uvs, normals, tangents):
            vertex_data.extend(v)  # v doit être une séquence (par exemple, un tuple de 3 valeurs)
            vertex_data.extend(uv)  # uv doit être une séquence (par exemple, un tuple de 2 valeurs)
            vertex_data.extend(n)  # n doit être une séquence (par exemple, un tuple de 3 valeurs)
            vertex_data.extend(t)  # t doit être une séquence (par exemple, un tuple de 3 valeurs)
            #vertex_data.extend(b)  # b doit être une séquence (par exemple, un tuple de 3 valeurs)

        vertex_data = np.array(vertex_data, dtype='f4')

        return vertex_data

    def separate_vertex_data(self, interleaved_data):
        vertices = [(interleaved_data[i], interleaved_data[i + 1], interleaved_data[i + 2])
                    for i in range(0, len(interleaved_data), 8)]
        uvs = [(interleaved_data[i + 3], interleaved_data[i + 4])
               for i in range(0, len(interleaved_data), 8)]
        normals = [(interleaved_data[i + 5], interleaved_data[i + 6], interleaved_data[i + 7])
                   for i in range(0, len(interleaved_data), 8)]
        return vertices, uvs, normals

    def calculate_tangents_bitangents(self, vertices, uvs, normals):
        tangents = np.zeros_like(vertices)
        bitangents = np.zeros_like(vertices)

        for i in range(0, len(vertices), 3):
            v0, v1, v2 = vertices[i], vertices[i + 1], vertices[i + 2]
            uv0, uv1, uv2 = uvs[i], uvs[i + 1], uvs[i + 2]

            # Calculer les différences de position pour les arêtes du triangle
            deltaPos1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
            deltaPos2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])

            # Calculer les différences de coordonnées UV pour les arêtes du triangle
            deltaUV1 = (uv1[0] - uv0[0], uv1[1] - uv0[1])
            deltaUV2 = (uv2[0] - uv0[0], uv2[1] - uv0[1])

            # Calcul de la tangente et de la bitangente
            r = 1.0 / (deltaUV1[0] * deltaUV2[1] - deltaUV1[1] * deltaUV2[0])
            tangent = ((deltaPos1[0] * deltaUV2[1] - deltaPos2[0] * deltaUV1[1]) * r,
                       (deltaPos1[1] * deltaUV2[1] - deltaPos2[1] * deltaUV1[1]) * r,
                       (deltaPos1[2] * deltaUV2[1] - deltaPos2[2] * deltaUV1[1]) * r)
            bitangent = ((deltaPos2[0] * deltaUV1[0] - deltaPos1[0] * deltaUV2[0]) * r,
                         (deltaPos2[1] * deltaUV1[0] - deltaPos1[1] * deltaUV2[0]) * r,
                         (deltaPos2[2] * deltaUV1[0] - deltaPos1[2] * deltaUV2[0]) * r)

            # Accumuler les tangentes et bitangentes pour chaque sommet du triangle
            tangents[i] += tangent
            tangents[i + 1] += tangent
            tangents[i + 2] += tangent

            bitangents[i] += bitangent
            bitangents[i + 1] += bitangent
            bitangents[i + 2] += bitangent

        # Normaliser les tangentes et bitangentes
        tangents = np.array([self.normalize(v) for v in tangents])
        bitangents = np.array([self.normalize(v) for v in bitangents])

        return tangents

    def normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

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
