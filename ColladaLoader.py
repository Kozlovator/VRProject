from collada import Collada
import collada.polylist
import collada.triangleset

class ColladaLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.mesh = None
        self.load()

    def load(self):
        #Charge le fichier COLLADA et extrait les données.
        try:
            self.mesh = Collada(self.file_path)
        except Exception as e:
            print(f"Failed to load COLLADA file: {e}")
            self.mesh = None

    def get_geometry(self):
        #Extrait et retourne les informations de géométrie.
        geometries = []
        if self.mesh:
            for geometry in self.mesh.geometries:
                for primitive in geometry.primitives:
                    if isinstance(primitive, (collada.polylist.Polylist, collada.triangleset.TriangleSet)):
                        geometries.append({
                            'id': geometry.id,  # Assurez-vous que ceci est correct et unique
                            'vertices': primitive.vertex,
                            'normals': primitive.normal,
                            'texcoords': primitive.texcoordset
                        })
        return geometries

    def get_skinning_data(self):
        #Extrait et retourne les données de skinning.
        controllers = []
        if self.mesh:
            for controller in self.mesh.controllers:
                if isinstance(controller, collada.controller.Skin):  # Vérifie si le contrôleur est de type Skin
                    skin_data = {
                        'bind_shape_matrix': controller.bind_shape_matrix,
                        'weights': controller.weights,
                    }
                    controllers.append(skin_data)
        return controllers

    def get_animations(self):
        #Extrait et retourne les animations.
        animations_list = []
        if self.mesh:
            # Parcourir toutes les animations au niveau racine
            for animation in self.mesh.animations:
                # Appel récursif pour explorer les animations enfants et extraire les données
                self.extract_animation_data(animation, animations_list)
        return animations_list

    def extract_animation_data(self, animation, animations_list):
        #Extrait récursivement les données des animations et des enfants.
        # Supposons que chaque animation peut contenir des sous-animations
        for child in animation.children:
            if isinstance(child, collada.animation.Animation):
                # Si l'enfant est une animation, plongez plus profondément
                self.extract_animation_data(child, animations_list)

    def get_textures(self):
        #Extrait et retourne les chemins des textures.
        textures = []
        if self.mesh:
            for image in self.mesh.images:
                textures.append(image.path)
        return textures
