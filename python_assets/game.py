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
        self.tmx_data = pytmx.util_pygame.load_pygame("assets/maps/spawn.tmx")
        self.map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(self.map_data, self.screen.get_size())
        self.map_layer.zoom = 2
        self.map = "spawn"

        # générer un joueur
        player_position = self.tmx_data.get_object_by_name("playerspawn")
        self.player = player.Player(player_position.x, player_position.y)
        self.inventory = []

        # liste de collisions
        self.walls = []
        self.coins = []
        self.found_coins = {
            "spawn": [],
            "village": []
        }
        self.apples = []
        self.found_apples = {
            "spawn": [],
            "village": []
        }
        self.dictionaries = []
        self.found_dictionaries = {
            "spawn": [],
            "village": []
        }

        for obj in self.tmx_data.objects:
            if obj.type == "collision":
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            if obj.name == "coin":
                self.coins.append(
                    {
                        "pos": (obj.x, obj.y),
                        "id": obj.id
                    }
                )
            elif obj.name == "apple":
                self.apples.append(
                    {
                        "pos": (obj.x, obj.y),
                        "id": obj.id
                    }
                )
            elif obj.name == "dictionary":
                self.dictionaries.append(
                    {
                        "pos": (obj.x, obj.y),
                        "id": obj.id
                    }
                )

        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=2)
        self.group.add(self.player)
    
    def update(self):
        self.group.update()

        # vérification des collisions
        for sprite in self.group.sprites():
            # objets collisions
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back()
            # ITEMS
            # pièces
            for coin in self.coins:
                if sprite.rect.collidepoint(coin.get("pos")) and not coin.get("id") in self.found_coins.get(self.map):
                    print("vous avez trouvé une pièce !")
                    self.found_coins.get(self.map).append(coin.get("id"))
            # pommes
            for apple in self.apples:
                if sprite.rect.collidepoint(apple.get("pos"))\
                        and not apple.get("id") in self.found_apples.get(self.map):
                    print("vous avez trouvé une pomme !")
                    self.found_apples.get(self.map).append(apple.get("id"))
            # dictionary
            for dictionary in self.dictionaries:
                if sprite.rect.collidepoint(dictionary.get("pos")) \
                        and not dictionary.get("id") in self.found_dictionaries.get(self.map):
                    print("vous avez trouvé le dictionnaire !")
                    self.found_dictionaries.get(self.map).append(dictionary.get("id"))

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
        elif pressed[pygame.K_e]:
            print(self.map)

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
            self.screen.blit(self.pixel_verdana.render("Trésor de Klah " + self.version, False, (0, 0, 0)), (0, 0))
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
