import numpy as np
import glm
import moderngl as mgl


class Skybox:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.texture = app.mesh.texture.textures['cubemap']
        self.vao = app.mesh.vao.vaos['skybox']
        self.program = self.vao.program
        self.camera = app.camera

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

        # Créer le VBO pour la skybox
        self.vbo = self.ctx.buffer(skybox_vertices.tobytes())
        # Associer le VBO au VAO
        self.vao = self.ctx.vertex_array(self.program, [(self.vbo, '3f', 'in_position')])

    def render(self):
        # Préparation du rendu de la skybox
        self.ctx.disable(mgl.DEPTH_TEST)
        self.texture.use()

        # Utiliser une matrice de vue modifiée pour la skybox
        view_matrix = glm.mat4(glm.mat3(self.camera.m_view))
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(view_matrix)

        # Render la skybox
        self.vao.render()

        # Réactiver le test de profondeur pour le reste de la scène
        self.ctx.enable(mgl.DEPTH_TEST)

    def destroy(self):
        self.vbo.release()
