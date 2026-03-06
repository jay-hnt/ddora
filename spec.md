# 계단 점프 미니게임 - 기술 명세 (spec.md)

## 1. 기술 스택

- **언어**: Python 3.x
- **라이브러리**: Pygame 2.5+
- **실행**: `python main.py` 또는 `run_game.bat` 더블클릭
- **exe 빌드**: PyInstaller (선택, `build_exe.bat`)

## 2. 프로젝트 구조

```
stair_jump/
├── main.py          # 진입점, Pygame 루프, 렌더링, 입력 처리
├── game.py          # 게임 상태·로직 (GameState, Stair)
├── config.py        # 화면/게임 상수 (해상도, 열 수, 시간, 색상 등)
├── requirements.txt # pygame
├── run_game.bat     # 더블클릭 실행 (Windows)
├── build_exe.bat    # PyInstaller exe 빌드
├── prd.md           # 제품 요구사항
└── spec.md          # 본 기술 명세
```

## 3. 핵심 모듈/클래스

### 3.1 config.py

- **SCREEN_WIDTH / SCREEN_HEIGHT**: 480×720
- **COLS**: 5 (열 개수)
- **COL_WIDTH**: 열당 픽셀 폭
- **STAIR_HEIGHT / STAIR_WIDTH**: 계단 크기
- **JUMP_DURATION / MOVE_DURATION**: 점프·이동 애니메이션 길이(초)
- **INITIAL_TIME, MIN_TIME, TIME_DECREASE**: 시간 제한 초기값·최소값·감소량
- **LEVEL_SPEED_UP_EVERY, LEVEL_TIME_DECREASE_EXTRA**: 레벨업 시 추가 시간 감소
- **TIME_ITEM_CHANCE**: 시간 아이템 등장 확률
- **TIME_ITEM_BONUS**: 시간 아이템으로 추가되는 시간

### 3.2 game.py (연결된 계단)

- **Stair**: `col` (0~4), `has_time_item` (bool)
- **_next_stair_col(prev_col)**: 다음 계단은 **왼쪽 또는 오른쪽 한 칸**만 (prev_col ± 1, 제자리 없음)
- **GameState**:
  - `facing_right`: 진행 방향 (True=오른쪽, False=왼쪽)
  - `stair_list`: 연결된 계단 리스트. 다음 계단은 `_next_stair_col(마지막.col)`로만 생성.
  - `score`, `current_stair` / `next_stair`, `_ensure_next_stair()`
  - `get_landing_col_climb()`: 오르기 시 착지 열 (현재 방향으로 한 칸)
  - `get_landing_col_turn()`: 방향 전환 후 착지 열 (방향 뒤집고 한 칸)
  - `try_land(landing_col)`: 착지 판정. landing_col == next_stair.col 이면 성공.
  - `time_left` / `base_time`, `game_over`, `tick_time(dt)`

### 3.3 main.py

- **GameApp**: Pygame 창, 이벤트 루프, 업데이트·그리기
- **애니메이션 상태**: IDLE, JUMP_UP (대각선 점프만)
- **이징**: 점프 궤적 `ease_out_quad`. 점프 시 start_x/y → end_x/y 대각선 보간
- **좌표**: `col_to_x(col)`, `stair_y(row_index)` 로 열·행 → 픽셀 변환
- **렌더링**: 배경, 현재/다음 계단, 시간 아이템, 캐릭터, 타이머 바, 점수, 게임 오버 화면

## 4. 게임 로직 요약

1. **시작**: 중앙 열(2), `facing_right=True`, `stair_list = [첫 계단, 왼/오 한 칸 두 번째 계단]`
2. **계단 생성**: 다음 계단은 `_next_stair_col(이전.col)`로만 추가 (prev±1, 제자리 없음)
3. **매 프레임**: `state.tick_time(dt)`; 0 이하 시 게임 오버 (time)
4. **입력**: 스페이스/D/→ → 오르기 (`get_landing_col_climb()` 후 대각선 점프), A/← → 방향 전환 (`get_landing_col_turn()` 후 대각선 점프)
5. **점프 애니메이션**: JUMP_UP 시 `JUMP_DURATION` 동안 (start_x, start_y) → (end_x, end_y) 대각선 보간 후 `try_land(landing_col)` 호출
6. **착지**: `landing_col == next_stair.col` 이면 성공 → `score++`, 시간 갱신; 아니면 게임 오버 (wrong)
7. **시간 계산**: `get_time_for_level(score)` 로 점점 줄어드는 제한 시간

## 5. 의존성

- `pygame>=2.5.0` (requirements.txt)
- exe 빌드 시: `pyinstaller` (build_exe.bat에서 설치)

## 6. 업데이트 이력

- 최초 작성: 구조, config/game/main 역할, 로직·애니메이션·시간·아이템 명세 정리
