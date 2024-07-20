from yamb import YambEnv
import numpy as np
import pygame
from numpy.typing import NDArray

def process_text(s: str) -> NDArray[np.int64]:
    num1s, num2s, num3s, num4s, num5s, num6s, announce, announce_row, row_to_fill, col_to_fill = 0,0,0,0,0,0,0,0,0,0
    
    for c in s:
        if c.isnumeric():
            if int(c)==1: num1s += 1
            if int(c)==2: num2s += 1
            if int(c)==3: num3s += 1
            if int(c)==4: num4s += 1
            if int(c)==5: num5s += 1
            if int(c)==6: num6s += 1
        else:
            break
            
    try:
        index_a = s.index("a")
        if s[index_a+1:index_a+3].isnumeric():
            announce_row = int(s[index_a+1:index_a+3])
        else:
            announce_row = int(s[index_a+1:index_a+2])
        announce = 1
    except ValueError as e:
        announce = 0
        announce_row = 0
        
    try:
        index_r = s.index("r")
        if s[index_r+1:index_r+3].isnumeric():
            row_to_fill = int(s[index_r+1:index_r+3])
        else:
            row_to_fill = int(s[index_r+1:index_r+2])
    except ValueError as e:
        row_to_fill = 0
        
    try:
        index_c = s.index("c")
        if s[index_c+1:index_c+3].isnumeric():
            col_to_fill = int(s[index_c+1:index_c+3])
        else:
            col_to_fill = int(s[index_c+1:index_c+2])
    except ValueError as e:
        col_to_fill = 0
    row_col_fill = YambEnv.convert_row_fill_col_fill(row_to_fill, col_to_fill)
    result = np.array([num1s, num2s, num3s, num4s, num5s, num6s, announce, announce_row, row_col_fill])
    return result

if __name__ == "__main__":
    try:
        env = YambEnv()
        env.reset()
        env.render()
        run = True
        input_box = pygame.Rect(env.SCREEN_WIDTH//2, env.SCREEN_HEIGHT//2+100, 250, 40)
        input_box_color = (200, 200, 200)
        text = ""
        text_color = (0, 0, 0)
        font = pygame.freetype.Font(None, 20)
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        observation, reward, terminated, truncated, info = env.step(process_text(text))
                        env.render()
                        print(f"Reward:{reward}")
                        text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

                pygame.draw.rect(env.screen, input_box_color, input_box, 40)
                font.render_to(env.screen, (input_box.x+5, input_box.y+5), text, text_color)
                env.clock.tick(YambEnv.RENDER_FPS)
                pygame.display.flip()

        env.close()
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
    