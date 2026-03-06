# 계단 점프 (Stair Jump)

시중의 **무한의 계단 오르기**와 같은 방식의 미니게임입니다. 캐릭터는 진행 방향(왼/오)만 가지며, 그 방향으로 대각선 점프해서 한 칸씩 올라갑니다.

## 실행 방법

1. **Python 설치** 후 터미널에서:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```
2. **더블클릭**: `run_game.bat` 더블클릭 (Python·pygame이 설치된 환경)
3. **exe로 실행**: `build_exe.bat` 실행 후 생성된 `dist\StairJump.exe` 더블클릭

## 다른 사람에게 공유하는 방법 (링크/파일 하나만)

### 방법 A: 파일 하나만 보내기 (가장 간단, 추천)

1. **본인 PC에서** `stair_jump` 폴더 안에서 **`build_exe.bat`** 더블클릭  
   → 처음이면 1~2분 걸릴 수 있음  
2. 완료되면 **`dist`** 폴더 안에 **`StairJump.exe`** 가 생성됨  
3. **그 exe 파일 하나만** 상대방에게 전달 (이메일·카톡·USB 등)  
4. **받는 사람**: **StairJump.exe 더블클릭**만 하면 게임 실행 (Python 설치 불필요, Windows만 해당)

- 선택: `실행방법_받는사람용.txt` 를 exe와 함께 보내면 조작법을 안내할 수 있음  
- **정리**: 상대방에게 건네는 건 **StairJump.exe 하나**면 충분함  

### 방법 B: 폴더 통째로 보내기

- `stair_jump` 폴더를 zip으로 압축해서 전달  
- 받는 사람은 **Python 설치** 후 `pip install -r requirements.txt` → **`run_game.bat`** 더블클릭

### 방법 C: GitHub에 올리고 링크로 공유

1. **GitHub에서 저장소 만들기**  
   [github.com](https://github.com) 로그인 → **New repository** → 이름 예: `stair-jump` → Create.

2. **프로젝트 올리기** (처음 한 번)
   ```bash
   cd stair_jump
   git init
   git add .
   git commit -m "계단 점프 게임"
   git branch -M main
   git remote add origin https://github.com/본인아이디/stair-jump.git
   git push -u origin main
   ```

3. **exe 빌드**  
   `build_exe.bat` 실행 → `dist\StairJump.exe` 생성.

4. **Release로 exe 올리기**  
   GitHub 저장소 페이지 → **Releases** → **Create a new release**  
   - Tag: `v1.0` (또는 원하는 버전)  
   - Release title: `v1.0 - 다운로드`  
   - **Attach binaries** 에서 `StairJump.exe` 파일 선택 후 업로드  
   - **Publish release** 클릭

5. **공유할 링크**  
   Release 페이지 주소를 상대방에게 보내면 됨.  
   예: `https://github.com/본인아이디/stair-jump/releases`  
   → 받는 사람은 여기서 **StairJump.exe** 다운로드 후 더블클릭.

- **정리**: GitHub에 코드 올려두고, Release에 exe만 올리면 **한 링크**로 코드·다운로드 모두 공유 가능.

### 방법 D: 웹에서 링크 하나로 실행

- [Pygbag](https://pygame-web.github.io/)으로 브라우저용 빌드 후 [itch.io](https://itch.io) 등에 올리면 **링크만 보내서** 브라우저에서 바로 플레이 가능 (설정 필요)

## 조작

- **스페이스**: **오르기** — 현재 방향으로 한 칸 올라감
- **왼쪽 Alt**: **방향 전환** — 방향을 바꾸고 그 방향으로 한 칸 올라감
- **R**: 게임 오버 후 재시작
- **ESC**: 종료

## 규칙

- 다음 계단은 항상 **현재 계단의 왼쪽 또는 오른쪽** 한 칸에만 있습니다.
- **오르기**는 현재 보는 방향으로, **방향 전환**은 반대 방향으로 한 칸 올라갑니다.
- 잘못된 방향으로 점프하거나 시간 안에 올라가지 못하면 게임 오버입니다.
- 파란색 아이템이 있는 계단에 올라가면 제한 시간이 늘어납니다.

요구사항·기술 명세는 `prd.md`, `spec.md`를 참고하세요.
