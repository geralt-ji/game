import pygame

class Bird:
    def __init__(self, x, y, scale_factor):
        self.original_x = x
        self.original_y = y
        self.scale_factor = scale_factor
        self.x = x * scale_factor
        self.y = y  # 直接使用传入的 y 值，不进行缩放
        self.velocity = 0
        self.gravity = 0.35 * scale_factor
        self.jump_strength = -5.6 * scale_factor
        self.original_size = (30, 30)
        self.size = (int(self.original_size[0] * scale_factor), int(self.original_size[1] * scale_factor))
        self.image = pygame.Surface(self.size)
        self.image.fill((255, 255, 0))  # 黄色方块代表小鸟
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def jump(self):
        self.velocity = self.jump_strength

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def resize(self, scale_factor):
        self.scale_factor = scale_factor
        self.x = self.original_x * scale_factor
        # 保持 y 坐标不变，确保小鸟保持在屏幕中间
        self.size = (int(self.original_size[0] * scale_factor), int(self.original_size[1] * scale_factor))
        self.image = pygame.Surface(self.size)
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.gravity = 0.35 * scale_factor
        self.jump_strength = -5.6 * scale_factor