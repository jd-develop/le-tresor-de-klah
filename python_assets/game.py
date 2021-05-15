#!/usr/bin/env python3
# coding:utf-8
import pygame
from pygame import mixer
from pygame import locals
import pytmx
import pyscroll

from python_assets import player


class Game:
    def __init__(self, version) -> None:
        self.version = version
        self.FPS = 60
        self.screen = pygame.display.set_mode((800, 600), locals.RESIZABLE)
        pygame.display.set_caption("Le trésor de Klah")

        pygame.font.init()
        self.pixel_verdana = pygame.font.Font("assets/fonts/PixelFJVerdana12pt.ttf", 12)

        # charger la carte
        tmx_data = pytmx.util_pygame.load_pygame("assets/maps/spawn.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 2
        self.map = "spawn"

        # générer un joueur
        player_position = tmx_data.get_object_by_id(1)
        self.player = player.Player(player_position.x, player_position.y)

        # liste de collisions
        self.walls = []

        for obj in tmx_data.objects:
            if obj.type == "collision":
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
        
        # dessiner le goupe de calques
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=1)
        self.group.add(self.player)
    
    def update(self):
        self.group.update()

        # vérif collision
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back()
    
    def hundle_input(self):
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_z] or pressed[pygame.K_UP]:
            self.player.change_animation("up")
            self.player.move_up()
        elif pressed[pygame.K_s] or pressed[pygame.K_DOWN]:
            self.player.change_animation("down")
            self.player.move_down()
        elif pressed[pygame.K_d] or pressed[pygame.K_RIGHT]:
            self.player.change_animation("right")
            self.player.move_right()
        elif pressed[pygame.K_q] or pressed[pygame.K_LEFT]:
            self.player.change_animation("left")
            self.player.move_left()
    
    def run(self):
        mixer.music.load("assets/music/CrystalZone - Focus.ogg")
        mixer.music.play(-1)
        running = True
        clock = pygame.time.Clock()
        
        while running:
            self.player.save_location()
            self.hundle_input()
            self.update()
            self.group.center(self.player.rect.center)
            self.group.draw(self.screen)
            self.screen.blit(self.pixel_verdana.render(self.version, False, (0, 0, 0)), (0, 0))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == locals.VIDEORESIZE:
                    width, height = event.size
                    if width < 800:
                        width = 800
                    if height < 600:
                        height = 600
                    self.screen = pygame.display.set_mode((width,height), locals.RESIZABLE)
                    self.map_layer.set_size(self.screen.get_size())

            clock.tick(self.FPS)
        
        pygame.quit()
