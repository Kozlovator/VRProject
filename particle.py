from model import ParticleModel


class ParticleSystem:
    def __init__(self, app):
        self.particles = []
        self.app = app

    def create_particle(self, position, color, lifetime=10000):
        particle = ParticleModel(self.app, 'particle', position, color=color)
        particle.lifetime = lifetime  # Durée de vie de la particule
        self.particles.append(particle)

    def update(self, delta_time):
        for particle in self.particles:
            particle.update(delta_time)
            # Supprimer la particule si sa durée de vie est écoulée
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def render(self):
        for particle in self.particles:
            if particle.alive:  # Vérifier si la particule est active avant de la render
                particle.render()
