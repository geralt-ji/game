import sys
import os
import pygame
from game import Game

# 将当前目录添加到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 初始化Pygame
pygame.init()

# 设置初始窗口大小
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Flappy Bird Clone")

# 设置游戏图标
icon_path = os.path.join(current_dir, 'assets', 'flappy_bird_icon.png')
if os.path.exists(icon_path):
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)
else:
    print("Warning: Icon file not found. Using default icon.")

# 创建游戏对象
game = Game(WINDOW_WIDTH, WINDOW_HEIGHT)

# 主游戏循环
def main():
    global screen  # 声明 screen 为全局变量
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.bird_jump()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_p:
                    game.toggle_pause()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    if not game.check_pause_button(event.pos) and not game.check_invincible_button(event.pos):
                        game.bird_jump()
            if event.type == pygame.VIDEORESIZE:
                WINDOW_WIDTH, WINDOW_HEIGHT = event.size
                screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
                game.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # 更新游戏状态
        game.update()
        
        # 绘制游戏
        game.draw(screen)
        pygame.display.flip()
        
        # 控制帧率
        clock.tick(60)

if __name__ == "__main__":
    main()