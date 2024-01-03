import pygame
import os
import random

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
FLOOR_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
BIRD_IMG = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

pygame.font.init()
FONT_SCORE = pygame.font.SysFont('Arial', 50)

class Bird:
    IMGS = BIRD_IMG

    # Rotação
    MAX_ROT = 25
    SPEED_ROT = 20
    TIME_ANIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.img_cont = 0
        self.image = self.IMGS[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        self.time += 1
        deslc = 1.5 * (self.time ** 2) + self.speed * self.time # deslocamento

        if deslc > 16: # correção de altura
            deslc = 16
        elif deslc < 0: # correção de impulso
            deslc -= 2

        self.y += deslc 

        if deslc < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROT:
                self.angle = self.MAX_ROT
        elif self.angle > -90:
            self.angle -= self.SPEED_ROT

    def draw(self, screen):
        self.img_cont += 1

        if self.img_cont < self.TIME_ANIME:
            self.image = self.IMGS[0]
        elif self.img_cont < self.TIME_ANIME * 2:
            self.image = self.IMGS[1]
        elif self.img_cont < self.TIME_ANIME * 3:
            self.image = self.IMGS[2]
        elif self.img_cont < self.TIME_ANIME * 4:
            self.image = self.IMGS[1]
        elif self.img_cont < self.TIME_ANIME * 4+1:
            self.image = self.IMGS[0]
            self.img_cont = 0
        
        if self.angle <= -80:
            self.image = self.IMGS[1]
            self.img_cont = self.TIME_ANIME * 2

        img_rotate = pygame.transform.rotate(self.image, self.angle)
        img_center = self.image.get_rect(topleft=(self.x, self.y)).center
        bird_rect = img_rotate.get_rect(center=img_center)
        screen.blit(img_rotate, bird_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    DIST = 200 # distância entre um cano e outro
    SPEED_PIPE = 5 

    def __init__(self, x):
        self.x = x
        self.width = 0
        self.pos_top = 0
        self.pos_base = 0
        self.PIPE_TOP = PIPE_IMG
        self.PIPE_BASE = pygame.transform.flip(PIPE_IMG, False, True)
        self.passed = False # passáro passou do cano
        self.define_width()

    def define_width(self):
        self.width = random.randrange(50, 450)
        self.pos_base = self.width - self.PIPE_TOP.get_height()
        self.pos_top = self.width + self.DIST
    
    def move(self):
        self.x -= self.SPEED_PIPE

    def draw(self, screen):
        screen.blit(self.PIPE_TOP, (self.x, self.pos_top))
        screen.blit(self.PIPE_BASE, (self.x , self.pos_base))

    def collision(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        base_mask = pygame.mask.from_surface(self.PIPE_BASE)

        dist_top = (self.x - bird.x, round(self.pos_top) - round(bird.y))
        dist_base = (self.x - bird.x, round(self.pos_base) - round(bird.y))

        base_point = bird_mask.overlap(base_mask, dist_base)
        top_point = bird_mask.overlap(top_mask, dist_top)

        if base_point or top_point:
            return True
        else:
            return False
        

class Floor:
    SPEED_FLOOR = 5
    WIDTH = FLOOR_IMG.get_width()
    IMAGE = FLOOR_IMG

    def __init__(self, y):
        self.y = y
        self.x0 = 0
        self.x1 = self.WIDTH

    def move(self):
        self.x0 -= self.SPEED_FLOOR
        self.x1 -= self.SPEED_FLOOR

        if self.x0 + self.WIDTH < 0:
            self.x0 = self.x1 + self.WIDTH
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x0 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMAGE, (self.x0, self.y))
        screen.blit(self.IMAGE, (self.x1, self.y))


def draw_screen(screen, bird, pipes, floor, score):
    screen.blit(BG_IMG, (0, 0))
    bird.draw(screen)
    floor.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)
    
    text_score = FONT_SCORE.render(f"Score: {score}", 1, (255, 255, 255))
    screen.blit(text_score, (SCREEN_WIDTH - 10 - text_score.get_width(), 10))
    
    pygame.display.update()


def main():
    bird = Bird(230, 350)
    floor = Floor(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    score = 0
    clock = pygame.time.Clock()

    pygame.mixer.init()
    score_effect = pygame.mixer.Sound('sound/score_sound.wav')
    hit_effect = pygame.mixer.Sound('sound/hit_sound.mp3')

    run = True
    while run:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                if event.key == pygame.K_SPACE:
                    bird.jump()

        bird.move()
        floor.move()

        add_pipe = False
        remove_pipe = []
        for pipe in pipes:
            if pipe.collision(bird): # jogador perde
                score = 0
                hit_effect.play()
                # run = False 

            if not pipe.passed and bird.x > pipe.x:
                pipe.passed = True
                add_pipe = True
            
            pipe.move()
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_pipe.append(pipe)

        if add_pipe: # adiciona um cano e conta um ponto para o jogador
            score += 1
            score_effect.play()
            pipes.append(Pipe(600))
         
        for pipe in remove_pipe:
            pipes.remove(pipe)

        if (bird.y + bird.image.get_height()) > floor.y or bird.y < 0: # jogador perde
            score = 0
            hit_effect.play()
            # run = False

        draw_screen(screen, bird, pipes, floor, score)


if __name__ == '__main__':
    main()