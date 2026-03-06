# -*- coding: utf-8 -*-
"""계단 점프 게임 - 무한의 계단 방식"""
import random
from typing import Optional
from config import COLS, INITIAL_TIME, TIME_ITEM_BONUS, TIME_ITEM_CHANCE


class Stair:
    __slots__ = ('col', 'has_time_item')

    def __init__(self, col: int, has_time_item: bool = False):
        self.col = col
        self.has_time_item = has_time_item


def _next_stair_col(prev_col: int, prev_prev_col: Optional[int], level: int) -> int:
    """다음 계단 열. level이 올라갈수록 방향 전환 빈도 증가 (난이도 상승)."""
    if prev_col <= 0:
        return 1
    if prev_col >= COLS - 1:
        return COLS - 2
    if prev_prev_col is None:
        return prev_col + random.choice([-1, 1])
    # 같은 방향 열 vs 반대 방향 열
    same_col = max(0, min(COLS - 1, 2 * prev_col - prev_prev_col))
    if same_col == prev_col:
        return prev_col + (1 if prev_col == 0 else -1)
    other_col = prev_col - 1 if same_col == prev_col + 1 else prev_col + 1
    other_col = max(0, min(COLS - 1, other_col))
    # 50, 100, 200, 300... 기준으로 단계적으로 어려워짐 (같은 방향 유지 확률 감소)
    if level < 50:
        p_same = 0.85
    elif level < 100:
        p_same = 0.85 - (level - 50) / 50 * 0.06   # 0.85 → 0.79
    elif level < 200:
        p_same = 0.79 - (level - 100) / 100 * 0.10  # 0.79 → 0.69
    elif level < 300:
        p_same = 0.69 - (level - 200) / 100 * 0.08  # 0.69 → 0.61
    elif level < 400:
        p_same = 0.61 - (level - 300) / 100 * 0.08  # 0.61 → 0.53
    else:
        p_same = max(0.38, 0.53 - (level - 400) / 100 * 0.06)
    return same_col if random.random() < p_same else other_col


class GameState:
    def __init__(self):
        self.stair_list = []
        self.reset()

    def reset(self):
        self.score = -1
        self.facing_right = True
        self.stair_list = []
        self.stair_list.append(Stair(COLS // 2, random.random() < TIME_ITEM_CHANCE))
        for i in range(58):
            prev = self.stair_list[-1]
            prev_prev = self.stair_list[-2].col if len(self.stair_list) >= 2 else None
            level = len(self.stair_list)
            self.stair_list.append(Stair(_next_stair_col(prev.col, prev_prev, level), random.random() < TIME_ITEM_CHANCE))
        self.start_col = self.stair_list[0].col - 1
        self.time_left = INITIAL_TIME  # 연속 감소만, 계단마다 초기화 안 함
        self.game_over = False
        self.game_over_reason = ""

    @property
    def current_stair(self):
        if self.score < 0 or self.score >= len(self.stair_list):
            return None
        return self.stair_list[self.score]

    @property
    def next_stair(self):
        idx = self.score + 1
        if idx < len(self.stair_list):
            return self.stair_list[idx]
        return None

    def current_col(self):
        """현재 캐릭터 열 (score=-1일 때 start_col, 아니면 current_stair.col)"""
        if self.score == -1:
            return self.start_col
        if self.current_stair is not None:
            return self.current_stair.col
        return COLS // 2

    def _ensure_next_stair(self):
        """앞으로 올 계단을 미리 만들어 두기 (화면에 계속 보이게)"""
        while len(self.stair_list) <= self.score + 25:
            prev = self.stair_list[-1]
            prev_prev = self.stair_list[-2].col if len(self.stair_list) >= 2 else None
            level = len(self.stair_list)
            self.stair_list.append(Stair(_next_stair_col(prev.col, prev_prev, level), random.random() < TIME_ITEM_CHANCE))

    def get_landing_col_climb(self) -> int:
        c = self.current_col()
        return c + (1 if self.facing_right else -1)

    def get_landing_col_turn(self) -> int:
        self.facing_right = not self.facing_right
        return self.get_landing_col_climb()

    def try_land(self, landing_col: int):
        """착지 처리. 시간은 여기서 절대 초기화하지 않음. 꽃 먹을 때만 소폭 추가."""
        if self.game_over:
            return False, False
        self._ensure_next_stair()
        if landing_col < 0 or landing_col >= COLS:
            self.game_over = True
            self.game_over_reason = "wrong"
            return False, False
        next_idx = self.score + 1
        next_s = self.stair_list[next_idx]
        if landing_col != next_s.col:
            self.game_over = True
            self.game_over_reason = "wrong"
            return False, False
        got_item = next_s.has_time_item
        if got_item:
            next_s.has_time_item = False
            self.time_left += TIME_ITEM_BONUS  # 꽃일 때만 추가, 계단 올라갈 때마다 초기화 없음
        self.score = next_idx
        self._ensure_next_stair()
        return True, got_item

    def _time_speed_factor(self) -> float:
        """50, 100, 200, 300... 기준으로 단계적으로 시간이 더 빨리 줄어드는 배율."""
        s = max(0, self.score)
        if s < 50:
            return 1.0
        if s < 100:
            return 1.0 + (s - 50) / 50 * 0.04   # 1.0 → 1.04
        if s < 200:
            return 1.04 + (s - 100) / 100 * 0.06  # 1.04 → 1.10
        if s < 300:
            return 1.10 + (s - 200) / 100 * 0.06  # 1.10 → 1.16
        if s < 400:
            return 1.16 + (s - 300) / 100 * 0.06  # 1.16 → 1.22
        return min(2.0, 1.22 + (s - 400) / 100 * 0.05)

    def tick_time(self, dt: float):
        """매 프레임 호출. 계단 많이 오를수록 시간이 더 빨리 감소."""
        if self.game_over:
            return
        self.time_left -= dt * self._time_speed_factor()
        if self.time_left <= 0:
            self.game_over = True
            self.game_over_reason = "time"
