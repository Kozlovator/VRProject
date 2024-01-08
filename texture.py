import pygame as pg
import moderngl as mgl


class Texture:
    def __init__(self, ctx):
        self.ctx = ctx
        self.textures = {}
        self.textures['earth'] = self.get_texture(path='textures/earth/8k_earth_daymap.jpg')
        self.textures['sun'] = self.get_texture(path='textures/sun/2k_sun.jpg')
        self.textures['earth_normal'] = self.get_texture(path='textures/earth/normal_map.png')

        self.textures['cubemap'] = self.get_cubemap_texture([
            'textures/skybox/right.png',
            'textures/skybox/left.png',
            'textures/skybox/top.png',
            'textures/skybox/bottom.png',
            'textures/skybox/front.png',
            'textures/skybox/back.png'
        ])

    def get_texture(self, path):
        texture = pg.image.load(path).convert()
        texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
        texture = self.ctx.texture(size=texture.get_size(), components=3,
                                   data=pg.image.tostring(texture, 'RGB'))
        # mipmaps
        texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
        texture.build_mipmaps()
        # AF
        texture.anisotropy = 32.0
        return texture

    def get_cubemap_texture(self, paths):
        # Créer une texture cubemap
        cubemap_texture = self.ctx.texture_cube((2048, 2048), 3)
        cubemap_texture.filter = (mgl.LINEAR, mgl.LINEAR)
        cubemap_texture.wrap_s = cubemap_texture.wrap_t = cubemap_texture.wrap_r = 'clamp_to_edge'

        # Charger et attacher chaque image à la texture cubemap
        for i, path in enumerate(paths):
            texture = pg.image.load(path).convert()
            texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
            cubemap_texture.write(i, pg.image.tostring(texture, 'RGB'))

        return cubemap_texture

    def destroy(self):
        [tex.release() for tex in self.textures.values()]