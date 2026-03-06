# -*- coding: utf-8 -*-
"""
계단 점프 미니게임 - 메인 진입점
더블클릭 또는: python main.py
"""
import math
import os
import random
import sys
import pygame
from pygame import Rect

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    COLS, COL_WIDTH, STAIR_HEIGHT, STAIR_STEP_HEIGHT, STAIR_WIDTH, STAIR_OFFSET_X,
    STAIR_RADIUS, STAIR_SHADOW_OFFSET, BASE_Y,
    INITIAL_TIME,
    CHAR_SIZE, CHAR_RADIUS, JUMP_DURATION, JUMP_ARC_HEIGHT,
    COLOR_SKY_TOP, COLOR_SKY_MID1, COLOR_SKY_MID2, COLOR_SKY_BOTTOM, COLOR_SKY_GLOW, COLOR_VIGNETTE,
    COLOR_FOG, COLOR_FOG_SOFT, COLOR_FOG_LIGHT,
    COLOR_MOON, COLOR_MOON_GLOW, COLOR_MOON_DIM,
    COLOR_STAIR_TOP, COLOR_STAIR_MID, COLOR_STAIR_BOTTOM, COLOR_STAIR_EDGE,
    COLOR_STAIR_HIGHLIGHT, COLOR_STAIR_HIGHLIGHT_STRONG, COLOR_STAIR_SHADOW, COLOR_STAIR_SHADOW_SOFT,
    COLOR_STAIR_SIDE, COLOR_STAIR_SIDE_DARK,
    COLOR_STAIR_CURRENT_TOP, COLOR_STAIR_CURRENT_BOTTOM,
    COLOR_FLOWER_CENTER, COLOR_FLOWER_CENTER_LIGHT, COLOR_FLOWER_PETAL, COLOR_FLOWER_PETAL_SHADE,
    COLOR_FLOWER_PETAL_HIGHLIGHT, COLOR_FLOWER_LEAF, COLOR_FLOWER_LEAF_DARK, COLOR_FLOWER_SHADOW,
    COLOR_DOG_BODY, COLOR_DOG_BODY_DARK, COLOR_DOG_BODY_HIGHLIGHT, COLOR_DOG_BELLY,
    COLOR_DOG_NOSE, COLOR_DOG_NOSE_SHINE, COLOR_DOG_EAR, COLOR_DOG_EAR_SHADE, COLOR_DOG_EYE,
    COLOR_CHAR_MAIN, COLOR_CHAR_DARK, COLOR_CHAR_JUMP, COLOR_CHAR_OUTLINE, COLOR_CHAR_SHADOW,
    COLOR_CHAR_HAIR, COLOR_CHAR_EDGE, COLOR_CHAR_EYE, COLOR_CHAR_BLUSH,
    COLOR_UI_PANEL, COLOR_UI_PANEL_TOP, COLOR_UI_PANEL_BORDER, COLOR_UI_SHADOW,
    COLOR_TIMER_SAFE, COLOR_TIMER_MID, COLOR_TIMER_DANGER, COLOR_TIMER_BG,
    COLOR_TEXT, COLOR_TEXT_SUB, COLOR_GAME_OVER, COLOR_GAME_OVER_BG, COLOR_GAME_OVER_TEXT,
    FALL_GRAVITY, FALL_DURATION,
    GAME_OVER_SHAKE_DURATION, GAME_OVER_FADE_DURATION, GAME_OVER_TEXT_APPEAR,
    COLOR_TEAR, COLOR_TEAR_SHINE,
    LANDING_SHAKE_DURATION, LANDING_SHAKE_STRENGTH, COLOR_DUST, COLOR_TAKEOFF,
)
from game import GameState


def _base_path():
    """실행 파일/스크립트 기준 경로 (exe·웹 패키징 시에도 동작)."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except Exception:
        return os.getcwd()


def _user_path():
    """저장용 경로 (exe일 때는 exe 있는 폴더)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _is_web():
    """웹(Pygbag/Emscripten)에서 실행 중인지 여부."""
    return sys.platform == "emscripten"


def col_to_x(col: int) -> float:
    """열 인덱스 -> 화면 x 좌표 (열 중심)"""
    return col * COL_WIDTH + COL_WIDTH / 2


def stair_y_screen(level: int, camera: int) -> float:
    """계단 레벨의 윗면 화면 y. camera=현재 점수(카메라 기준)."""
    return (camera - level) * STAIR_HEIGHT + BASE_Y


def ease_out_quad(t: float) -> float:
    """0~1 -> 이징된 0~1 (점프 궤적용)"""
    return 1 - (1 - t) ** 2


def ease_in_out_quad(t: float) -> float:
    """이동 애니메이션용"""
    if t < 0.5:
        return 2 * t * t
    return 1 - (-2 * t + 2) ** 2 / 2


def draw_gradient_vertical(surf, top_color, bottom_color, y_start=0, height=None):
    """세로 그라데이션"""
    if height is None:
        height = surf.get_height() - y_start
    for i in range(height):
        t = i / max(height - 1, 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y_start + i), (SCREEN_WIDTH, y_start + i))


def draw_rect_vertical_gradient(surf, rect, top_color, bottom_color):
    """사각형 세로 그라데이션 채우기"""
    for i in range(rect.height):
        t = i / max(rect.height - 1, 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        pygame.draw.line(surf, (r, g, b), (rect.x, rect.y + i), (rect.right, rect.y + i))


def draw_rounded_rect(surf, color, rect, radius):
    """둥근 모서리 사각형 (pygame 2 border_radius)"""
    pygame.draw.rect(surf, color, rect, border_radius=radius)


def draw_rect_horizontal_gradient(surf, rect, left_color, right_color):
    """가로 그라데이션 (3D 빛 방향)"""
    for i in range(rect.width):
        t = i / max(rect.width - 1, 1)
        r = int(left_color[0] + (right_color[0] - left_color[0]) * t)
        g = int(left_color[1] + (right_color[1] - left_color[1]) * t)
        b = int(left_color[2] + (right_color[2] - left_color[2]) * t)
        pygame.draw.line(surf, (r, g, b), (rect.x + i, rect.y), (rect.x + i, rect.bottom))


def strip_white_background(surf, threshold=215):
    """밝은 배경을 완전 투명(alpha=0)으로. R,G,B 평균이 threshold 이상이면 배경으로 간주."""
    try:
        masks = surf.get_masks()
        if len(masks) < 4 or not masks[3]:
            return surf
    except Exception:
        return surf
    w, h = surf.get_size()
    for x in range(w):
        for y in range(h):
            c = surf.get_at((x, y))
            if len(c) >= 4:
                r, g, b, a = c[0], c[1], c[2], c[3]
                if (r + g + b) // 3 >= threshold:
                    surf.set_at((x, y), (r, g, b, 0))
    return surf


def draw_flower(surf, cx: int, cy: int, r: int = 12):
    """시간 아이템: 3D 꽃 (그림자·하이라이트·입체)"""
    # 바닥에 부드러운 그림자 (3D 떠있는 느낌)
    shadow_r = Rect(cx - r - 2, cy + 2, r * 2 + 4, r // 2 + 2)
    shadow_s = pygame.Surface((shadow_r.w, shadow_r.h), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_s, (*COLOR_FLOWER_SHADOW, 48), (0, 0, shadow_r.w, shadow_r.h))
    surf.blit(shadow_s, shadow_r.topleft)
    # 꽃잎 5개: 그림자 → 본색 → 하이라이트
    for i in range(5):
        angle = i * 2 * math.pi / 5 - math.pi / 2
        px = cx + int(r * 1.05 * math.cos(angle))
        py = cy + int(r * 1.05 * math.sin(angle))
        pygame.draw.circle(surf, COLOR_FLOWER_PETAL_SHADE, (px, py), r // 2 + 2)
        pygame.draw.circle(surf, COLOR_FLOWER_PETAL, (px, py), r // 2)
        # 꽃잎 위쪽 작은 하이라이트
        hx = cx + int(r * 0.6 * math.cos(angle - 0.2))
        hy = cy + int(r * 0.6 * math.sin(angle - 0.2))
        pygame.draw.circle(surf, COLOR_FLOWER_PETAL_HIGHLIGHT, (hx, hy), max(1, r // 4))
    # 중심: 입체 (어두운 테두리 → 밝은 중심)
    pygame.draw.circle(surf, COLOR_FLOWER_LEAF_DARK, (cx, cy), r // 2 + 1)
    pygame.draw.circle(surf, COLOR_FLOWER_CENTER, (cx, cy), r // 2)
    pygame.draw.circle(surf, COLOR_FLOWER_CENTER_LIGHT, (cx - 1, cy - 1), max(1, r // 4))
    # 잎
    for (dx, w, h) in [(-r - 4, 12, 10), (2, 12, 10)]:
        er = Rect(cx + dx, cy + r // 2, w, h)
        pygame.draw.ellipse(surf, COLOR_FLOWER_LEAF_DARK, er)
        pygame.draw.ellipse(surf, COLOR_FLOWER_LEAF, er.inflate(-2, -2))


# 최고 기록 파일
def _highscore_path():
    return os.path.join(_user_path(), "highscore.txt")


def load_highscore():
    try:
        p = _highscore_path()
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                return int(f.read().strip())
    except Exception:
        pass
    return 0


def save_highscore(score: int):
    try:
        with open(_highscore_path(), "w", encoding="utf-8") as f:
            f.write(str(score))
    except Exception:
        pass


class AnimState:
    """캐릭터 애니메이션 상태 - 제자리 이동 없음, 대각선 점프만"""
    IDLE = "idle"
    JUMP_UP = "jump_up"


class GameApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("계단 점프 (무한의 계단)")
        # 웹에서는 SCALED 없이 고정 해상도 사용 → exe와 비슷한 비율/크기 유지
        if _is_web():
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
        self.clock = pygame.time.Clock()
        # 디자인용 작은 글씨·예쁜 폰트 (없으면 기본)
        self._init_fonts()
        self.state = GameState()

        self.anim = AnimState.IDLE
        self.anim_t = 0.0
        self.jump_start_x = 0.0
        self.jump_end_x = 0.0
        self.jump_start_y = 0.0
        self.jump_end_y = 0.0
        self.jump_landing_col = None
        self.char_x = 0.0
        self.char_y = 0.0
        self.high_score = load_highscore()
        # 잘못된 방향 → 울면서 떨어짐 연출
        self.falling = False
        self.fall_t = 0.0
        self.fall_vy = 0.0
        # 화면 밖으로 점프 시: 잠깐 밖으로 나가는 연출 후 낙하
        self.jump_off_t = None  # None이 아니면 초 단위 누적 시간
        self.jump_off_direction = 0   # -1=왼쪽, 1=오른쪽
        # 게임오버 효과 (흔들림 → 페이드 → 텍스트)
        self.game_over_effect_start = None
        # 마일스톤 (50, 100, 200, 300... 계단 넘었을 때 안내)
        self.last_milestone_announced = 0
        self.milestone_message = None
        self.milestone_until = 0
        # 배경 이미지 (image/background.png 있으면 사용)
        self._bg_image = None
        self._bg_image_scaled = None
        _bg_path = os.path.join(_base_path(), "image", "background.png")
        if os.path.isfile(_bg_path):
            try:
                self._bg_image = pygame.image.load(_bg_path).convert_alpha()
            except Exception:
                pass
        # 캐릭터 이미지 (image/character) — 흰 배경이 있으면 코드로 투명 처리
        self._char_image = None
        self._char_image_left = None
        _img_dir = os.path.join(_base_path(), "image")
        for _name in ("character.png", "Character.png", "characetr.png", "character.jpg", "characetr.jpg", "character.jpeg", "characetr.jpeg"):
            _char_path = os.path.join(_img_dir, _name)
            if os.path.isfile(_char_path):
                try:
                    img = pygame.image.load(_char_path).convert_alpha()
                    strip_white_background(img, threshold=200)
                    cw, ch = 56, CHAR_SIZE
                    self._char_image = pygame.transform.smoothscale(img, (cw, ch))
                    self._char_image_left = pygame.transform.flip(self._char_image, True, False)
                    break
                except Exception:
                    pass
        # 계단 이미지 (image/step.png) — 배경 투명 처리 후 배경과 자연스럽게
        self._step_image = None
        _step_path = os.path.join(_img_dir, "step.png")
        if os.path.isfile(_step_path):
            try:
                step_img = pygame.image.load(_step_path).convert_alpha()
                strip_white_background(step_img, threshold=210)
                self._step_image = pygame.transform.smoothscale(step_img, (STAIR_WIDTH, STAIR_STEP_HEIGHT))
            except Exception:
                pass
        # 시간 아이템 이미지 (image/item.png) — 계단 위 꽃 대신 사용
        self._item_image = None
        _item_path = os.path.join(_img_dir, "item.png")
        _item_size = 40
        if os.path.isfile(_item_path):
            try:
                item_img = pygame.image.load(_item_path).convert_alpha()
                strip_white_background(item_img, threshold=210)
                self._item_image = pygame.transform.smoothscale(item_img, (_item_size, _item_size))
            except Exception:
                pass
        # 오프닝 타이틀 이미지 (image/title.png) — 규격 480x720이면 스케일 없이 사용
        self._title_image = None
        _title_path = os.path.join(_img_dir, "title.png")
        if os.path.isfile(_title_path):
            try:
                title_img = pygame.image.load(_title_path).convert_alpha()
                if title_img.get_size() == (SCREEN_WIDTH, SCREEN_HEIGHT):
                    self._title_image = title_img
                else:
                    self._title_image = pygame.transform.smoothscale(title_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except Exception:
                pass
        # Game Start 메시지 표시 종료 시각 (오프닝 직후 한 번)
        self.game_start_until = None
        # 모바일/데스크톱 공통: 하단 버튼 (방향전환 왼쪽, 점프 오른쪽)
        self._touch_buttons = True
        bw, bh = 110, 44
        gap = 20
        total_w = bw * 2 + gap
        left_x = (SCREEN_WIDTH - total_w) // 2
        by = SCREEN_HEIGHT - bh - 24
        self._btn_turn = Rect(left_x, by, bw, bh)
        self._btn_climb = Rect(left_x + bw + gap, by, bw, bh)
        # 게임오버 시 왼쪽 종료, 오른쪽 다시시작
        go_bw, go_bh = 100, 40
        go_gap = 16
        go_total = go_bw * 2 + go_gap
        go_left = (SCREEN_WIDTH - go_total) // 2
        go_by = SCREEN_HEIGHT // 2 + 50
        self._btn_quit = Rect(go_left, go_by, go_bw, go_bh)
        self._btn_restart = Rect(go_left + go_bw + go_gap, go_by, go_bw, go_bh)
        self._quit_requested = False
        # 점프·착지 이펙트
        self._particles = []
        self._landing_shake_until = 0
        self._shake_dx = 0
        self._shake_dy = 0
        self._update_char_pos_from_state()

    def _init_fonts(self):
        """한글 UI: font 폴더의 TTF 우선(Noto Sans KR 등), 없으면 맑은 고딕."""
        self._use_english_ui = False
        base = _base_path()
        ttf_names = ["NotoSansKR-Regular.ttf", "NanumGothic.ttf", "NotoSansKR-Medium.ttf", "Malgun.ttf"]
        ttf_candidates = [os.path.join(base, "font", name) for name in ttf_names]
        cwd = os.getcwd()
        for name in ttf_names:
            ttf_candidates.append(os.path.join(cwd, "font", name))
            ttf_candidates.append(os.path.normpath(os.path.join(cwd, "font", name)))
        if _is_web():
            ttf_candidates.extend(["font/" + name for name in ttf_names])
        ttf_path = None
        for p in ttf_candidates:
            if p and os.path.isfile(p):
                ttf_path = p
                break
        if ttf_path:
            try:
                self.font = pygame.font.Font(ttf_path, 14)
                self.font_big = pygame.font.Font(ttf_path, 20)
                self.font_title = pygame.font.Font(ttf_path, 48)
                return
            except Exception:
                pass
        try:
            self.font = pygame.font.SysFont("malgun gothic", 14, bold=False)
            self.font_big = pygame.font.SysFont("malgun gothic", 20, bold=True)
            self.font_title = pygame.font.SysFont("malgun gothic", 48, bold=True)
            return
        except Exception:
            pass
        self.font = pygame.font.Font(None, 22)
        self.font_big = pygame.font.Font(None, 32)
        self.font_title = pygame.font.Font(None, 48)

    def _update_char_pos_from_state(self):
        """현재 서 있는 위치(바닥 또는 계단) 기준 캐릭터 위치. 카메라 반영."""
        cam = self.state.score
        self.char_x = col_to_x(self.state.current_col())
        # score=-1: 바닥, score>=0: 계단 상단에 착지 (살짝만 위로)
        if cam == -1:
            self.char_y = stair_y_screen(-1, cam) - CHAR_SIZE
        else:
            step_top = stair_y_screen(cam, cam) - STAIR_STEP_HEIGHT
            self.char_y = step_top - CHAR_SIZE + 20

    def start_climb(self):
        """오르기: 현재 방향으로 대각선 점프"""
        if self.state.game_over or self.anim == AnimState.JUMP_UP:
            return
        landing_col = self.state.get_landing_col_climb()
        if landing_col < 0 or landing_col >= COLS:
            self.state.game_over = True
            self.state.game_over_reason = "wrong"
            self.jump_off_t = 0.0
            self.jump_off_direction = -1 if landing_col < 0 else 1
            return
        self._start_jump_to(landing_col)

    def start_turn_and_climb(self):
        """방향 전환: 돌고 그 방향으로 대각선 점프"""
        if self.state.game_over or self.anim == AnimState.JUMP_UP:
            return
        landing_col = self.state.get_landing_col_turn()
        if landing_col < 0 or landing_col >= COLS:
            self.state.game_over = True
            self.state.game_over_reason = "wrong"
            self.jump_off_t = 0.0
            self.jump_off_direction = -1 if landing_col < 0 else 1
            return
        self._start_jump_to(landing_col)

    def _spawn_takeoff_particles(self, x: float, y: float):
        """점프 시작 시 발밑 이펙트."""
        for _ in range(8):
            angle = random.uniform(-math.pi * 0.7, -math.pi * 0.3) + random.choice([0, math.pi]) * 0.3
            speed = random.uniform(40, 90)
            self._particles.append({
                "x": x + random.uniform(-8, 8), "y": y,
                "vx": math.cos(angle) * speed, "vy": -abs(math.sin(angle)) * speed * 0.4,
                "life": random.uniform(0.12, 0.22), "life_max": 0.22,
                "r": random.uniform(3, 6), "color": COLOR_TAKEOFF,
            })

    def _spawn_landing_particles(self, x: float, y: float):
        """착지 시 짧은 먼지 이펙트 (다음 점프 전에 금방 사라지도록)."""
        for _ in range(5):
            angle = random.uniform(0, math.pi) + random.uniform(-0.3, 0.3)
            speed = random.uniform(30, 70)
            life_max = random.uniform(0.06, 0.10)
            self._particles.append({
                "x": x + random.uniform(-6, 6), "y": y,
                "vx": math.cos(angle) * speed * 0.4,
                "vy": -abs(math.sin(angle)) * speed * 0.3,
                "life": life_max, "life_max": life_max,
                "r": random.uniform(2, 4), "color": COLOR_DUST,
            })

    def _start_jump_to(self, landing_col: int):
        """착지 열로 대각선 점프 시작. 현재 카메라 기준 다음 계단 위치로."""
        cam = self.state.score
        self.anim = AnimState.JUMP_UP
        self.anim_t = 0.0
        self.jump_start_x = self.char_x
        self.jump_end_x = col_to_x(landing_col)
        self.jump_start_y = self.char_y
        step_top = stair_y_screen(cam + 1, cam) - STAIR_STEP_HEIGHT
        self.jump_end_y = step_top - CHAR_SIZE + 20
        self.jump_landing_col = landing_col
        self._spawn_takeoff_particles(self.char_x, self.char_y + CHAR_SIZE - 8)

    def update(self, dt: float):
        self.state.tick_time(dt)

        # 화면 밖으로 점프한 경우: 잠깐 밖으로 나가는 연출 후 낙하 → 게임오버
        if self.jump_off_t is not None:
            self.jump_off_t += dt
            speed = COL_WIDTH * 2.8
            self.char_x += self.jump_off_direction * speed * dt
            if self.jump_off_t >= 0.25:
                self.jump_off_t = None
                self.falling = True
                self.fall_t = 0.0
                self.fall_vy = 0.0

        # 울면서 떨어지는 연출
        if self.falling:
            self.fall_t += dt
            self.fall_vy += FALL_GRAVITY * dt
            self.char_y += self.fall_vy * dt
            if self.fall_t >= FALL_DURATION or self.char_y > SCREEN_HEIGHT + 80:
                self.falling = False
                self.game_over_effect_start = pygame.time.get_ticks()
            return
        # 시간 초과 게임오버 → 효과 시작 시점
        if self.state.game_over and not self.falling and self.game_over_effect_start is None:
            self.game_over_effect_start = pygame.time.get_ticks()

        # 파티클 업데이트
        for p in self._particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self._particles.remove(p)
        # 착지 흔들림
        now = pygame.time.get_ticks()
        if now < self._landing_shake_until:
            self._shake_dx = (random.random() - 0.5) * 2 * LANDING_SHAKE_STRENGTH
            self._shake_dy = (random.random() - 0.5) * 2 * LANDING_SHAKE_STRENGTH
        else:
            self._shake_dx = 0
            self._shake_dy = 0

        if self.anim == AnimState.JUMP_UP:
            self.anim_t += dt / JUMP_DURATION
            if self.anim_t >= 1.0:
                self.anim_t = 1.0
                self.anim = AnimState.IDLE
                success, _ = self.state.try_land(self.jump_landing_col)
                if not success:
                    return
                self._update_char_pos_from_state()
                self._spawn_landing_particles(self.char_x, self.char_y + CHAR_SIZE - 8)
                self._landing_shake_until = now + int(LANDING_SHAKE_DURATION * 1000)
                self.jump_landing_col = None
                return
            t = self.anim_t
            # x는 선형 이동
            self.char_x = self.jump_start_x + (self.jump_end_x - self.jump_start_x) * t
            # y는 포물선: 직선 보간 + 위로 휘는 궤적 (0과 1에서 0, 0.5에서 최고점)
            y_linear = self.jump_start_y + (self.jump_end_y - self.jump_start_y) * t
            arc = JUMP_ARC_HEIGHT * 4 * t * (1 - t)  # 0 ~ 1에서 0, 중간에서 최대
            self.char_y = y_linear - arc

        # 50 → 100 → 200 → 300... 계단 넘었을 때 안내
        if not self.state.game_over and self.state.score >= 0:
            milestones = [50] + list(range(100, 10000, 100))
            for m in milestones:
                if self.state.score >= m and self.last_milestone_announced < m:
                    self.milestone_message = f"{m} steps!" if self._use_english_ui else f"{m}계단을 넘었습니다!"
                    self.milestone_until = pygame.time.get_ticks() + 2500
                    self.last_milestone_announced = m
                    break

    def _draw_background(self):
        """배경: image/background.png 이미지 사용, 없으면 기존 그리기"""
        h = SCREEN_HEIGHT
        w = SCREEN_WIDTH
        if self._bg_image is not None:
            if self._bg_image_scaled is None or (self._bg_image_scaled.get_width(), self._bg_image_scaled.get_height()) != (w, h):
                self._bg_image_scaled = pygame.transform.smoothscale(self._bg_image, (w, h))
            self.screen.blit(self._bg_image_scaled, (0, 0))
            # 가장자리 비네팅 (이미지 위에 은은하게)
            v_alpha = 42
            v_w, v_h = 56, 88
            for (x, y) in [(0, 0), (w - v_w, 0), (0, h - v_h), (w - v_w, h - v_h)]:
                vig = pygame.Surface((v_w, v_h))
                vig.set_alpha(v_alpha)
                vig.fill(COLOR_VIGNETTE)
                self.screen.blit(vig, (x, y))
            top_bar = pygame.Surface((w, 32))
            top_bar.set_alpha(24)
            top_bar.fill(COLOR_VIGNETTE)
            self.screen.blit(top_bar, (0, 0))
            bot_bar = pygame.Surface((w, 32))
            bot_bar.set_alpha(24)
            bot_bar.fill(COLOR_VIGNETTE)
            self.screen.blit(bot_bar, (0, h - 32))
            return
        # 폴백: 기존 밤하늘 + 달 + 안개
        draw_gradient_vertical(self.screen, COLOR_SKY_TOP, COLOR_SKY_MID1, 0, h // 4)
        draw_gradient_vertical(self.screen, COLOR_SKY_MID1, COLOR_SKY_MID2, h // 4, h // 4)
        draw_gradient_vertical(self.screen, COLOR_SKY_MID2, COLOR_SKY_BOTTOM, h // 2)
        moon_x, moon_y = w - 72, 58
        glow_s = pygame.Surface((80, 80), pygame.SRCALPHA)
        for r, alpha in [(38, 25), (30, 45), (22, 70)]:
            pygame.draw.circle(glow_s, (*COLOR_MOON_GLOW, alpha), (40, 40), r)
        self.screen.blit(glow_s, (moon_x - 40, moon_y - 40))
        pygame.draw.circle(self.screen, COLOR_MOON_DIM, (moon_x, moon_y), 22)
        pygame.draw.circle(self.screen, COLOR_MOON, (moon_x, moon_y), 18)
        pygame.draw.circle(self.screen, (240, 242, 248), (moon_x - 4, moon_y - 3), 4)
        for (px, py, rad) in [(80, 220, 55), (320, 380, 45), (200, 500, 40)]:
            fog_s = pygame.Surface((rad * 2 + 20, rad * 2 + 20), pygame.SRCALPHA)
            pygame.draw.circle(fog_s, (*COLOR_FOG_LIGHT, 38), (rad + 10, rad + 10), rad + 8)
            pygame.draw.circle(fog_s, (*COLOR_FOG_SOFT, 52), (rad + 10, rad + 10), rad)
            self.screen.blit(fog_s, (px - rad - 10, py - rad - 10))
        v_alpha = 48
        v_w, v_h = 52, 80
        for (x, y) in [(0, 0), (w - v_w, 0), (0, h - v_h), (w - v_w, h - v_h)]:
            vig = pygame.Surface((v_w, v_h))
            vig.set_alpha(v_alpha)
            vig.fill(COLOR_VIGNETTE)
            self.screen.blit(vig, (x, y))
        top_bar = pygame.Surface((w, 28))
        top_bar.set_alpha(28)
        top_bar.fill(COLOR_VIGNETTE)
        self.screen.blit(top_bar, (0, 0))
        bot_bar = pygame.Surface((w, 28))
        bot_bar.set_alpha(28)
        bot_bar.fill(COLOR_VIGNETTE)
        self.screen.blit(bot_bar, (0, h - 28))

    def _draw_stairs(self):
        """카메라 따라 화면에 보이는 계단만 그림. 이전 계단은 그대로 두고 화면 밖이면 안 그리기."""
        self.state._ensure_next_stair()
        cam = self.state.score
        # 카메라 기준 화면에 보일 레벨 범위 (현재 계단 위아래로 충분히)
        # 화면에 보이는 범위: 아래 8칸 + 위로 많이 (다음 계단 미리 보기)
        draw_from = max(0, cam - 8)
        draw_to = min(len(self.state.stair_list), cam + 22)
        # 바닥(레벨 -1) — 잔디 반짝임 없이 그라데이션만
        if cam == -1:
            ground_y = stair_y_screen(-1, -1)
            gr = Rect(0, ground_y, SCREEN_WIDTH, 18)
            draw_rect_vertical_gradient(self.screen, gr, COLOR_STAIR_TOP, COLOR_STAIR_MID)
            pygame.draw.line(self.screen, COLOR_STAIR_EDGE, (0, gr.bottom), (SCREEN_WIDTH, gr.bottom), 1)
        for level in range(draw_from, draw_to):
            sy_top = stair_y_screen(level, cam)
            if sy_top < -STAIR_STEP_HEIGHT or sy_top > SCREEN_HEIGHT + STAIR_HEIGHT:
                continue
            s = self.state.stair_list[level]
            sx = s.col * COL_WIDTH + STAIR_OFFSET_X
            sy = sy_top - STAIR_STEP_HEIGHT
            r = Rect(sx, sy, STAIR_WIDTH, STAIR_STEP_HEIGHT)
            is_current = level == cam
            if self._step_image is not None:
                # step.png 이미지로 계단 그리기
                sh = Rect(r.x + STAIR_SHADOW_OFFSET, r.y + STAIR_SHADOW_OFFSET, r.w, r.h)
                shadow_surf = pygame.Surface((sh.w + 8, sh.h + 8), pygame.SRCALPHA)
                pygame.draw.rect(shadow_surf, (*COLOR_STAIR_SHADOW, 60), (4, 4, sh.w, sh.h), border_radius=STAIR_RADIUS + 2)
                self.screen.blit(shadow_surf, (sh.x - 4, sh.y - 4))
                self.screen.blit(self._step_image, (r.x, r.y))
            else:
                # 폴백: 기존 잔디밭 도형
                sh = Rect(r.x + STAIR_SHADOW_OFFSET, r.y + STAIR_SHADOW_OFFSET, r.w, r.h)
                shadow_surf = pygame.Surface((sh.w + 8, sh.h + 8), pygame.SRCALPHA)
                pygame.draw.rect(shadow_surf, (*COLOR_STAIR_SHADOW, 70), (4, 4, sh.w, sh.h), border_radius=STAIR_RADIUS + 2)
                self.screen.blit(shadow_surf, (sh.x - 4, sh.y - 4))
                draw_rounded_rect(self.screen, COLOR_STAIR_SHADOW_SOFT, sh, STAIR_RADIUS + 2)
                side_h = min(6, STAIR_STEP_HEIGHT // 3)
                side_rect = Rect(r.x, r.bottom, r.w, side_h)
                draw_rect_vertical_gradient(self.screen, side_rect, COLOR_STAIR_BOTTOM, COLOR_STAIR_SIDE_DARK)
                pygame.draw.line(self.screen, COLOR_STAIR_EDGE, (r.x, r.bottom), (r.right, r.bottom))
                pygame.draw.rect(self.screen, COLOR_STAIR_EDGE, side_rect, 1)
                top_c = COLOR_STAIR_CURRENT_TOP if is_current else COLOR_STAIR_TOP
                bot_c = COLOR_STAIR_CURRENT_BOTTOM if is_current else COLOR_STAIR_BOTTOM
                draw_rect_vertical_gradient(self.screen, r, top_c, bot_c)
                seed = hash((level, s.col)) % 0x8000
                for i in range(12):
                    rx = r.x + STAIR_RADIUS + (i * 7 + (seed % 5)) % max(1, r.w - STAIR_RADIUS * 2)
                    if rx >= r.right - STAIR_RADIUS:
                        continue
                    blade_h = 3 + (seed >> (i % 4)) % 4
                    pygame.draw.line(self.screen, COLOR_STAIR_HIGHLIGHT, (rx, r.y + 2), (rx, r.y + blade_h), 1)
                pygame.draw.rect(self.screen, COLOR_STAIR_EDGE, r, 1, border_radius=STAIR_RADIUS)
                hl_y = r.y + 1
                pygame.draw.line(self.screen, COLOR_STAIR_HIGHLIGHT_STRONG,
                                 (r.x + STAIR_RADIUS, hl_y), (r.right - STAIR_RADIUS, hl_y), 1)
            if s.has_time_item:
                if self._item_image is not None:
                    iw, ih = self._item_image.get_width(), self._item_image.get_height()
                    self.screen.blit(self._item_image, (r.centerx - iw // 2, r.top - ih + 18))
                else:
                    draw_flower(self.screen, r.centerx, r.top + 4, 10)

    def _draw_particles(self):
        """점프·착지 파티클 그리기 (착지 흔들림 오프셋 적용)."""
        dx, dy = int(self._shake_dx), int(self._shake_dy)
        for p in self._particles:
            alpha = int(255 * max(0, p["life"] / p["life_max"]))
            if alpha <= 0:
                continue
            surf = pygame.Surface((p["r"] * 2 + 4, p["r"] * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*p["color"], alpha), (p["r"] + 2, p["r"] + 2), p["r"])
            self.screen.blit(surf, (int(p["x"]) - p["r"] - 2 + dx, int(p["y"]) - p["r"] - 2 + dy))

    def _draw_character(self):
        """캐릭터: image/character 이미지 사용, 없으면 기존 도형 닥스훈트 (착지 흔들림 오프셋 적용)."""
        dx, dy = int(self._shake_dx), int(self._shake_dy)
        cx = int(self.char_x) + dx
        cy = int(self.char_y) + dy
        facing_right = self.state.facing_right
        if self._char_image is not None:
            img = self._char_image if facing_right else self._char_image_left
            iw, ih = img.get_width(), img.get_height()
            self.screen.blit(img, (cx - iw // 2, cy))
            return
        # 폴백: 기존 도형 닥스훈트
        body_w, body_h = 44, 18
        head_r = 12
        body_rect = Rect(cx - body_w // 2, cy + 8, body_w, body_h)
        head_cx = cx + (body_w // 2 + head_r - 2) if facing_right else cx - body_w // 2 - head_r + 2
        head_cy = cy + 10 + body_h // 2
        if self.anim != AnimState.JUMP_UP:
            shadow_rect = Rect(cx - body_w // 2 - 3, cy + CHAR_SIZE - 5, body_w + 10, 10)
            shadow_s = pygame.Surface((shadow_rect.w, shadow_rect.h), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_s, (*COLOR_CHAR_SHADOW, 65), (0, 0, shadow_rect.w, shadow_rect.h))
            self.screen.blit(shadow_s, shadow_rect.topleft)
        draw_rect_vertical_gradient(self.screen, body_rect,
                                  COLOR_CHAR_JUMP if self.anim == AnimState.JUMP_UP else COLOR_DOG_BODY,
                                  COLOR_DOG_BODY_DARK)
        highlight_strip = Rect(body_rect.x + 6, body_rect.y + 2, body_rect.w - 12, 4)
        pygame.draw.rect(self.screen, COLOR_DOG_BODY_HIGHLIGHT, highlight_strip, border_radius=2)
        pygame.draw.rect(self.screen, COLOR_CHAR_OUTLINE, body_rect, 1, border_radius=10)
        belly_r = Rect(body_rect.x + 4, body_rect.bottom - 8, body_rect.w - 8, 6)
        pygame.draw.rect(self.screen, COLOR_DOG_BELLY, belly_r, border_radius=3)
        pygame.draw.circle(self.screen, COLOR_CHAR_OUTLINE, (head_cx, head_cy), head_r + 1)
        pygame.draw.circle(self.screen, COLOR_DOG_BODY, (head_cx, head_cy), head_r)
        pygame.draw.circle(self.screen, COLOR_DOG_BODY_HIGHLIGHT, (head_cx - 2, head_cy - 2), max(2, head_r // 3))
        nose_x = head_cx + head_r - 2 if facing_right else head_cx - head_r + 2
        pygame.draw.circle(self.screen, COLOR_DOG_NOSE, (nose_x, head_cy), 5)
        pygame.draw.circle(self.screen, COLOR_DOG_NOSE_SHINE, (nose_x - 1, head_cy - 1), 1)
        if facing_right:
            pygame.draw.ellipse(self.screen, COLOR_DOG_EAR_SHADE, (head_cx - 5, head_cy - head_r - 3, 10, 12))
            pygame.draw.ellipse(self.screen, COLOR_DOG_EAR, (head_cx - 4, head_cy - head_r - 4, 10, 12))
            pygame.draw.ellipse(self.screen, COLOR_DOG_EAR_SHADE, (head_cx + 1, head_cy - head_r - 3, 10, 12))
            pygame.draw.ellipse(self.screen, COLOR_DOG_EAR, (head_cx + 2, head_cy - head_r - 4, 10, 12))
        else:
            pygame.draw.ellipse(self.screen, COLOR_DOG_EAR_SHADE, (head_cx - 13, head_cy - head_r - 3, 10, 12))
            pygame.draw.ellipse(self.screen, COLOR_DOG_EAR, (head_cx - 12, head_cy - head_r - 4, 10, 12))
            pygame.draw.ellipse(self.screen, COLOR_DOG_EAR_SHADE, (head_cx - 7, head_cy - head_r - 3, 10, 12))
            pygame.draw.ellipse(self.screen, COLOR_DOG_EAR, (head_cx - 6, head_cy - head_r - 4, 10, 12))
        if facing_right:
            pygame.draw.circle(self.screen, COLOR_DOG_EYE, (head_cx + 4, head_cy - 3), 2)
            pygame.draw.circle(self.screen, COLOR_DOG_EYE, (head_cx + 8, head_cy - 2), 2)
        else:
            pygame.draw.circle(self.screen, COLOR_DOG_EYE, (head_cx - 8, head_cy - 2), 2)
            pygame.draw.circle(self.screen, COLOR_DOG_EYE, (head_cx - 4, head_cy - 3), 2)
        leg_y = body_rect.bottom - 2
        for lx in [body_rect.x + 10, body_rect.right - 14]:
            pygame.draw.rect(self.screen, COLOR_DOG_BODY_DARK, (lx, leg_y, 6, 10), border_radius=2)

    def _draw_character_crying(self):
        """울면서 떨어질 때: 캐릭터 이미지 있으면 그대로, 없으면 기존 슬픈 도형"""
        cx = int(self.char_x)
        cy = int(self.char_y)
        facing_right = self.state.facing_right
        if self._char_image is not None:
            img = self._char_image if facing_right else self._char_image_left
            iw, ih = img.get_width(), img.get_height()
            self.screen.blit(img, (cx - iw // 2, cy))
            return
        # 폴백: 기존 슬픈 닥스훈트 (눈물 등)
        body_w, body_h = 44, 18
        head_r = 12
        body_rect = Rect(cx - body_w // 2, cy + 8, body_w, body_h)
        head_cx = cx + (body_w // 2 + head_r - 2) if facing_right else cx - body_w // 2 - head_r + 2
        head_cy = cy + 10 + body_h // 2
        draw_rect_vertical_gradient(self.screen, body_rect, COLOR_DOG_BODY, COLOR_DOG_BODY_DARK)
        pygame.draw.rect(self.screen, COLOR_CHAR_OUTLINE, body_rect, 1, border_radius=10)
        belly_r = Rect(body_rect.x + 4, body_rect.bottom - 8, body_rect.w - 8, 6)
        pygame.draw.rect(self.screen, COLOR_DOG_BELLY, belly_r, border_radius=3)
        pygame.draw.circle(self.screen, COLOR_CHAR_OUTLINE, (head_cx, head_cy), head_r + 1)
        pygame.draw.circle(self.screen, COLOR_DOG_BODY, (head_cx, head_cy), head_r)
        pygame.draw.circle(self.screen, COLOR_DOG_NOSE, (head_cx + (head_r - 2 if facing_right else -head_r + 2), head_cy), 5)
        if facing_right:
            pygame.draw.ellipse(self.screen, COLOR_DOG_EAR, (head_cx - 4, head_cy - head_r - 4, 10, 12))
            pygame.draw.ellipse(self.screen, COLOR_DOG_EAR, (head_cx + 2, head_cy - head_r - 4, 10, 12))
        else:
            pygame.draw.ellipse(self.screen, COLOR_DOG_EAR, (head_cx - 12, head_cy - head_r - 4, 10, 12))
            pygame.draw.ellipse(self.screen, COLOR_DOG_EAR, (head_cx - 6, head_cy - head_r - 4, 10, 12))
        for ex in [head_cx - 6, head_cx + 6]:
            pygame.draw.arc(self.screen, COLOR_DOG_EYE, (ex - 3, head_cy - 6, 6, 8), math.pi * 0.25, math.pi * 0.75, 2)
        tear_off = (int(self.fall_t * 12) % 8) - 4
        for tx in [head_cx - 5, head_cx + 5]:
            ty = head_cy + 2 + tear_off
            pygame.draw.circle(self.screen, COLOR_TEAR_SHINE, (tx, ty), 3)
            pygame.draw.circle(self.screen, COLOR_TEAR, (tx, ty), 2)
        leg_y = body_rect.bottom - 2
        for lx in [body_rect.x + 10, body_rect.right - 14]:
            pygame.draw.rect(self.screen, COLOR_DOG_BODY_DARK, (lx, leg_y, 6, 10), border_radius=2)

    def draw(self):
        self._draw_background()
        self._draw_stairs()
        # 화면 밖 점프 연출 중이거나 울면서 떨어질 때
        if self.jump_off_t is not None or self.falling:
            if self.falling:
                dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                dim.set_alpha(60)
                dim.fill((40, 45, 55))
                self.screen.blit(dim, (0, 0))
            self._draw_character_crying()
        else:
            self._draw_character()
        self._draw_particles()

        # UI 패널 (글래스·3D)
        bar_h = 10
        bar_y = 8
        bar_w = SCREEN_WIDTH - 48
        panel_rect = Rect(16, bar_y - 2, bar_w + 24, bar_h + 22)
        shadow_rect = Rect(panel_rect.x + 3, panel_rect.y + 3, panel_rect.w, panel_rect.h)
        shadow_s = pygame.Surface((shadow_rect.w + 4, shadow_rect.h + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_s, (*COLOR_UI_SHADOW, 90), (2, 2, shadow_rect.w, shadow_rect.h), border_radius=10)
        self.screen.blit(shadow_s, (shadow_rect.x - 2, shadow_rect.y - 2))
        draw_rounded_rect(self.screen, COLOR_UI_PANEL, panel_rect, 10)
        # 상단 하이라이트 (글래스 반사)
        hl_rect = Rect(panel_rect.x + 4, panel_rect.y + 2, panel_rect.w - 8, 3)
        draw_rect_vertical_gradient(self.screen, hl_rect, COLOR_UI_PANEL_TOP, COLOR_UI_PANEL)
        pygame.draw.rect(self.screen, COLOR_UI_PANEL_BORDER, panel_rect, 1, border_radius=10)
        # 타이머 바 (도형만: 배경 + 남은 시간만큼 초록→빨강 채움)
        bar_inner = Rect(22, bar_y + 1, bar_w, bar_h - 2)
        draw_rounded_rect(self.screen, COLOR_TIMER_BG, bar_inner, 4)
        if INITIAL_TIME > 0:
            fill = self.state.time_left / INITIAL_TIME
            fill = max(0, min(1.0, fill))
            w = int(bar_w * fill)
            if w > 0:
                if fill > 0.5:
                    t = (1.0 - fill) * 2
                    r = int(COLOR_TIMER_SAFE[0] + (COLOR_TIMER_MID[0] - COLOR_TIMER_SAFE[0]) * t)
                    g = int(COLOR_TIMER_SAFE[1] + (COLOR_TIMER_MID[1] - COLOR_TIMER_SAFE[1]) * t)
                    b = int(COLOR_TIMER_SAFE[2] + (COLOR_TIMER_MID[2] - COLOR_TIMER_SAFE[2]) * t)
                else:
                    t = 1.0 - fill * 2
                    r = int(COLOR_TIMER_MID[0] + (COLOR_TIMER_DANGER[0] - COLOR_TIMER_MID[0]) * t)
                    g = int(COLOR_TIMER_MID[1] + (COLOR_TIMER_DANGER[1] - COLOR_TIMER_MID[1]) * t)
                    b = int(COLOR_TIMER_MID[2] + (COLOR_TIMER_DANGER[2] - COLOR_TIMER_MID[2]) * t)
                bar_color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
                draw_rounded_rect(self.screen, bar_color, Rect(22, bar_y + 1, w, bar_h - 2), 4)
            pct = min(100, int(100 * self.state.time_left / INITIAL_TIME))
            pct_text = self.font.render(str(pct), True, COLOR_TEXT)
            self.screen.blit(pct_text, (22 + bar_w - pct_text.get_width(), bar_y + bar_h - 1))
        disp_score = max(0, self.state.score)
        if disp_score > self.high_score:
            self.high_score = disp_score
            save_highscore(self.high_score)
        score_str = f"Score {disp_score}  ·  Best {self.high_score}" if self._use_english_ui else f"현재 {disp_score}  ·  최고 {self.high_score}"
        score_text = self.font.render(score_str, True, COLOR_TEXT)
        self.screen.blit(score_text, (22, bar_y + bar_h + 4))
        # 조작 안내 (한 구석에 상시 표시, 작은 글씨)
        ctrl_str = "Space: Jump   Alt: Turn" if self._use_english_ui else "스페이스: 점프   Alt: 방향전환"
        ctrl_text = self.font.render(ctrl_str, True, COLOR_TEXT_SUB)
        self.screen.blit(ctrl_text, (22, bar_y + bar_h + 22))

        # 계단 마일스톤 메시지 (50 → 100 → 200 → 300...)
        if self.milestone_message and pygame.time.get_ticks() < self.milestone_until:
            msg_surf = self.font_big.render(self.milestone_message, True, (255, 255, 255))
            mw, mh = msg_surf.get_width(), msg_surf.get_height()
            pad_x, pad_y = 28, 14
            box = Rect(SCREEN_WIDTH // 2 - mw // 2 - pad_x, SCREEN_HEIGHT // 2 - mh // 2 - pad_y, mw + pad_x * 2, mh + pad_y * 2)
            panel = pygame.Surface((box.w, box.h))
            panel.set_alpha(200)
            panel.fill((40, 48, 65))
            self.screen.blit(panel, box.topleft)
            pygame.draw.rect(self.screen, (80, 90, 110), box, 1, border_radius=8)
            self.screen.blit(msg_surf, (SCREEN_WIDTH // 2 - mw // 2, SCREEN_HEIGHT // 2 - mh // 2))

        # 게임 오버 (연출: 흔들림 → 페이드인 → 텍스트 등장)
        if self.state.game_over and not self.falling:
            if self.game_over_effect_start is None:
                self.game_over_effect_start = pygame.time.get_ticks()
            cur = max(0, self.state.score)
            if cur > self.high_score:
                self.high_score = cur
                save_highscore(self.high_score)
            effect_t = (pygame.time.get_ticks() - self.game_over_effect_start) / 1000.0
            fade_t = max(0, effect_t - GAME_OVER_TEXT_APPEAR)
            overlay_alpha = int(min(210, 210 * min(1.0, effect_t / GAME_OVER_FADE_DURATION)))
            text_alpha = min(255, int(255 * min(1.0, fade_t / 0.25)))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(overlay_alpha)
            overlay.fill(COLOR_GAME_OVER_BG)
            self.screen.blit(overlay, (0, 0))
            reason = "Game Over"
            go_text = self.font_big.render(reason, True, COLOR_GAME_OVER_TEXT)
            go_score_str = f"Score  {cur}  ·  Best  {self.high_score}" if self._use_english_ui else f"최종 점수  {cur}  ·  최고  {self.high_score}"
            score_text = self.font_big.render(go_score_str, True, COLOR_GAME_OVER_TEXT)
            restart_str = "R: Restart  ·  ESC: Quit" if self._use_english_ui else "R: 다시하기  ·  ESC: 종료"
            restart_text = self.font.render(restart_str, True, COLOR_GAME_OVER_TEXT)
            cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
            if text_alpha > 0:
                go_text.set_alpha(text_alpha)
                score_text.set_alpha(text_alpha)
                restart_text.set_alpha(text_alpha)
                self.screen.blit(go_text, (cx - go_text.get_width() // 2, cy - 52))
                self.screen.blit(score_text, (cx - score_text.get_width() // 2, cy - 18))
                self.screen.blit(restart_text, (cx - restart_text.get_width() // 2, cy + 18))
            # 게임오버 시 왼쪽 종료, 오른쪽 다시시작 버튼
            if self._touch_buttons and text_alpha > 0:
                quit_lbl = "Quit" if self._use_english_ui else "종료"
                restart_lbl = "Restart" if self._use_english_ui else "다시시작"
                for rect, label in [(self._btn_quit, quit_lbl), (self._btn_restart, restart_lbl)]:
                    draw_rounded_rect(self.screen, (70, 130, 80), rect, 8)
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=8)
                    txt = self.font_big.render(label, True, (255, 255, 255))
                    self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        # 게임오버 직후 흔들림 (화면 전체)
        if self.state.game_over and not self.falling and self.game_over_effect_start is not None:
            effect_t = (pygame.time.get_ticks() - self.game_over_effect_start) / 1000.0
            if effect_t < GAME_OVER_SHAKE_DURATION:
                strength = 14 * (1 - effect_t / GAME_OVER_SHAKE_DURATION)
                shake_x = int((random.random() - 0.5) * 2 * strength)
                shake_y = int((random.random() - 0.5) * 2 * strength)
                copy = self.screen.copy()
                self.screen.fill(COLOR_GAME_OVER_BG)
                self.screen.blit(copy, (shake_x, shake_y))

        # Game Start 오버레이 (오프닝 직후: 커졌다 작아졌다 사라지는 이펙트)
        if self.game_start_until is not None and not self.state.game_over:
            now = pygame.time.get_ticks()
            if now < self.game_start_until:
                elapsed = (now - self.game_start_start) / 1000.0
                duration = 1.8
                t = min(1.0, elapsed / duration)
                if t < 0.2:
                    scale = 0.5 + (1.25 - 0.5) * (t / 0.2)
                elif t < 0.65:
                    scale = 1.25 + (1.0 - 1.25) * ((t - 0.2) / 0.45)
                else:
                    scale = 1.0 - (1.0 - 0.4) * ((t - 0.65) / 0.35)
                    scale = max(0.4, scale)
                alpha = 255 if t < 0.65 else int(255 * (1 - (t - 0.65) / 0.35))
                gs = self.font_title.render("Game Start", True, (255, 255, 255))
                gw, gh = gs.get_size()
                sw = max(1, int(gw * scale))
                sh = max(1, int(gh * scale))
                gs_scaled = pygame.transform.smoothscale(gs, (sw, sh))
                gs_scaled.set_alpha(alpha)
                gs_x = SCREEN_WIDTH // 2 - sw // 2
                gs_y = SCREEN_HEIGHT // 2 - sh // 2
                self.screen.blit(gs_scaled, (gs_x, gs_y))
                hint_str = "Space: Jump   Alt: Turn" if self._use_english_ui else "스페이스: 점프   Alt: 방향전환"
                hint = self.font_big.render(hint_str, True, (255, 255, 255))
                hint.set_alpha(alpha)
                self.screen.blit(hint, ((SCREEN_WIDTH - hint.get_width()) // 2, gs_y + sh + 16))
            else:
                self.game_start_until = None
        # 하단 터치 버튼 (왼쪽 방향전환, 오른쪽 점프)
        if self._touch_buttons:
            turn_lbl = "Turn" if self._use_english_ui else "방향전환"
            climb_lbl = "Jump" if self._use_english_ui else "점프"
            for rect, label in [(self._btn_turn, turn_lbl), (self._btn_climb, climb_lbl)]:
                draw_rounded_rect(self.screen, (70, 130, 80), rect, 10)
                pygame.draw.rect(self.screen, (50, 100, 60), rect, 2, border_radius=10)
                txt = self.font_big.render(label, True, (255, 255, 255))
                self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))
        pygame.display.flip()

    def _run_opening(self):
        """오프닝: title.png만 표시 (글자는 이미지에 포함) → 3초 페이드 아웃. (exe/동기용)"""
        opening_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        if self._title_image is not None:
            opening_surf.blit(self._title_image, (0, 0))
        else:
            opening_surf.fill((20, 20, 40))

        FADE_MS = 3000
        start_ticks = pygame.time.get_ticks()
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    return
            elapsed = pygame.time.get_ticks() - start_ticks
            if elapsed >= FADE_MS:
                break
            alpha = int(255 * (1 - elapsed / FADE_MS))
            opening_surf.set_alpha(alpha)
            self.screen.fill((0, 0, 0))
            self.screen.blit(opening_surf, (0, 0))
            pygame.display.flip()
            self.clock.tick(FPS)

    async def _run_opening_async(self):
        """오프닝 (웹용): 매 프레임 await 해서 브라우저가 그리기/이벤트 처리할 수 있게 함."""
        opening_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        if self._title_image is not None:
            opening_surf.blit(self._title_image, (0, 0))
        else:
            opening_surf.fill((20, 20, 40))

        import asyncio
        FADE_MS = 3000
        start_ticks = pygame.time.get_ticks()
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    return
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    return
            elapsed = pygame.time.get_ticks() - start_ticks
            if elapsed >= FADE_MS:
                break
            alpha = int(255 * (1 - elapsed / FADE_MS))
            opening_surf.set_alpha(alpha)
            self.screen.fill((0, 0, 0))
            self.screen.blit(opening_surf, (0, 0))
            pygame.display.flip()
            self.clock.tick(FPS)
            await asyncio.sleep(0)

    def run(self):
        self._run_opening()
        self._run_main_loop()

    def _run_main_loop(self):
        self.game_start_start = pygame.time.get_ticks()
        self.game_start_until = self.game_start_start + 1800
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and getattr(self, "_touch_buttons", False):
                    if self.state.game_over:
                        if self._btn_restart.collidepoint(e.pos):
                            self.state.reset()
                            self.anim = AnimState.IDLE
                            self.jump_landing_col = None
                            self.falling = False
                            self.jump_off_t = None
                            self.game_over_effect_start = None
                            self.last_milestone_announced = 0
                            self.milestone_message = None
                            self._particles = []
                            self._landing_shake_until = 0
                            self._update_char_pos_from_state()
                        elif self._btn_quit.collidepoint(e.pos):
                            pygame.quit()
                            sys.exit()
                    elif self._btn_climb.collidepoint(e.pos):
                        self.start_climb()
                    elif self._btn_turn.collidepoint(e.pos):
                        self.start_turn_and_climb()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if self.state.game_over:
                        if e.key == pygame.K_r:
                            self.state.reset()
                            self.anim = AnimState.IDLE
                            self.jump_landing_col = None
                            self.falling = False
                            self.jump_off_t = None
                            self.game_over_effect_start = None
                            self.last_milestone_announced = 0
                            self.milestone_message = None
                            self._particles = []
                            self._landing_shake_until = 0
                            self._update_char_pos_from_state()
                        continue
                    if e.key == pygame.K_SPACE:
                        self.start_climb()
                    elif e.key == pygame.K_LALT:
                        self.start_turn_and_climb()
            if not self.state.game_over:
                self.update(dt)
            self.draw()

    async def run_async(self):
        """웹(Pygbag)용: 한 프레임마다 브라우저에 제어권 반환."""
        import asyncio
        await self._run_opening_async()
        self.game_start_start = pygame.time.get_ticks()
        self.game_start_until = self.game_start_start + 1800
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    return
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self._touch_buttons:
                    if self.state.game_over:
                        if self._btn_restart.collidepoint(e.pos):
                            self.state.reset()
                            self.anim = AnimState.IDLE
                            self.jump_landing_col = None
                            self.falling = False
                            self.jump_off_t = None
                            self.game_over_effect_start = None
                            self.last_milestone_announced = 0
                            self.milestone_message = None
                            self._particles = []
                            self._landing_shake_until = 0
                            self._update_char_pos_from_state()
                        elif self._btn_quit.collidepoint(e.pos):
                            self._quit_requested = True
                    elif self._btn_climb.collidepoint(e.pos):
                        self.start_climb()
                    elif self._btn_turn.collidepoint(e.pos):
                        self.start_turn_and_climb()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    if self.state.game_over:
                        if e.key == pygame.K_r:
                            self.state.reset()
                            self.anim = AnimState.IDLE
                            self.jump_landing_col = None
                            self.falling = False
                            self.jump_off_t = None
                            self.game_over_effect_start = None
                            self.last_milestone_announced = 0
                            self.milestone_message = None
                            self._particles = []
                            self._landing_shake_until = 0
                            self._update_char_pos_from_state()
                        continue
                    if e.key == pygame.K_SPACE:
                        self.start_climb()
                    elif e.key == pygame.K_LALT:
                        self.start_turn_and_climb()
            if self._quit_requested:
                pygame.quit()
                return
            if not self.state.game_over:
                self.update(dt)
            self.draw()
            await asyncio.sleep(0)


if __name__ == "__main__":
    import asyncio
    async def main():
        app = GameApp()
        await app.run_async()
    asyncio.run(main())

