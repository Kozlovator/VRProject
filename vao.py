from vbo import VBO
from shader_program import ShaderProgram



class VAO:
    def __init__(self, ctx):
        self.ctx = ctx
        self.vbo = VBO(ctx)
        self.program = ShaderProgram(ctx)
        self.vaos = {}

        # earth vao
        self.vaos['earth'] = self.get_vao(
            program=self.program.programs['earth'],
            vbo=self.vbo.vbos['earth'])

        # sun vao
        self.vaos['sun'] = self.get_vao(
            program=self.program.programs['sun'],
            vbo=self.vbo.vbos['sun'])

        # skybox vao
        self.vaos['skybox'] = self.get_vao(
            program=self.program.programs['skybox'],
            vbo=self.vbo.vbos['skybox'])

        # particle vao
        self.vaos['particle'] = self.get_vao(
            program=self.program.programs['particle'],
            vbo=self.vbo.vbos['particle'])

    def get_vao(self, program, vbo):
        vao = self.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs)])
        return vao

    def destroy(self):
        self.vbo.destroy()
        self.program.destroy()