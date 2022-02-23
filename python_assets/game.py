#!/usr/bin/env python3
# coding:utf-8
import pygame
from pygame import mixer
from pygame import locals
import pytmx
import pyscroll

import random

from python_assets import player
from python_assets import item


class Game:
    def __init__(self, version) -> None:
        self.version = version
        self.FPS = 60
        self.screen = pygame.display.set_mode((800, 600), locals.RESIZABLE)
        pygame.display.set_caption("Le trésor de Klah")

        pygame.font.init()
        self.pixel_verdana = pygame.font.Font("assets/fonts/PixelFJVerdana12pt.ttf", 12)

        self.last_action = "nothing here :)"

        # charger la carte
        self.tmx_data = pytmx.util_pygame.load_pygame("assets/maps/spawn.tmx")
        self.map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(self.map_data, self.screen.get_size())
        self.map_layer.zoom = 2
        self.map = "spawn"

        # générer un joueur
        player_position = self.tmx_data.get_object_by_name("playerspawn")
        self.player = player.Player(player_position.x, player_position.y)
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=2)
        self.group.add(self.player)

        # liste de collisions + items
        self.walls = []
        self.items = []
        for obj in self.tmx_data.objects:
            if obj.type == "collision":
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            if obj.name == "coin":
                coin = item.Item(obj.x, obj.y, 'purse', loot={
                    'coin': random.randint(5, 10),
                    'emerald': 0 if random.randint(1, 10) != 1 else random.randint(1, 5),
                    'mushroom': 0 if random.randint(1, 5) != 1 else random.randint(0, 10),
                    'bone': 0 if random.randint(1, 20) != 1 else random.randint(0, 1),
                    'cheese': 0 if random.randint(1, 100) != 1 else random.randint(0, 1)
                }
                                 )
                self.group.add(coin)
                self.items.append(coin)
            elif obj.name == "apple":
                apple = item.Item(obj.x, obj.y, 'food/redapple', loot={'apple': 1})
                self.group.add(apple)
                self.items.append(apple)
            elif obj.name == "dictionary":
                dictionary = item.Item(obj.x, obj.y, 'books/book14', outline='normal', loot={'dictionary': 1})
                self.group.add(dictionary)
                self.items.append(dictionary)
            elif obj.name == "rock":
                rock = item.Item(obj.x, obj.y, 'rock', loot={'rock': 1})
                self.group.add(rock)
                self.items.append(rock)

    def update(self):
        self.group.update()

        # vérification des collisions
        for sprite in self.group.sprites():
            if isinstance(sprite, player.Player):
                # objets collisions
                if sprite.feet.collidelist(self.walls) > -1:
                    sprite.move_back()
                # ITEMS
                items_collided = sprite.rect.collidelistall(self.items)
                if len(items_collided) > 0:
                    indexes = []
                    for item_idx in items_collided:
                        item_ = self.items[item_idx]
                        self.group.remove(item_)
                        self.player.loot(item_.loot)
                        loot = {}
                        for loot_ in item_.loot:
                            if item_.loot[loot_] != 0:
                                loot[loot_] = item_.loot[loot_]
                        self.last_action = ', '.join(f"{x} +{loot[x]}" for x in loot)
                        indexes.append(item_idx)
                    self.items = [e for i, e in enumerate(self.items) if i not in indexes]

    def handle_input(self):
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
        elif pressed[pygame.K_m]:
            print(self.map)
        elif pressed[pygame.K_e]:
            print(self.player.inventory)

    def change_map(self, map_name: str = "spawn"):
        # charger la carte
        self.tmx_data = pytmx.util_pygame.load_pygame(f"assets/maps/{map_name}.tmx")
        self.map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(self.map_data, self.screen.get_size())
        self.map_layer.zoom = 2
        self.map = map_name

    def run(self):
        mixer.music.load("assets/music/CrystalZone - Focus.ogg")
        mixer.music.play(-1)
        running = True
        clock = pygame.time.Clock()

        while running:
            self.player.save_location()
            self.handle_input()
            self.update()
            self.group.center(self.player.rect.center)
            self.group.draw(self.screen)
            self.screen.blit(self.pixel_verdana.render("Trésor de Klah " + self.version, False, (0, 0, 0)), (5, 0))
            self.screen.blit(self.pixel_verdana.render(f"Last action: {self.last_action}", False, (0, 0, 0)), (5, 25))
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
                    self.screen = pygame.display.set_mode((width, height), locals.RESIZABLE)
                    self.map_layer.set_size(self.screen.get_size())

            clock.tick(self.FPS)

        pygame.quit()
