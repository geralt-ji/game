import pygame

class Pipe:
    def __init__(self, x, top_height, bottom_height, speed, scale_factor):
        self.x = x
        self.top_height = top_height
        self.bottom_height = bottom_height
        self.speed = speed
        self.width = int(52 * scale_factor)
        self.color = (0, 255, 0)  # 绿色
        self.gap = int(150 * scale_factor)  # 添加 gap 属性

        self.top_pipe = pygame.Rect(x, 0, self.width, top_height)
        self.bottom_pipe = pygame.Rect(x, top_height + self.gap, self.width, bottom_height)

        self.base_speed = speed  # 保存基础速度

    def update(self, speed_multiplier=1):
        self.x -= self.base_speed * speed_multiplier
        self.top_pipe.x = self.x
        self.bottom_pipe.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.top_pipe)
        pygame.draw.rect(screen, self.color, self.bottom_pipe)

    def is_off_screen(self):
        return self.x + self.width < 0