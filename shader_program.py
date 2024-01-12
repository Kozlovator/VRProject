
class ShaderProgram:
    def __init__(self, ctx):
        self.ctx = ctx
        self.programs = {}
        self.programs['earth'] = self.get_program('earth')
        self.programs['sun'] = self.get_program('sun')
        self.programs['skybox'] = self.get_program('skybox')
        self.programs['particle'] = self.get_program('particle')

    def get_program(self, shader_program_name):
        try:
            with open(f'shaders/{shader_program_name}.vert') as file:
                vertex_shader = file.read()
            print("1= vert", shader_program_name)
            with open(f'shaders/{shader_program_name}.frag') as file:
                fragment_shader = file.read()
            print("2= frag", shader_program_name)
            program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
            print(f"Program '{shader_program_name}' chargé : {program}")
            return program
        except Exception as e:
            print(f"Erreur lors du chargement du shader '{shader_program_name}': {e}")
            return None

    #Méthode pour appeler les 2 textures pour le bump mapping de la Terre
    def setup_earth_shader(self, earth_texture, earth_normal_map):
        self.programs['earth'].use()

        # Lier la texture de la Terre
        earth_texture.use(location=0)
        self.programs['earth']['u_texture_0'] = 0

        # Lier la normal map de la Terre
        earth_normal_map.use(location=1)
        self.programs['earth']['u_normal_map'] = 1

    def destroy(self):
        [program.release() for program in self.programs.values()]
