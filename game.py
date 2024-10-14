import pygame
import random
from bird import Bird
from pipe import Pipe

class Game:
    def __init__(self, width, height):
        self.original_width = 288  # 原始游戏宽度
        self.original_height = 512  # 原始游戏高度
        self.width = width
        self.height = height
        self.scale_factor = min(width / self.original_width, height / self.original_height)
        
        self.score = 0  # 将score的初始化移到这里
        self.bird = Bird(50, self.height // 2, self.scale_factor)
        self.pipes = []  # 初始化为空列表
        self.pipe_spawn_timer = 0
        self.PIPE_SPAWN_INTERVAL = int(75 * self.scale_factor)
        self.font = pygame.font.Font(None, int(36 * self.scale_factor))
        self.game_state = "START"
        self.paused = False

        self.background = pygame.Surface((width, height))
        self.background.fill((135, 206, 235))  # 天蓝色

        self.ground_height = int(100 * self.scale_factor)
        self.ground = pygame.Surface((width, self.ground_height))
        self.ground.fill((222, 184, 135))  # 浅棕色
        self.ground_scroll = 0
        self.GROUND_SCROLL_SPEED = 2 * self.scale_factor

        # 添加暂停按钮
        self.pause_button_size = int(30 * self.scale_factor)
        self.pause_button = pygame.Rect(10, 10, self.pause_button_size, self.pause_button_size)
        self.pause_button_color = (255, 0, 0)  # 红色

        self.initial_gap_size = int(100 * self.scale_factor)  # 初始间隙大小
        self.max_gap_size = int(130 * self.scale_factor)  # 最大间隙大小
        self.gap_size_increment = int(1 * self.scale_factor)  # 每次增加的间隙大小

        self.level = 1
        self.pipes_per_level = 1  # 每个关卡的管道数量
        self.pipes_passed = 0
        self.max_gap_size = int(150 * self.scale_factor)
        self.min_gap_size = int(100 * self.scale_factor)
        self.current_gap_size = self.max_gap_size

        self.level_gap = int(150 * self.scale_factor)  # 减少关卡之间的间隔
        self.pipe_distance = int(300 * self.scale_factor)  # 管道之间的固定距离
        self.pipes_on_screen = 3  # 屏幕上同时显示的管道数量
        self.next_pipe_x = width + 100  # 初始化 next_pipe_x

        # 初始化管道
        self.pipes = []
        for _ in range(self.pipes_on_screen):
            self.pipes.append(self.create_pipe())

        # 添加无敌模式相关属性
        self.invincible = False
        self.invincible_button_size = int(50 * self.scale_factor)
        self.invincible_button = pygame.Rect(10, height - self.invincible_button_size - 10, 
                                             self.invincible_button_size, self.invincible_button_size)
        self.invincible_button_color = (255, 165, 0)  # 橙色

        self.pipe_distance = int(300 * self.scale_factor)  # 管道之间的水平距离
        self.pipe_gap = int(150 * self.scale_factor)  # 上下管道之间的垂直间隙
        self.pipe_min_height = int(50 * self.scale_factor)  # 管道的最小高度
        self.pipe_speed = 2 * self.scale_factor  # 管道移动速度

        self.pipes = []
        self.add_pipe()

    def calculate_gap_size(self):
        increment = min(self.score, 30) * self.gap_size_increment
        return min(self.initial_gap_size + increment, self.max_gap_size)

    def create_pipe(self):
        gap_size = self.current_gap_size
        new_pipe = Pipe(self.next_pipe_x, self.height, gap_size, self.height, self.scale_factor)
        self.next_pipe_x += self.pipe_distance
        return new_pipe

    def bird_jump(self):
        if self.game_state == "PLAYING" and not self.paused:
            self.bird.jump()
        elif self.game_state == "START":
            self.game_state = "PLAYING"
            self.reset_game()  # 重置游戏状态，包括创建初始管道

    def update(self):
        if self.game_state == "PLAYING" and not self.paused:
            self.bird.update()
            speed_multiplier = 5 if self.invincible else 1
            self.ground_scroll -= self.GROUND_SCROLL_SPEED * speed_multiplier
            if abs(self.ground_scroll) > self.width:
                self.ground_scroll = 0
            
            for pipe in self.pipes:
                pipe.update(speed_multiplier)  # 传递速度乘数
            
            # 移除屏幕外的管道
            if self.pipes and self.pipes[0].is_off_screen():
                self.pipes.pop(0)
                self.score += 1
                self.add_pipe()

            # 确保始终有足够的管道
            while len(self.pipes) < 3 or self.pipes[-1].x < self.width:
                self.add_pipe()

            if not self.invincible and self.check_collision():
                self.game_state = "START"
                self.reset_game()

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        
        if self.game_state == "START":
            self.draw_start_screen(screen)
        else:
            for pipe in self.pipes:
                pipe.draw(screen)
            self.bird.draw(screen)
            
            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            screen.blit(score_text, (10 + self.pause_button_size + 10, 10))  # 移动分数显示位置
        
        scaled_ground_pos = (self.ground_scroll, self.height - self.ground_height)
        screen.blit(self.ground, scaled_ground_pos)
        screen.blit(self.ground, (self.ground_scroll + self.width, self.height - self.ground_height))

        # 绘制暂停按钮
        pygame.draw.rect(screen, self.pause_button_color, self.pause_button)

        if self.paused:
            self.draw_pause_screen(screen)

        if self.game_state != "START":
            level_text = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
            screen.blit(level_text, (10, 50))  # 在分数下方显示关卡

        # 绘制无敌模式按钮
        pygame.draw.rect(screen, self.invincible_button_color, self.invincible_button)
        invincible_text = self.font.render("God", True, (255, 255, 255))
        text_rect = invincible_text.get_rect(center=self.invincible_button.center)
        screen.blit(invincible_text, text_rect)

        if self.invincible:
            invincible_status = self.font.render("Invincible Mode ON", True, (255, 165, 0))
            screen.blit(invincible_status, (10, self.height - 40))

        if self.game_state == "PLAYING":
            speed_text = self.font.render(f"Speed: {'5x' if self.invincible else '1x'}", True, (255, 255, 255))
            screen.blit(speed_text, (10, self.height - 80))

    def draw_start_screen(self, screen):
        title_font = pygame.font.Font(None, int(64 * self.scale_factor))
        title_text = title_font.render("Flappy Bird Clone", True, (255, 255, 255))
        start_text = self.font.render("Press SPACE to start", True, (255, 255, 255))
        screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, self.height // 3))
        screen.blit(start_text, (self.width // 2 - start_text.get_width() // 2, self.height // 2))

    def check_collision(self):
        if self.bird.y <= 0 or self.bird.y >= self.height - self.ground_height:
            return True
        
        for pipe in self.pipes:
            if pipe.top_pipe.colliderect(self.bird.rect) or pipe.bottom_pipe.colliderect(self.bird.rect):
                return True
        
        return False

    def reset_game(self):
        self.bird = Bird(50, self.height // 2, self.scale_factor)
        self.pipes = []
        self.add_pipe()
        self.score = 0
        self.level = 1

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.scale_factor = min(width / self.original_width, height / self.original_height)
        self.background = pygame.Surface((width, height))
        self.background.fill((135, 206, 235))  # 天蓝色
        self.ground_height = int(100 * self.scale_factor)
        self.ground = pygame.Surface((width, self.ground_height))
        self.ground.fill((222, 184, 135))  # 浅棕色
        self.font = pygame.font.Font(None, int(36 * self.scale_factor))
        self.GROUND_SCROLL_SPEED = 2 * self.scale_factor
        self.PIPE_SPAWN_INTERVAL = int(75 * self.scale_factor)
        self.bird.resize(self.scale_factor)
        for pipe in self.pipes:
            pipe.resize(self.scale_factor)

        # 调整暂停按钮大小和位置
        self.pause_button_size = int(30 * self.scale_factor)
        self.pause_button = pygame.Rect(10, 10, self.pause_button_size, self.pause_button_size)

        # 调整无敌模式按钮大小和位置
        self.invincible_button_size = int(50 * self.scale_factor)
        self.invincible_button = pygame.Rect(10, height - self.invincible_button_size - 10, 
                                             self.invincible_button_size, self.invincible_button_size)

    def draw_pause_screen(self, screen):
        pause_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pause_surface.fill((0, 0, 0, 128))  # 半透明黑色
        screen.blit(pause_surface, (0, 0))
        
        pause_text = self.font.render("PAUSED", True, (255, 255, 255))
        screen.blit(pause_text, (self.width // 2 - pause_text.get_width() // 2, self.height // 2))

    def toggle_pause(self):
        if self.game_state == "PLAYING":
            self.paused = not self.paused
            # 切换暂停按钮颜色
            self.pause_button_color = (0, 255, 0) if self.paused else (255, 0, 0)

    def check_pause_button(self, pos):
        if self.pause_button.collidepoint(pos):
            self.toggle_pause()
            return True
        return False

    def toggle_invincible(self):
        self.invincible = not self.invincible
        self.invincible_button_color = (0, 255, 0) if self.invincible else (255, 165, 0)

    def check_invincible_button(self, pos):
        if self.invincible_button.collidepoint(pos):
            self.toggle_invincible()
            return True
        return False

    def add_pipe(self):
        x = self.width + 100  # 确保新管道在屏幕右侧外生成
        if self.pipes:
            last_pipe = self.pipes[-1]
            x = max(x, last_pipe.x + self.pipe_distance)
        
        top_height = random.randint(self.pipe_min_height, self.height - self.pipe_gap - self.pipe_min_height)
        bottom_height = self.height - top_height - self.pipe_gap
        new_pipe = Pipe(x, top_height, bottom_height, self.pipe_speed, self.scale_factor)
        self.pipes.append(new_pipe)