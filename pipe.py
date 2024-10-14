import pygame

class Pipe:
    def __init__(self, x, top_height, bottom_height, speed, scale_factor):
        self.x = x
        self.top_height = top_height
        self.bottom_height = bottom_height
        self.speed = speed
        self.scale_factor = scale_factor
        self.color = (0, 255, 0)  # 绿色
        self.reward = None
        self.gap = int(150 * scale_factor)  # 添加这行
        self.resize(scale_factor)

    def resize(self, new_scale_factor):
        self.scale_factor = new_scale_factor
        self.width = int(52 * self.scale_factor)
        self.gap = int(150 * self.scale_factor)  # 更新 gap
        self.top_pipe = pygame.Rect(self.x, 0, self.width, self.top_height)
        self.bottom_pipe = pygame.Rect(self.x, self.top_height + self.gap, self.width, self.bottom_height)
        self.base_speed = self.speed * (new_scale_factor / self.scale_factor)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.top_pipe)
        pygame.draw.rect(screen, self.color, self.bottom_pipe)

    def update(self, game_speed):
        self.x -= self.speed * game_speed
        self.top_pipe.x = self.x
        self.bottom_pipe.x = self.x

    def is_off_screen(self):
        return self.x + self.width < 0
