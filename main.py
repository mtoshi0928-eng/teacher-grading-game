import asyncio
import pygame
import sys
import random
import math

# 1. 初期設定
pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 650
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("教員汚字採点")
clock = pygame.time.Clock()

# --- 固定サーフェスの事前生成（毎フレーム生成を防止） ---
STUDENT_SHEET_RECT = pygame.Rect(8, 135, 500, 350)
MODEL_SHEET_RECT   = pygame.Rect(516, 135, 500, 350)
UNMARKED_STACK_RECT = pygame.Rect(-40, 480, 180, 180)  
MARKED_STACK_RECT   = pygame.Rect(860, 480, 180, 180)  

student_sheet = pygame.Surface((STUDENT_SHEET_RECT.width, STUDENT_SHEET_RECT.height))
model_sheet   = pygame.Surface((MODEL_SHEET_RECT.width, MODEL_SHEET_RECT.height))
rev_student_sheet = pygame.Surface((STUDENT_SHEET_RECT.width, STUDENT_SHEET_RECT.height))
rev_model_sheet   = pygame.Surface((MODEL_SHEET_RECT.width, MODEL_SHEET_RECT.height))
title_shade = pygame.Surface((SCREEN_WIDTH, 160), pygame.SRCALPHA)
guide_box = pygame.Surface((640, 140), pygame.SRCALPHA)
top_bar_shade = pygame.Surface((SCREEN_WIDTH, 115), pygame.SRCALPHA)
panel = pygame.Surface((924, 570), pygame.SRCALPHA)

# --- フォントの設定 ---
def get_safe_font(size):
    for font_file in ["NotoSansJP-Regular.ttf", "font.ttf", "meiryo.ttc"]:
        try:
            return pygame.font.Font(font_file, size)
        except:
            pass
    system_fonts = ["msgothic", "meiryo", "yumincho", "notosanscjkjp"]
    for f_name in system_fonts:
        try:
            f = pygame.font.SysFont(f_name, size)
            if f.render("あ", True, (0, 0, 0)).get_width() > 0:
                return f
        except:
            pass
    return pygame.font.Font(None, size)

font_sub = get_safe_font(14)
font_main = get_safe_font(30)
font_ui = get_safe_font(26)
font_alert = get_safe_font(24)
font_timer_warn = get_safe_font(32)
font_gameover = get_safe_font(48)

# --- 2. 各種アセットの読み込み ---
maru_images = []
cross_images = []
for i in range(1, 11):
    try:
        img_m = pygame.image.load(f"maru_toumei{i}.png").convert_alpha()
        maru_images.append(pygame.transform.scale(img_m, (80, 80)))
    except:
        pass
    try:
        img_c = pygame.image.load(f"batsu_toumei{i}.png").convert_alpha()
        cross_images.append(pygame.transform.scale(img_c, (80, 80)))
    except:
        pass

try:
    chime_sound = pygame.mixer.Sound("Japanese_School_Bell02-02(Slow-Mid).ogg")
except:
    try:
        chime_sound = pygame.mixer.Sound("Japanese_School_Bell02-02_Slow-Mid_.ogg")
    except:
        chime_sound = None

try:
    se_btn_hover = pygame.mixer.Sound("cursor_move_se.ogg")
    se_btn_start = pygame.mixer.Sound("start_btn_se.ogg")
    se_btn_score_view = pygame.mixer.Sound("saiten_se.ogg")
    se_btn_hover.set_volume(0.3)
    se_btn_start.set_volume(0.5)
    se_btn_score_view.set_volume(0.5)
except:
    se_btn_hover = se_btn_start = se_btn_score_view = None

maru_sounds = []
batsu_sounds = []
for i in range(1, 4):
    try:
        maru_sounds.append(pygame.mixer.Sound(f"maru_se_{i}.ogg"))
    except:
        try:
            maru_sounds.append(pygame.mixer.Sound(f"maru_se_{i}.wav"))
        except:
            pass
    try:
        batsu_sounds.append(pygame.mixer.Sound(f"batsu_se_{i}.ogg"))
    except:
        try:
            batsu_sounds.append(pygame.mixer.Sound(f"batsu_se_{i}.wav"))
        except:
            pass

try:
    bg_image = pygame.image.load("kyouin_tsukue6_hiru.png").convert()
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    bg_image = None

try:
    img_unmarked = pygame.image.load("misaiten1_touka.png").convert_alpha()
    img_unmarked = pygame.transform.scale(img_unmarked, (180, 180))
except:
    img_unmarked = None

try:
    img_marked = pygame.image.load("saitenzumi2_touka.png").convert_alpha()
    img_marked = pygame.transform.scale(img_marked, (180, 180))
except:
    img_marked = None

otsubone_sheets = {}
for grade in range(1, 7):
    try:
        raw_img = pygame.image.load(f"otsubone{grade}nen_haikeitouka.png").convert_alpha()
        otsubone_sheets[grade] = pygame.transform.scale(raw_img, (320, 320))
    except:
        otsubone_sheets[grade] = None

try:
    img_title_bg = pygame.image.load("title_haikei_kouho4.png").convert()
    img_title_bg = pygame.transform.scale(img_title_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    img_title_bg = None

try:
    img_result_bg = pygame.image.load("result_haikei_kouho3.png").convert()
    img_result_bg = pygame.transform.scale(img_result_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    img_result_bg = None

SHEET_CONFIGS = [
    {"file": "hk1.jpg",  "wrong": [1, 2, 3, 5, 6, 7, 9, 10]},  
    {"file": "hk2.jpg",  "wrong": [2, 3, 5, 7, 10]},           
    {"file": "hk3.jpg",  "wrong": [1, 3, 4, 5, 6, 7, 9, 10]},  
    {"file": "hk4.jpg",  "wrong": [1, 5, 6]},                 
    {"file": "hk5.jpg",  "wrong": [3, 4, 5, 6, 7, 10]},        
    {"file": "hk6.jpg",  "wrong": [2, 4, 5, 6, 8]},           
    {"file": "hk7.jpg",  "wrong": [1, 6, 7, 8, 10]},          
    {"file": "hk8.jpg",  "wrong": [1, 2, 4]},                 
    {"file": "hk9.jpg",  "wrong": [2, 3, 6, 8, 9]},           
    {"file": "hk10.jpg", "wrong": [2, 3, 5, 7, 9]},
    {"file": "hk11.jpg", "wrong": [4, 5, 6, 7, 10]}            
]

student_sheets_images = {}
for cfg in SHEET_CONFIGS:
    try:
        img_raw = pygame.image.load(cfg["file"]).convert()
        student_sheets_images[cfg["file"]] = pygame.transform.scale(img_raw, (500, 350))
    except:
        student_sheets_images[cfg["file"]] = None

# --- 3. 状態管理変数 ---
game_state = "TITLE"
global_score = 0
current_stage = 1            
sheet_completed = False
global_timer = 60.0          
stage_timer = 0.0            

is_otsubone_active = False  
otsubone_triggered = False   
speech_bubbles = []          

current_img = None
current_mode = None
anim_progress = 0.0
is_animating = False
ANIM_SPEED = 1.0 / 12  

was_hovering_title_start  = False
was_hovering_result_miss   = False
was_hovering_result_back   = False

all_sheets_time = []        
all_sheets_penalties = []   
current_sheet_penalty = 0   

total_sheets_marked = 0
total_miss_count = 0
has_missed_in_game = [False] * 10  
show_wrong_matrix = False   

history_marked_sheets = []  
review_current_idx = 0     

STUDENT_NAMES = [
    "山田 まるお", "佐藤 さくら", "鈴木 たかし", "田中 つばさ", 
    "高橋 めぐみ", "渡辺 けんた", "伊藤 ひなた", "中村 ゆい"
]
current_student_name = random.choice(STUDENT_NAMES)
current_sheet_file = "hk1.jpg" 

answer_boxes = {}
for i in range(5):
    answer_boxes[i] = pygame.Rect(326 - i * 76, 31, 76, 148)
    answer_boxes[5 + i] = pygame.Rect(326 - i * 76, 179, 76, 148)

prob_order = list(range(10)) 
current_order_idx = 0
current_prob_idx = prob_order[current_order_idx]

title_start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 190, 440, 380, 65)
result_view_miss_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 240, 450, 480, 55)
result_back_to_stat_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 545, 240, 50)

# WebAssembly用に stop() へ変更
def play_scene_bgm(scene_name):
    try:
        pygame.mixer.music.stop()
        if scene_name in ["TITLE", "RESULT"]:
            pygame.mixer.music.load("title_result_bgm.ogg") 
            pygame.mixer.music.set_volume(0.4)       
            pygame.mixer.music.play(-1)              
        elif scene_name == "PLAY":
            pygame.mixer.music.load("play_haikei_bgm.ogg")  
            pygame.mixer.music.set_volume(0.12)      
            pygame.mixer.music.play(-1)
    except:
        pass

def generate_kanji_dataset_for_sheet(wrong_list):
    base_data = [
        {"num": "1",  "model_ans": "あお"},
        {"num": "2",  "model_ans": "あか"},
        {"num": "3",  "model_ans": "しろ"},
        {"num": "4",  "model_ans": "くろ"},
        {"num": "5",  "model_ans": "みどり"},
        {"num": "6",  "model_ans": "おれんじ"},
        {"num": "7",  "model_ans": "ちゃいろ"},
        {"num": "8",  "model_ans": "ぴんく"},
        {"num": "9",  "model_ans": "むらさき"},
        {"num": "10", "model_ans": "きいろ"}
    ]
    for item in base_data:
        num_int = int(item["num"])
        item["correct"] = "BATSU" if num_int in wrong_list else "MARU"
    return base_data

sheet_stamps = [None] * 10
current_dataset = generate_kanji_dataset_for_sheet([])
scoring_results = [None] * 10
erased_marks = [False] * 10
current_sheet_miss_flags = [False] * 10 

def start_new_game():
    global global_score, current_stage, total_sheets_marked, total_miss_count, global_timer, stage_timer
    global otsubone_triggered, is_otsubone_active, current_dataset, scoring_results, erased_marks, current_order_idx, current_prob_idx, current_student_name, game_state, has_missed_in_game, show_wrong_matrix
    global all_sheets_time, all_sheets_penalties, current_sheet_penalty, current_sheet_file, sheet_stamps
    global is_animating, anim_progress, current_img, current_mode, history_marked_sheets, review_current_idx, current_sheet_miss_flags
    
    global_score = 0
    current_stage = 1
    total_sheets_marked = 0
    total_miss_count = 0
    global_timer = 60.0     
    stage_timer = 0.0  
    current_sheet_penalty = 0
    all_sheets_time = []
    all_sheets_penalties = []
    history_marked_sheets = [] 
    review_current_idx = 0
    current_sheet_miss_flags = [False] * 10
    otsubone_triggered = False
    is_otsubone_active = False
    show_wrong_matrix = False
    has_missed_in_game = [False] * 10  
    sheet_stamps = [None] * 10
    
    is_animating = False
    anim_progress = 0.0
    current_img = None
    current_mode = None
    
    chosen_cfg = random.choice(SHEET_CONFIGS)
    current_sheet_file = chosen_cfg["file"]
    current_dataset = generate_kanji_dataset_for_sheet(chosen_cfg["wrong"])
    
    scoring_results = [None] * 10
    erased_marks = [False] * 10
    current_order_idx = 0
    current_prob_idx = prob_order[current_order_idx]
    current_student_name = random.choice(STUDENT_NAMES)
    
    play_scene_bgm("PLAY") 
    game_state = "PLAY"

def get_maru_mask(size, progress):
    mask = pygame.Surface(size, pygame.SRCALPHA)
    center = (size[0] // 2, size[1] // 2)
    radius = max(size)
    if progress >= 1.0: 
        mask.fill((255, 255, 255, 255))
        return mask
    points = [center]
    start_angle_deg = 135
    total_span_deg = 360 * progress
    step = 10
    while step <= total_span_deg:
        angle_rad = math.radians(start_angle_deg + step)
        points.append((center[0] + radius * math.cos(angle_rad), center[1] + radius * math.sin(angle_rad)))
        step += 10
    pygame.draw.polygon(mask, (255, 255, 255, 255), points)
    return mask

def get_cross_mask(size, progress):
    mask = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size
    if progress <= 0.5:
        pygame.draw.polygon(mask, (255, 255, 255, 255), [(0, 0), (w * progress * 2, 0), (w * progress * 2, h * progress * 2), (0, h * progress * 2)])
    else:
        pygame.draw.polygon(mask, (255, 255, 255, 255), [(0, 0), (w, 0), (w, h), (0, h)])
        t = (progress - 0.5) * 2
        if t < 1.0:
            erase = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.polygon(erase, (0, 0, 0, 255), [(0, h), (0, h * t), (w * (1 - t), h), (0, h)])
            mask.blit(erase, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return mask

# =================================================================
# 非同期メインループ
# =================================================================
async def main():
    global game_state, global_timer, stage_timer, is_otsubone_active, otsubone_triggered, speech_bubbles
    global current_img, current_mode, anim_progress, is_animating
    global was_hovering_title_start, was_hovering_result_miss, was_hovering_result_back
    global all_sheets_time, all_sheets_penalties, current_sheet_penalty, total_sheets_marked, total_miss_count
    global has_missed_in_game, show_wrong_matrix, history_marked_sheets, review_current_idx
    global current_student_name, current_sheet_file, current_dataset, scoring_results, erased_marks
    global current_sheet_miss_flags, sheet_stamps, current_order_idx, current_prob_idx, sheet_completed, current_stage, global_score

    play_scene_bgm("TITLE")

    while True:
        delta_time = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        if game_state == "TITLE":
            if title_start_button_rect.collidepoint(mouse_pos):
                if not was_hovering_title_start:
                    if se_btn_hover: se_btn_hover.play() 
                    was_hovering_title_start = True
            else: was_hovering_title_start = False

        elif game_state == "RESULT":
            if not show_wrong_matrix:
                if result_view_miss_btn_rect.collidepoint(mouse_pos):
                    if not was_hovering_result_miss:
                        if se_btn_hover: se_btn_hover.play() 
                        was_hovering_result_miss = True
                else: was_hovering_result_miss = False
            else:
                if result_back_to_stat_btn_rect.collidepoint(mouse_pos):
                    if not was_hovering_result_back:
                        if se_btn_hover: se_btn_hover.play() 
                        was_hovering_result_back = True
                else: was_hovering_result_back = False

        # --- ① TITLE ---
        if game_state == "TITLE":
            if img_title_bg: screen.blit(img_title_bg, (0, 0))
            else: screen.fill((50, 60, 70)) 
                
            title_shade.fill((0, 0, 0, 120)) 
            screen.blit(title_shade, (0, 40))
            
            title_lbl = font_gameover.render("教員汚字採点", True, (255, 255, 255))
            sub_lbl = font_ui.render("〜 休み時間の職員室サバイバル 〜", True, (255, 215, 0))
            screen.blit(title_lbl, (SCREEN_WIDTH // 2 - title_lbl.get_width() // 2, 50))
            screen.blit(sub_lbl, (SCREEN_WIDTH // 2 - sub_lbl.get_width() // 2, 115))
            
            guide_y = 230
            guide_box.fill((0, 0, 0, 160))
            screen.blit(guide_box, (SCREEN_WIDTH // 2 - 320, guide_y - 10))
            
            g1 = font_sub.render("● [ ↑ ] キー ＝ 〇 (正解)  /  [ ↓ ] キー ＝ ✖ (不正解)", True, (255, 255, 255))
            g2 = font_sub.render("● [ ← ] ＝ 1問前の問題に戻る / [→] = 1問後の問題に進む", True, (255, 255, 255))
            g3 = font_sub.render("● [ SPACE ] 連打 ＝ お局先生の邪魔マシンガントークを破壊！", True, (255, 230, 230))
            screen.blit(g1, (SCREEN_WIDTH // 2 - g1.get_width() // 2, guide_y))
            screen.blit(g2, (SCREEN_WIDTH // 2 - g2.get_width() // 2, guide_y + 35))
            screen.blit(g3, (SCREEN_WIDTH // 2 - g3.get_width() // 2, guide_y + 70))
            
            pygame.draw.rect(screen, (100, 20, 30), (title_start_button_rect.x, title_start_button_rect.y + 4, title_start_button_rect.width, title_start_button_rect.height), border_radius=10)
            pygame.draw.rect(screen, (210, 40, 60), title_start_button_rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), title_start_button_rect, 2, border_radius=10)
            
            btn_txt = font_ui.render("勤務開始 (Enter)", True, (255, 255, 255))
            screen.blit(btn_txt, (SCREEN_WIDTH // 2 - btn_txt.get_width() // 2, title_start_button_rect.y + title_start_button_rect.height // 2 - btn_txt.get_height() // 2))
            
            pulse_alpha = int(140 + 115 * math.sin(pygame.time.get_ticks() * 0.006))
            tap_lbl = font_timer_warn.render("Tap to start", True, (255, 255, 255))
            tap_surf = tap_lbl.convert_alpha()
            tap_surf.fill((255, 255, 255, pulse_alpha), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(tap_surf, (SCREEN_WIDTH // 2 - tap_lbl.get_width() // 2, title_start_button_rect.y + title_start_button_rect.height + 8))

        # --- ② PLAY ---
        elif game_state == "PLAY":
            global_timer -= delta_time
            if global_timer <= 0.0:
                global_timer = 0.0
                if chime_sound: chime_sound.play()
                play_scene_bgm("RESULT")
                game_state = "RESULT" 

            if not sheet_completed:
                stage_timer += delta_time

            if not is_otsubone_active and not is_animating and not sheet_completed:
                if random.randint(1, 2400) == 777:
                    is_otsubone_active = True
                    speech_bubbles = []
                    bubble_count = 8 + (current_stage * 2) 
                    for _ in range(bubble_count):
                        bx = random.randint(60, 420)
                        by = random.randint(120, 450)
                        br = random.randint(35, 60)
                        speech_bubbles.append((bx, by, br))

            if bg_image: screen.blit(bg_image, (0, 0))
            else: screen.fill((90, 110, 100)) 

            top_bar_shade.fill((0, 0, 0, 140)) 
            screen.blit(top_bar_shade, (0, 0))

            student_sheet.fill((255, 255, 255))
            model_sheet.fill((255, 255, 255)) 

            pygame.draw.rect(model_sheet, (160, 160, 160), (460, 29, 34, 273), 1)   
            pygame.draw.rect(model_sheet, (160, 160, 160), (415, 29, 45, 273), 1)   
            pygame.draw.line(model_sheet, (160, 160, 160), (415, 85), (460, 85), 1)   
            pygame.draw.line(model_sheet, (160, 160, 160), (415, 225), (460, 225), 1) 
            
            title_str = "ひらがなテスト"
            for t_idx, t_char in enumerate(title_str):
                model_sheet.blit(font_sub.render(t_char, True, (120, 120, 120)), (470, 45 + t_idx * 18))
            model_sheet.blit(font_sub.render("番", True, (120, 120, 120)), (430, 52))
            model_sheet.blit(font_sub.render("名前", True, (120, 120, 120)), (423, 145))
            model_sheet.blit(font_sub.render("点", True, (120, 120, 120)), (430, 255))

            active_sheet_img = student_sheets_images.get(current_sheet_file)
            if active_sheet_img: 
                student_sheet.blit(active_sheet_img, (0, 0))
            else: 
                student_sheet.fill((245, 240, 230))

            for idx in range(10): 
                box_rect = answer_boxes[idx]
                prob = current_dataset[idx]
                
                is_current = (idx == current_prob_idx and not sheet_completed)
                box_color = (255, 50, 50) if is_current else (200, 200, 200)
                box_thick = 3 if is_current else 1
                
                pygame.draw.rect(student_sheet, box_color, box_rect, box_thick)
                pygame.draw.rect(model_sheet, (200, 50, 50) if is_current else (160, 160, 160), box_rect, box_thick)
                
                num_str = f"({prob['num']})"
                model_sheet.blit(font_sub.render(num_str, True, (120, 120, 120)), (box_rect.x + 10, box_rect.y - 16))
                
                total_chars = len(prob["model_ans"])
                spacing = (box_rect.height - 20) // total_chars if total_chars > 1 else 38
                start_y_offset = 20 if total_chars > 2 else 32  
                start_x_offset = box_rect.width // 2 - 15       

                for g_idx, g_char in enumerate(prob["model_ans"]):
                    model_sheet.blit(font_main.render(g_char, True, (220, 50, 50)), (box_rect.x + start_x_offset, box_rect.y + start_y_offset + g_idx * spacing))

                if scoring_results[idx] and (not is_animating or idx != current_prob_idx):
                    st_img = sheet_stamps[idx]
                    if st_img:
                        sdx = box_rect.x + box_rect.width // 2 - 40
                        sdy = box_rect.y + box_rect.height // 2 - 40
                        student_sheet.blit(st_img, (sdx, sdy))
                    
                    if erased_marks[idx]:
                        center_x = box_rect.x + box_rect.width // 2
                        pygame.draw.line(student_sheet, (255, 0, 0), (center_x - 4, box_rect.y + 10), (center_x - 4, box_rect.y + box_rect.height - 10), 2)
                        pygame.draw.line(student_sheet, (255, 0, 0), (center_x + 4, box_rect.y + 10), (center_x + 4, box_rect.y + box_rect.height - 10), 2)

            screen.blit(student_sheet, (STUDENT_SHEET_RECT.x, STUDENT_SHEET_RECT.y))
            screen.blit(model_sheet, (MODEL_SHEET_RECT.x, MODEL_SHEET_RECT.y))

            if is_animating and current_img and not is_otsubone_active:
                box = answer_boxes[current_prob_idx]
                dx = STUDENT_SHEET_RECT.x + box.x + box.width // 2 - 40
                dy = STUDENT_SHEET_RECT.y + box.y + box.height // 2 - 40
                mask = get_maru_mask(current_img.get_size(), anim_progress) if current_mode == "MARU" else get_cross_mask(current_img.get_size(), anim_progress)
                disp = current_img.copy()
                disp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                screen.blit(disp, (dx, dy))

            screen.blit(font_ui.render("模範解答（小学 1 年）", True, (255, 255, 255)), (MODEL_SHEET_RECT.x + 15, 105))
            screen.blit(font_ui.render(f"児童答案（{current_student_name} - {current_sheet_file}）", True, (255, 255, 255)), (STUDENT_SHEET_RECT.x + 15, 105))

            if img_unmarked: screen.blit(img_unmarked, (UNMARKED_STACK_RECT.x, UNMARKED_STACK_RECT.y))
            if img_marked: screen.blit(img_marked, (MARKED_STACK_RECT.x, MARKED_STACK_RECT.y))

            screen.blit(font_sub.render(f"現在：小学 {current_stage} 年生", True, (240, 240, 240)), (20, 490))
            screen.blit(font_sub.render(f"採点完了：{total_sheets_marked} 枚", True, (240, 240, 240)), (890, 490))

            if is_otsubone_active:
                for (bx, by, br) in speech_bubbles:
                    pygame.draw.circle(screen, (255, 255, 255), (bx, by), br)
                    pygame.draw.circle(screen, (100, 100, 100), (bx, by), br, 2)
                    screen.blit(font_sub.render("...", True, (150, 150, 150)), (bx - 10, by - 8))
                    
                active_otsubone_img = otsubone_sheets.get(current_stage)
                if active_otsubone_img: screen.blit(active_otsubone_img, (340, 130))

                pygame.draw.rect(screen, (220, 50, 50), (50, 550, 924, 55))
                pygame.draw.rect(screen, (255, 255, 255), (50, 550, 924, 55), 3)
                alert_txt = f"【小学{current_stage}年】お局先生の弾幕トーク！ [SPACE連打]で話を遮れ！ (残り:{len(speech_bubbles)}発)"
                screen.blit(font_alert.render(alert_txt, True, (255, 255, 255)), (70, 565))

            screen.blit(font_ui.render("総スコア: 集計中...", True, (255, 255, 255)), (750, 25))
            g_minutes, g_seconds = int(global_timer // 60), int(global_timer % 60)
            screen.blit(font_ui.render(f"勤務終了まで: {g_minutes:02d}:{g_seconds:02d}", True, (100, 250, 100)), (420, 25))
            screen.blit(font_ui.render(f"処理時間: {stage_timer:.1f} 秒 ⏱️", True, (255, 255, 255)), (30, 25))

            guide_text = "操作: [↑]〇  [↓]×  [←][→]問題移動  [Backspace]ミス訂正(二重線)"
            screen.blit(font_sub.render(guide_text, True, (200, 200, 200)), (30, 75))

            if sheet_completed and not is_otsubone_active:
                pygame.draw.rect(screen, (0, 0, 0, 180), (200, 555, 630, 45))
                screen.blit(font_ui.render("【Enter】で採点を確定して、次の答案用紙へ", True, (255, 215, 0)), (210, 565))

        # --- ③ RESULT ---
        elif game_state == "RESULT":
            if img_result_bg: screen.blit(img_result_bg, (0, 0))
            else: screen.fill((30, 40, 60)) 
            
            panel.fill((0, 0, 0, 150)) 
            screen.blit(panel, (50, 30))
            
            if not show_wrong_matrix:
                res_title = font_gameover.render("クラス全体の採点結果発表", True, (255, 215, 0))
                screen.blit(res_title, (SCREEN_WIDTH // 2 - res_title.get_width() // 2, 50))
                pygame.draw.line(screen, (100, 100, 100), (80, 115), (944, 115), 2)

                sheet_count = len(all_sheets_time)
                base_bonus = sheet_count * 100
                avg_speed = sum(all_sheets_time) / sheet_count if sheet_count > 0 else 0.0
                
                total_speed_bonus = 0
                for t in all_sheets_time:
                    total_speed_bonus += max(0, int((30.0 - t) * 35))
                    
                total_penalty = 10 * total_miss_count * total_miss_count
                global_score = max(0, base_bonus + total_speed_bonus - total_penalty)
                
                data_x = 85
                data_start_y = 140  
                data_pitch = 40
                
                lbl_report_title = font_ui.render("【 放課後の勤務査定レポート 】", True, (255, 230, 150))
                screen.blit(lbl_report_title, (data_x, data_start_y))
                
                r1 = font_sub.render(f"■ 採点枚数ボーナス ： {sheet_count} 枚 × 100点  ➡️  +{base_bonus:,} 点", True, (255, 255, 255))
                r2 = font_sub.render(f"■ 平均採点スピード ： 1枚あたり {avg_speed:.1f} 秒", True, (100, 250, 250))
                r3 = font_sub.render(f"■ 総スピードボーナス： (職人技)  ➡️  +{total_speed_bonus:,} 点", True, (100, 250, 100))
                r4 = font_sub.render(f"■ 総採点ミス数によるペナルティ： {total_miss_count} 回の誤認 ➡️ 【 50 * x * x 】  ➡️  -{total_penalty:,} 点", True, (255, 130, 130))
                
                screen.blit(r1, (data_x + 15, data_start_y + data_pitch))
                screen.blit(r2, (data_x + 15, data_start_y + data_pitch * 2))
                screen.blit(r3, (data_x + 15, data_start_y + data_pitch * 3))
                screen.blit(r4, (data_x + 15, data_start_y + data_pitch * 4.2)) 
                
                pygame.draw.line(screen, (120, 120, 120), (80, 345), (944, 345))
                
                lbl_final_score = font_ui.render(f"🔥 最終教員戦闘力（総スコア）： {global_score:,} 点", True, (255, 255, 255))
                screen.blit(lbl_final_score, (data_x, 365))
                
                if global_score > 2000: rank_letter, rank_name, rank_color = "S", "伝説の校長級", (255, 50, 50)
                elif global_score > 1000: rank_letter, rank_name, rank_color = "A", "敏腕学年主任級", (255, 215, 0)
                elif global_score > 300: rank_letter, rank_name, rank_color = "B", "中堅教諭級", (100, 220, 255)
                else: rank_letter, rank_name, rank_color = "C", "新米臨時教員級", (180, 180, 180)
                    
                lbl_final_rank = font_ui.render(f"👑 最終評価： 【 {rank_letter} ランク 】： {rank_name}", True, rank_color)
                screen.blit(lbl_final_rank, (data_x, 405))
                
                pygame.draw.rect(screen, (20, 40, 80), (result_view_miss_btn_rect.x, result_view_miss_btn_rect.y + 4, result_view_miss_btn_rect.width, result_view_miss_btn_rect.height), border_radius=8)
                pygame.draw.rect(screen, (40, 80, 160), result_view_miss_btn_rect, border_radius=8)
                pygame.draw.rect(screen, (255, 255, 255), result_view_miss_btn_rect, 2, border_radius=8)
                
                btn_txt = font_ui.render("📄 採点結果を1枚ずつ見直す", True, (255, 255, 255))
                screen.blit(btn_txt, (SCREEN_WIDTH // 2 - btn_txt.get_width() // 2, result_view_miss_btn_rect.y + result_view_miss_btn_rect.height // 2 - btn_txt.get_height() // 2 - 2))
                
            else:
                if len(history_marked_sheets) == 0:
                    err_lbl = font_ui.render("採点された答案用紙がありません。", True, (255, 255, 255))
                    screen.blit(err_lbl, (SCREEN_WIDTH // 2 - err_lbl.get_width() // 2, 260))
                else:
                    rev_data = history_marked_sheets[review_current_idx]
                    
                    res_title = font_gameover.render(f"答案見直し： {review_current_idx + 1} / {len(history_marked_sheets)} 枚目", True, (100, 250, 100))
                    screen.blit(res_title, (SCREEN_WIDTH // 2 - res_title.get_width() // 2, 40))
                    
                    nav_lbl = font_ui.render("【←】前の枚数へ  /  【→】次の枚数へ", True, (255, 215, 0))
                    screen.blit(nav_lbl, (SCREEN_WIDTH // 2 - nav_lbl.get_width() // 2, 95))
                    
                    rev_student_sheet.fill((255, 255, 255))
                    rev_model_sheet.fill((255, 255, 255))
                    
                    base_img = student_sheets_images.get(rev_data["file"])
                    if base_img: rev_student_sheet.blit(base_img, (0, 0))
                    
                    pygame.draw.rect(rev_model_sheet, (160, 160, 160), (460, 29, 34, 273), 1)   
                    pygame.draw.rect(rev_model_sheet, (160, 160, 160), (415, 29, 45, 273), 1)   
                    pygame.draw.line(rev_model_sheet, (160, 160, 160), (415, 85), (460, 85), 1)   
                    pygame.draw.line(rev_model_sheet, (160, 160, 160), (415, 225), (460, 225), 1) 
                    
                    title_str = "ひらがなテスト"
                    for t_idx, t_char in enumerate(title_str):
                        rev_model_sheet.blit(font_sub.render(t_char, True, (120, 120, 120)), (470, 45 + t_idx * 18))
                    rev_model_sheet.blit(font_sub.render("番", True, (120, 120, 120)), (430, 52))
                    rev_model_sheet.blit(font_sub.render("名前", True, (120, 120, 120)), (423, 145))
                    rev_model_sheet.blit(font_sub.render("点", True, (120, 120, 120)), (430, 255))
                    
                    for idx in range(10):
                        box_rect = answer_boxes[idx]
                        h_prob = rev_data["dataset"][idx]
                        
                        pygame.draw.rect(rev_student_sheet, (200, 200, 200), box_rect, 1)
                        pygame.draw.rect(rev_model_sheet, (160, 160, 160), box_rect, 1)
                        
                        num_str = f"({h_prob['num']})"
                        rev_model_sheet.blit(font_sub.render(num_str, True, (120, 120, 120)), (box_rect.x + 10, box_rect.y - 16))
                        
                        t_chars = len(h_prob["model_ans"])
                        spacing = (box_rect.height - 20) // t_chars if t_chars > 1 else 38
                        start_y_offset = 20 if t_chars > 2 else 32
                        start_x_offset = box_rect.width // 2 - 15
                        for g_idx, g_char in enumerate(h_prob["model_ans"]):
                            rev_model_sheet.blit(font_main.render(g_char, True, (220, 50, 50)), (box_rect.x + start_x_offset, box_rect.y + start_y_offset + g_idx * spacing))
                        
                        user_res = rev_data["scoring_results"][idx]
                        if user_res == "MARU" and maru_images:
                            rev_student_sheet.blit(maru_images[0], (box_rect.x + box_rect.width // 2 - 40, box_rect.y + box_rect.height // 2 - 40))
                        elif user_res == "BATSU" and cross_images:
                            rev_student_sheet.blit(cross_images[0], (box_rect.x + box_rect.width // 2 - 40, box_rect.y + box_rect.height // 2 - 40))
                            
                        if rev_data["erased_marks"][idx]:
                            cx = box_rect.x + box_rect.width // 2
                            pygame.draw.line(rev_student_sheet, (255, 0, 0), (cx - 4, box_rect.y + 10), (cx - 4, box_rect.y + box_rect.height - 10), 2)
                            pygame.draw.line(rev_student_sheet, (255, 0, 0), (cx + 4, box_rect.y + 10), (cx + 4, box_rect.y + box_rect.height - 10), 2)
                        
                        if rev_data["miss_flags"][idx]:
                            miss_shade = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
                            miss_shade.fill((255, 0, 0, 70)) 
                            rev_student_sheet.blit(miss_shade, (box_rect.x, box_rect.y))
                            pygame.draw.rect(rev_student_sheet, (255, 0, 0), box_rect, 3) 
                            
                            m_txt = font_sub.render("MISSED", True, (255, 255, 255))
                            pygame.draw.rect(rev_student_sheet, (20, 20, 20), (box_rect.x + 2, box_rect.y + box_rect.height - 20, box_rect.width - 4, 18))
                            rev_student_sheet.blit(m_txt, (box_rect.x + box_rect.width // 2 - m_txt.get_width() // 2, box_rect.y + box_rect.height - 18))

                    screen.blit(rev_student_sheet, (STUDENT_SHEET_RECT.x, STUDENT_SHEET_RECT.y - 10))
                    screen.blit(rev_model_sheet, (MODEL_SHEET_RECT.x, MODEL_SHEET_RECT.y - 10))
                    
                    info_font = font_sub
                    screen.blit(info_font.render(f"生徒: {rev_data['student_name']} ({rev_data['file']})", True, (255, 255, 255)), (STUDENT_SHEET_RECT.x + 10, STUDENT_SHEET_RECT.y + 350))
                    screen.blit(info_font.render(f"ミス数: {sum(rev_data['miss_flags'])} 箇所", True, (255, 150, 150)), (MODEL_SHEET_RECT.x + 10, MODEL_SHEET_RECT.y + 350))

                pygame.draw.rect(screen, (50, 50, 50), (result_back_to_stat_btn_rect.x, result_back_to_stat_btn_rect.y + 3, result_back_to_stat_btn_rect.width, result_back_to_stat_btn_rect.height), border_radius=6)
                pygame.draw.rect(screen, (100, 100, 100), result_back_to_stat_btn_rect, border_radius=6)
                pygame.draw.rect(screen, (255, 255, 255), result_back_to_stat_btn_rect, 1, border_radius=6)
                back_font_txt = font_ui.render("査定レポートに戻る", True, (255, 255, 255))
                screen.blit(back_font_txt, (SCREEN_WIDTH // 2 - back_font_txt.get_width() // 2, result_back_to_stat_btn_rect.y + result_back_to_stat_btn_rect.height // 2 - back_font_txt.get_height() // 2))

            pulse_alpha = int(155 + 100 * math.sin(pygame.time.get_ticks() * 0.007))
            restart_lbl = font_ui.render("【 Enter 】を押してタイトル画面に戻る", True, (150, 160, 170))
            restart_surf = restart_lbl.convert_alpha()
            restart_surf.fill((255, 255, 255, pulse_alpha), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(restart_surf, (SCREEN_WIDTH // 2 - restart_lbl.get_width() // 2, 595))

        # --- イベント処理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "TITLE":
                    if title_start_button_rect.collidepoint(event.pos):
                        if se_btn_start: se_btn_start.play() 
                        start_new_game()
                        continue
                
                elif game_state == "RESULT":
                    if not show_wrong_matrix:
                        if result_view_miss_btn_rect.collidepoint(event.pos):
                            if se_btn_score_view: se_btn_score_view.play() 
                            show_wrong_matrix = True
                            review_current_idx = 0 
                    else:
                        if result_back_to_stat_btn_rect.collidepoint(event.pos):
                            if se_btn_start: se_btn_start.play() 
                            show_wrong_matrix = False

            if event.type == pygame.KEYDOWN:
                if game_state == "TITLE" and event.key == pygame.K_RETURN:
                    if se_btn_start: se_btn_start.play() 
                    start_new_game()
                    continue

                if game_state == "RESULT" and event.key == pygame.K_RETURN:
                    if se_btn_start: se_btn_start.play() 
                    play_scene_bgm("TITLE") 
                    game_state = "TITLE"
                    continue

                if game_state == "RESULT" and show_wrong_matrix and len(history_marked_sheets) > 0:
                    if event.key == pygame.K_LEFT:
                        if review_current_idx > 0:
                            review_current_idx -= 1
                            if batsu_sounds: random.choice(batsu_sounds).play()
                    elif event.key == pygame.K_RIGHT:
                        if review_current_idx < len(history_marked_sheets) - 1:
                            review_current_idx += 1
                            if batsu_sounds: random.choice(batsu_sounds).play()

                if game_state == "PLAY":
                    if is_otsubone_active:
                        if event.key == pygame.K_SPACE:
                            if speech_bubbles:
                                speech_bubbles.pop()
                                if maru_sounds: random.choice(maru_sounds).play() 
                            if not speech_bubbles: is_otsubone_active = False 
                        continue 

                    if not is_animating and not sheet_completed and not is_otsubone_active:
                        if event.key == pygame.K_LEFT:
                            if current_order_idx > 0:
                                current_order_idx -= 1
                                current_prob_idx = prob_order[current_order_idx]
                                if batsu_sounds: random.choice(batsu_sounds).play()
                        elif event.key == pygame.K_RIGHT:
                            if current_order_idx < 9: 
                                current_order_idx += 1
                                current_prob_idx = prob_order[current_order_idx]
                                if batsu_sounds: random.choice(batsu_sounds).play()

                        elif event.key == pygame.K_BACKSPACE:
                            if scoring_results[current_prob_idx] is not None and not erased_marks[current_prob_idx]:
                                erased_marks[current_prob_idx] = True 
                                sheet_completed = False                
                                total_miss_count += 1 
                                current_sheet_penalty = 50 * total_miss_count * total_miss_count
                                current_sheet_miss_flags[current_prob_idx] = True 
                                has_missed_in_game[current_prob_idx] = True 
                                if batsu_sounds: random.choice(batsu_sounds).play() 

                        elif event.key == pygame.K_UP:
                            current_mode, anim_progress, is_animating = "MARU", 0.0, True
                            current_img = random.choice(maru_images) if maru_images else None
                            sheet_stamps[current_prob_idx] = current_img
                            scoring_results[current_prob_idx] = "MARU"
                            erased_marks[current_prob_idx] = False 
                            if current_dataset[current_prob_idx]["correct"] != "MARU":
                                total_miss_count += 1
                                current_sheet_penalty = 50 * total_miss_count * total_miss_count
                                current_sheet_miss_flags[current_prob_idx] = True 
                                has_missed_in_game[current_prob_idx] = True
                            if maru_sounds: random.choice(maru_sounds).play()
                            
                        elif event.key == pygame.K_DOWN:
                            current_mode, anim_progress, is_animating = "BATSU", 0.0, True
                            current_img = random.choice(cross_images) if cross_images else None
                            sheet_stamps[current_prob_idx] = current_img
                            scoring_results[current_prob_idx] = "BATSU"
                            erased_marks[current_prob_idx] = False 
                            if current_dataset[current_prob_idx]["correct"] != "BATSU":
                                total_miss_count += 1
                                current_sheet_penalty = 50 * total_miss_count * total_miss_count
                                current_sheet_miss_flags[current_prob_idx] = True 
                                has_missed_in_game[current_prob_idx] = True
                            if batsu_sounds: random.choice(batsu_sounds).play()

                    if sheet_completed and event.key == pygame.K_RETURN and not is_otsubone_active:
                        sheet_snapshot = {
                            "file": current_sheet_file,
                            "student_name": current_student_name,
                            "dataset": list(current_dataset),
                            "scoring_results": list(scoring_results),
                            "erased_marks": list(erased_marks),
                            "miss_flags": list(current_sheet_miss_flags)
                        }
                        history_marked_sheets.append(sheet_snapshot)
                        
                        all_sheets_time.append(stage_timer)          
                        all_sheets_penalties.append(current_sheet_penalty) 
                        total_sheets_marked += 1 
                        current_sheet_penalty = 0                    
                        
                        if current_stage < 6: current_stage += 1
                        else: current_stage = 1
                        
                        chosen_cfg = random.choice(SHEET_CONFIGS)
                        current_sheet_file = chosen_cfg["file"]
                        current_dataset = generate_kanji_dataset_for_sheet(chosen_cfg["wrong"])
                        
                        stage_timer = 0.0  
                        scoring_results = [None] * 10
                        erased_marks = [False] * 10 
                        sheet_stamps = [None] * 10
                        current_sheet_miss_flags = [False] * 10 
                        current_order_idx, sheet_completed, otsubone_triggered = 0, False, False
                        current_prob_idx = prob_order[current_order_idx]
                        current_student_name = random.choice(STUDENT_NAMES)

        if game_state == "PLAY" and is_animating and not is_otsubone_active:
            anim_progress += ANIM_SPEED
            if anim_progress >= 1.0:
                anim_progress, is_animating = 1.0, False
                
                all_done = True
                for i in range(10):
                    if scoring_results[i] is None or erased_marks[i]:
                        all_done = False
                        break
                        
                if all_done:
                    sheet_completed = True
                else:
                    found_next = False
                    for search_idx in range(current_order_idx + 1, 10):
                        p_idx = prob_order[search_idx]
                        if scoring_results[p_idx] is None or erased_marks[p_idx]:
                            current_order_idx = search_idx
                            current_prob_idx = p_idx
                            found_next = True
                            break
                    if not found_next:
                        for search_idx in range(0, current_order_idx):
                            p_idx = prob_order[search_idx]
                            if scoring_results[p_idx] is None or erased_marks[p_idx]:
                                current_order_idx = search_idx
                                current_prob_idx = p_idx
                                found_next = True
                                break

        pygame.display.flip()
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())