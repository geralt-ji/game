import pygame
import random
from bird import Bird
from pipe import Pipe
from PIL import Image, ImageSequence
import io

class Game:
    def __init__(self, width, height):
        self.original_width = 288  # 原始游戏宽度
        self.original_height = 512  # 原始游戏高度
        self.width = width
        self.height = height
        self.scale_factor = min(width / self.original_width, height / self.original_height)
        
        # 加载小鸟 GIF
        self.bird_frames = self.load_gif_frames(r'C:\Users\Wen Ji\Desktop\work\game\Images\Gif previews\Bird-A.gif')
        self.bird_frame_index = 0
        self.bird_animation_speed = 0.2  # 增加动画速度

        # 调整小鸟的初始位置
        bird_start_x = int(self.width * 0.2)  # 将小鸟放在屏幕宽度的20%处
        self.bird = Bird(bird_start_x, self.height // 2, self.scale_factor, self.bird_frames[0])
        
        # 添加这行，确保它在任何可能使用它的方法之前定义
        self.pipe_min_height = int(50 * self.scale_factor)
        
        # 添加这行来定义 pipe_speed
        self.pipe_speed = 2 * self.scale_factor
        
        self.score = 0  # 将score的初始化移到这里
        self.pipes = []  # 初始化为列表
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
        self.invincible_timer = 0  # 添加这行
        self.invincible_duration = 5 * 60  # 5秒 * 60帧/秒

        self.pipe_gap = int(150 * self.scale_factor)  # 上下管道之间的垂直间隙
        self.pipe_speed = 2 * self.scale_factor  # 管道移动速度

        self.pipes = []
        self.add_pipe()

        # 添加速度调整按钮
        self.speed_button_size = int(50 * self.scale_factor)
        self.speed_button = pygame.Rect(self.width - self.speed_button_size - 10, 10, 
                                    self.speed_button_size, self.speed_button_size)
        self.speed_button_color = (0, 191, 255)  # 深天蓝色
        self.game_speed = 1  # 初始游戏速度

        # 奖励方块相关
        self.reward = None
        self.reward_size = int(30 * self.scale_factor)
        self.reward_spawn_timer = 0
        self.reward_spawn_interval = random.randint(300, 600)  # 5-10秒 (假设60帧/秒)
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 5 * 60  # 5秒无敌时间

    def calculate_gap_size(self):
        increment = min(self.score, 30) * self.gap_size_increment
        return min(self.initial_gap_size + increment, self.max_gap_size)

    def create_pipe(self):
        gap_size = self.current_gap_size
        top_height = random.randint(self.pipe_min_height, self.height - gap_size - self.pipe_min_height)
        bottom_height = self.height - top_height - gap_size
        new_pipe = Pipe(self.next_pipe_x, top_height, bottom_height, self.pipe_speed, self.scale_factor)
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
            speed_multiplier = self.game_speed  # 移除对无敌模式的特殊处理
            self.ground_scroll -= self.GROUND_SCROLL_SPEED * speed_multiplier
            if abs(self.ground_scroll) > self.width:
                self.ground_scroll = 0
            
            for pipe in self.pipes:
                pipe.update(self.game_speed)  # 使用当前游戏速度
            
            # 移除屏幕外的管道
            if self.pipes and self.pipes[0].is_off_screen():
                self.pipes.pop(0)
                self.score += 1
                # 检查是否需要增加关卡
                if self.score % 3 == 0:
                    self.level += 1
                    # 每当关卡增加时，自动增加游戏速度
                    self.adjust_speed(increase=True)
                self.add_pipe()

            # 确保始终有足够的管道
            while len(self.pipes) < 3 or self.pipes[-1].x < self.width:
                self.add_pipe()

            if not self.invincible and self.check_collision():
                self.game_state = "START"
                self.reset_game()

            # 更新奖励方块
            if self.reward:
                self.reward.x -= self.pipe_speed * self.game_speed
                if self.bird.rect.colliderect(self.reward):
                    self.invincible = True
                    self.invincible_timer = self.invincible_duration
                    self.reward = None
                elif self.reward.right < 0:
                    self.reward = None

            # 生成新的奖励方块
            self.reward_spawn_timer += 1
            if self.reward_spawn_timer >= self.reward_spawn_interval and not self.reward:
                self.spawn_reward()
                self.reward_spawn_timer = 0
                self.reward_spawn_interval = random.randint(300, 600)

            # 更新无敌状态
            if self.invincible:
                self.invincible_timer -= 1
                if self.invincible_timer <= 0:
                    self.invincible = False

            # 更新小鸟动画
            self.bird_frame_index = (self.bird_frame_index + self.bird_animation_speed) % len(self.bird_frames)
            self.bird.image = self.bird_frames[int(self.bird_frame_index)]

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        
        if self.game_state == "START":
            self.draw_start_screen(screen)
        else:
            for pipe in self.pipes:
                pipe.draw(screen)
            
            # 绘制小鸟，如果无敌则改变颜色
            if self.invincible:
                self.bird.color = (255, 0, 0)  # 无敌时为红色
            else:
                self.bird.color = (255, 255, 0)  # 普通模式为黄色
            screen.blit(self.bird.image, self.bird.rect)
            
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
            speed_text = self.font.render(f"Speed: {self.game_speed:.1f}x", True, (255, 255, 255))
            screen.blit(speed_text, (10, self.height - 80))

        # 绘制速度调整按钮
        pygame.draw.rect(screen, self.speed_button_color, self.speed_button)
        speed_text = self.font.render(f"Speed: {self.game_speed:.1f}x", True, (255, 255, 255))
        text_rect = speed_text.get_rect(center=self.speed_button.center)
        screen.blit(speed_text, text_rect)

        # 绘制奖励方块
        if self.reward:
            pygame.draw.rect(screen, (255, 215, 0), self.reward)  # 金色

        # 显示下一个奖励到来时间
        next_reward_time = (self.reward_spawn_interval - self.reward_spawn_timer) // 60  # 转换为秒
        next_reward_text = self.font.render(f"Next Reward: {next_reward_time}s", True, (255, 255, 255))
        screen.blit(next_reward_text, (self.width - next_reward_text.get_width() - 10, 10))

        # 绘制无敌状态倒计时
        if self.invincible and self.invincible_timer > 0:
            remaining_time = (self.invincible_timer + 59) // 60  # 向上取整，确保从5开始
            countdown_text = self.font.render(f"Invincible: {remaining_time}s", True, (255, 0, 0))
            text_rect = countdown_text.get_rect(center=(self.width // 2, self.height - 50))
            screen.blit(countdown_text, text_rect)

    def draw_start_screen(self, screen):
        title_font = pygame.font.Font(None, int(64 * self.scale_factor))
        title_text = title_font.render("Flappy Bird Clone", True, (255, 255, 255))
        start_text = self.font.render("Press SPACE to start", True, (255, 255, 255))
        screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, self.height // 3))
        screen.blit(start_text, (self.width // 2 - start_text.get_width() // 2, self.height // 2))

    def check_collision(self):
        if self.bird.rect.top <= 0 or self.bird.rect.bottom >= self.height - self.ground_height:
            return True
        
        for pipe in self.pipes:
            if pipe.top_pipe and pipe.top_pipe.colliderect(self.bird.rect):
                return True
            if pipe.bottom_pipe and pipe.bottom_pipe.colliderect(self.bird.rect):
                return True
        
        return False

    def reset_game(self):
        bird_start_x = int(self.width * 0.2)
        self.bird = Bird(bird_start_x, self.height // 2, self.scale_factor, self.bird_frames[0])
        self.pipes = []
        self.add_pipe()
        self.score = 0
        self.level = 1  # 确保关卡重置为1
        self.game_speed = 1  # 重置游戏速度为初始值
        self.reward = None
        self.reward_spawn_timer = 0
        self.invincible = False
        self.invincible_timer = 0

    def resize(self, width, height):
        old_scale_factor = self.scale_factor
        self.width = width
        self.height = height
        self.scale_factor = min(width / self.original_width, height / self.original_height)
        scale_ratio = self.scale_factor / old_scale_factor

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

        # 调整管道的位置
        for pipe in self.pipes:
            pipe.x *= scale_ratio
            pipe.top_pipe.x = pipe.x
            pipe.bottom_pipe.x = pipe.x
            pipe.top_pipe.height = int(pipe.top_pipe.height * scale_ratio)
            pipe.bottom_pipe.y = int(pipe.bottom_pipe.y * scale_ratio)
            pipe.bottom_pipe.height = int(pipe.bottom_pipe.height * scale_ratio)

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
        if self.invincible:
            self.invincible_timer = self.invincible_duration
        else:
            self.invincible_timer = 0

    def check_invincible_button(self, pos):
        if self.invincible_button.collidepoint(pos):
            self.toggle_invincible()
            return True
        return False

    def add_pipe(self):
        # 设置地面和空中的比例
        ground_height = self.ground_height
        sky_height = self.height - ground_height

        # 设置空中部分的比例
        gap_height = int(sky_height * 0.3)  # 空隙占中部分的30%
        min_pipe_height = int(sky_height * 0.1)  # 最小管道高度

        # 随机设置上方管道的高度
        top_height = random.randint(min_pipe_height, sky_height - gap_height - min_pipe_height)
        
        # 计算下方管道的高度
        bottom_height = sky_height - top_height - gap_height

        # 设置管道的位置
        x = self.width + 100  # 确保新管道在屏幕右侧外生成
        if self.pipes:
            last_pipe = self.pipes[-1]
            x = max(x, last_pipe.x + self.pipe_distance)

        # 创建新的Pipe对象
        new_pipe = Pipe(x, top_height, bottom_height, self.pipe_speed, self.scale_factor)
        
        # 调整下方管道的y坐标，使其从空隙底部开始
        new_pipe.bottom_pipe.y = self.height - ground_height - bottom_height

        self.pipes.append(new_pipe)

    def adjust_speed(self, increase=True):
        if increase:
            self.game_speed = min(self.game_speed + 0.2, 5)  # 最大速度为5，每次增加0.2
        else:
            self.game_speed = max(self.game_speed - 0.2, 0.5)  # 最小速度为0.5，每次减少0.2

    def check_speed_button(self, pos):
        if self.speed_button.collidepoint(pos):
            # 左键点击增加速度，右键点击减少速度
            if pygame.mouse.get_pressed()[0]:  # 左键
                self.adjust_speed(increase=True)
            elif pygame.mouse.get_pressed()[2]:  # 右键
                self.adjust_speed(increase=False)
            return True
        return False

    def spawn_reward(self):
        # 找到屏幕外的第一个管道
        screen_right_edge = self.width
        pipe_outside_screen = next((pipe for pipe in self.pipes if pipe.x > screen_right_edge), None)
        
        if pipe_outside_screen:
            gap_top = pipe_outside_screen.top_pipe.bottom
            gap_bottom = pipe_outside_screen.bottom_pipe.top
            reward_y = random.randint(gap_top + self.reward_size, gap_bottom - self.reward_size)
            self.reward = pygame.Rect(pipe_outside_screen.x + pipe_outside_screen.width / 2 - self.reward_size / 2, 
                                      reward_y - self.reward_size / 2, 
                                      self.reward_size, self.reward_size)

    def load_gif_frames(self, gif_path):
        frames = []
        with Image.open(gif_path) as gif:
            for frame in ImageSequence.Iterator(gif):
                # 将 PIL Image 转换为 Pygame surface
                frame = frame.convert('RGBA')
                frame_data = frame.tobytes()
                size = frame.size
                mode = frame.mode
                py_image = pygame.image.fromstring(frame_data, size, mode).convert_alpha()
                
                # 缩放图像
                scaled_size = (int(size[0] * 0.5 * self.scale_factor), int(size[1] * 0.5 * self.scale_factor))
                scaled_image = pygame.transform.scale(py_image, scaled_size)
                
                frames.append(scaled_image)
        return frames