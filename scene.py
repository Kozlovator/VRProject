from model import *
from skybox import Skybox
from particle import ParticleSystem
import numpy as np

class Scene:
    def __init__(self, app):
        self.app = app
        self.objects = []
        self.skybox = Skybox(app)  # Créer une instance de Skybox
        self.particle_system = ParticleSystem(app)  # Créer une instance de ParticleSystem
        self.load()
        self.init_particles()

    def add_object(self, obj):
        self.objects.append(obj)

    def load(self):
        app = self.app
        add = self.add_object

        # Position du Soleil
        sun_position = (10, 0, -20)
        add(Sun(app, pos=sun_position))

        # Ajouter la Terre en orbite autour du Soleil
        add(Earth(app, particle_system= self.particle_system,orbit_center=sun_position, orbit_radius=25, orbit_speed=0.0003, pos=(34.99999887500001, 0, -19.9925000001125)))

    def init_particles(self):
        """
        # Définir le nombre de particules
        number_of_particles = 5000

        # Créer les particules avec des positions aléatoires
        for _ in range(number_of_particles):
            x = np.random.uniform(-50, 50)
            y = np.random.uniform(-50, 50)
            z = np.random.uniform(-50, 50)
            self.particle_system.create_particle((x, y, z), (0, 1, 0))  # Rouge
        """

    def render(self):
        self.skybox.render()
        for obj in self.objects:
            obj.update()
            obj.render()
        self.particle_system.update(self.app.delta_time)
        self.particle_system.render()