import pygame

class Bird:
    def __init__(self, x, y, scale_factor, image):
        self.image = image
        self.rect = self.image.get_rect()
        
        # 调整中心点，使其更靠前
        self.rect.centerx = x
        self.rect.centery = y
        self.rect.x -= int(self.rect.width * 0.3)  # 将中心点向左移动图像宽度的30%
        
        self.velocity = 0
        self.gravity = 0.5 * scale_factor * 0.5  # 降低重力到原来的50%
        self.jump_strength = -8 * scale_factor * 0.7  # 同样降低跳跃强度到原来的50%

    def update(self):
        self.velocity += self.gravity
        self.rect.y += self.velocity

    def jump(self):
        self.velocity = self.jump_strength

    # 移除 draw 方法，因为我们现在在 Game 类中处理绘制
