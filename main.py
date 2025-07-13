import pygame
import random
import math

# --- 1. 초기 설정 및 상수 정의 ---
pygame.init()

# 화면 크기
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Advanced Shooting Game")

# 색상
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# 게임 설정
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

consecutive_item_xp_bonus = 0 # 전역 변수로 선언 및 초기화

# --- 2. 게임 객체 클래스 정의 ---

# --- 2. 게임 객체 클래스 정의 ---

UPGRADE_OPTIONS = {
    "speed": {"name": "Move Speed", "max_level": 6},
    "power": {"name": "Attack Power", "max_level": 6},
    "firerate": {"name": "Fire Rate", "max_level": 6},
    "resistance": {"name": "Damage Resist", "max_level": 6},
    "submissile": {"name": "Sub Missile", "max_level": 6},
}

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        points = [(25, 0), (0, 40), (20, 50), (30, 50), (50, 40)]
        pygame.draw.polygon(self.image, GREEN, points)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50))
        
        # 기본 능력치 및 레벨 시스템
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = self.level * 10
        
        # 업그레이드 레벨
        self.upgrade_levels = {key: 0 for key in UPGRADE_OPTIONS}

        # 발사 딜레이 관련
        self.last_shot_time = 0
        self.last_sub_missile_time = 0
        self.shield_active_timer = 0 # 방어막 활성화 타이머 (밀리초)
        
        self.recalculate_stats()

    def recalculate_stats(self):
        # 업그레이드 레벨에 따라 실제 능력치 계산
        self.speed = 5 + (self.upgrade_levels["speed"] * 0.5)
        self.attack_power = 1 + (self.upgrade_levels["power"] * 0.5)
        self.fire_cooldown = 500 - (self.upgrade_levels["firerate"] * 50)
        self.invulnerability_duration = self.upgrade_levels["resistance"] * 500 # 레벨당 0.5초 무적
        self.sub_missile_cooldown = 6000 - (self.upgrade_levels["submissile"] * 500)

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_to_next_level:
            self.level += 1
            self.xp -= self.xp_to_next_level
            self.xp_to_next_level = self.level * 5
            self.recalculate_stats()
            return True # 레벨업 했음을 알림
        return False

    def update(self):
        # 이동
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
        # 보조 미사일 자동 발사
        now = pygame.time.get_ticks()
        if self.upgrade_levels["submissile"] > 0:
            if now - self.last_sub_missile_time > self.sub_missile_cooldown:
                self.last_sub_missile_time = now
                sub_missile = SubMissile(self.rect.center)
                all_sprites.add(sub_missile)
                bullets.add(sub_missile)

        # 방어막 타이머 감소
        if self.shield_active_timer > 0:
            self.shield_active_timer -= clock.get_time()
            if self.shield_active_timer < 0:
                self.shield_active_timer = 0

    def draw_aux_ship(self, surface):
        # 보조 기체 그리기 (플레이어 옆에 작은 삼각형)
        aux_ship_size = 20
        # 왼쪽 보조 기체
        points_left = [            (self.rect.left - aux_ship_size, self.rect.centery),            (self.rect.left - aux_ship_size + aux_ship_size // 2, self.rect.centery - aux_ship_size),            (self.rect.left - aux_ship_size + aux_ship_size, self.rect.centery)        ]
        pygame.draw.polygon(surface, GREEN, points_left)

        # 오른쪽 보조 기체
        points_right = [            (self.rect.right + aux_ship_size, self.rect.centery),            (self.rect.right + aux_ship_size - aux_ship_size // 2, self.rect.centery - aux_ship_size),            (self.rect.right + aux_ship_size - aux_ship_size, self.rect.centery)        ]
        pygame.draw.polygon(surface, GREEN, points_right)

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.fire_cooldown:
            self.last_shot_time = now
            # 미사일 레벨은 이제 아이템이 아닌 보조적인 개념으로 남겨두거나, 다른 방식으로 활용 가능
            # 여기서는 기존 로직을 유지하되, 공격력은 self.attack_power를 따르도록 함
            if player.missile_level == 1:
                self.create_bullet(0)
            elif player.missile_level == 2:
                self.create_bullet(0, offset_x=-15)
                self.create_bullet(0, offset_x=15)
            elif player.missile_level == 3:
                self.create_bullet(0); self.create_bullet(-30); self.create_bullet(30)
            elif player.missile_level == 4:
                self.create_bullet(-30); self.create_bullet(-10); self.create_bullet(10); self.create_bullet(30)
            else: # 5레벨 이상
                self.create_bullet(0); self.create_bullet(-15); self.create_bullet(15); self.create_bullet(-45); self.create_bullet(45)

    def create_bullet(self, angle, offset_x=0):
        bullet = Bullet(self.rect.centerx + offset_x, self.rect.top, angle, self.attack_power)
        all_sprites.add(bullet)
        bullets.add(bullet)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, damage):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        
        # 데미지에 따라 색상 변경
        if damage < 2:
            bullet_color = BLUE
        elif damage < 3:
            bullet_color = (0, 200, 255) # 밝은 파랑
        elif damage < 4:
            bullet_color = (0, 255, 200) # 청록
        elif damage < 5:
            bullet_color = GREEN
        else:
            bullet_color = YELLOW

        pygame.draw.circle(self.image, bullet_color, (5, 5), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        self.angle = math.radians(angle)
        self.damage = damage

    def update(self):
        self.rect.y -= self.speed * math.cos(self.angle)
        self.rect.x -= self.speed * math.sin(self.angle)
        if self.rect.bottom < 0 or self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.kill()

class SubMissile(pygame.sprite.Sprite):
    def __init__(self, center_pos):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.rect(self.image, YELLOW, (0, 0, 12, 12))
        self.rect = self.image.get_rect(center=center_pos)
        self.speed = 5
        self.damage = 2 # 보조 미사일은 고정 데미지
        
        # 가장 가까운 적을 찾아 방향 설정
        closest_enemy = self.find_closest_enemy()
        if closest_enemy:
            direction = pygame.math.Vector2(closest_enemy.rect.center) - pygame.math.Vector2(self.rect.center)
            self.velocity = direction.normalize() * self.speed
        else:
            self.velocity = pygame.math.Vector2(0, -self.speed) # 적이 없으면 위로

    def find_closest_enemy(self):
        if not enemies:
            return None
        return min(enemies, key=lambda e: pygame.math.Vector2(e.rect.center).distance_to(self.rect.center))

    def update(self):
        self.rect.move_ip(self.velocity)
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, health):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        # 적 우주선 모양 정의
        points = [(0, 0), (40, 0), (35, 35), (20, 40), (5, 35)]
        pygame.draw.polygon(self.image, RED, points)
        self.rect = self.image.get_rect(center=(random.randint(20, SCREEN_WIDTH - 20), -20))
        self.speed = random.randint(1, 3)
        self.max_health = health
        self.health = health

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def draw_health_bar(self, surface):
        if self.health < self.max_health:
            bar_width = self.rect.width * (self.health / self.max_health)
            bar_height = 5
            pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 10, bar_width, bar_height))
            pygame.draw.rect(surface, WHITE, (self.rect.x, self.rect.y - 10, self.rect.width, bar_height), 1)


class Item(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        # 간단한 별 모양 그리기 (pygame.draw.star가 없으므로 polygon으로 대체)
        points = [(15,0), (20,10), (30,10), (22,18), (25,30), (15,22), (5,30), (8,18), (0,10), (10,10)]
        pygame.draw.polygon(self.image, YELLOW, points)
        self.rect = self.image.get_rect(center=(random.randint(15, SCREEN_WIDTH - 15), -15))
        self.speed = 4

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.randint(1, 3)
        self.color = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = random.randint(-20, 0) # 화면 위에서 다시 시작
            self.x = random.randint(0, SCREEN_WIDTH)
            self.size = random.randint(1, 3)
            self.speed = random.randint(1, 3)
            self.color = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))

    def draw(self, surface):
        # 반짝이는 효과 (크기나 밝기 조절)
        if random.random() < 0.05: # 5% 확률로 반짝임
            pygame.draw.circle(surface, (255, 255, 255), (self.x, self.y), self.size + 1)
        else:
            pygame.draw.circle(surface, self.color, (self.x, self.y), self.size)

# --- 3. 게임 초기화 및 전역 변수 ---
def reset_game():
    global all_sprites, enemies, bullets, items, player, score, enemy_base_health
    global start_time, last_health_increase_time, last_item_spawn_time, last_enemy_spawn_time
    global enemies_per_spawn, killed_enemies, game_state, available_upgrades, consecutive_item_xp_bonus, stars

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    items = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)
    player.missile_level = 1 # 미사일 레벨 초기화
    player.shield_active_timer = 0 # 방어막 타이머 초기화

    score = 0
    killed_enemies = 0
    enemy_base_health = 1
    enemies_per_spawn = 1
    available_upgrades = []

    consecutive_item_xp_bonus = 0 # 초기화 위치 변경

    start_time = pygame.time.get_ticks()
    last_health_increase_time = start_time
    last_item_spawn_time = start_time
    last_enemy_spawn_time = start_time
    
    game_state = "playing"

    # 별 초기화
    stars = [Star() for _ in range(100)] # 100개의 별 생성

def get_upgrade_options():
    # 6레벨 미만인 업그레이드 목록 필터링
    options = [key for key, data in UPGRADE_OPTIONS.items() if player.upgrade_levels[key] < data["max_level"]]
    # 목록에서 3개 무작위 선택
    return random.sample(options, min(len(options), 3))

def show_level_up_screen():
    global game_state, available_upgrades
    
    screen.fill(BLACK)
    title_font = pygame.font.Font(None, 60)
    option_font = pygame.font.Font(None, 42)

    title_text = title_font.render("LEVEL UP!", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, SCREEN_HEIGHT/4 - 50))

    # 업그레이드 선택지 버튼 표시
    mouse_x, mouse_y = pygame.mouse.get_pos()
    for i, key in enumerate(available_upgrades):
        button_rect = pygame.Rect(SCREEN_WIDTH/2 - 150, SCREEN_HEIGHT/2 - 50 + i * 70, 300, 50)
        button_color = (50, 50, 100)
        if button_rect.collidepoint(mouse_x, mouse_y):
            button_color = (80, 80, 150)
        
        pygame.draw.rect(screen, button_color, button_rect)
        option_text = option_font.render(UPGRADE_OPTIONS[key]["name"], True, WHITE)
        screen.blit(option_text, (button_rect.centerx - option_text.get_width()/2, button_rect.centery - option_text.get_height()/2))

    pygame.display.flip()

    # 선택지 클릭 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, key in enumerate(available_upgrades):
                button_rect = pygame.Rect(SCREEN_WIDTH/2 - 150, SCREEN_HEIGHT/2 - 50 + i * 70, 300, 50)
                if button_rect.collidepoint(mouse_x, mouse_y):
                    player.upgrade_levels[key] += 1
                    player.recalculate_stats()
                    game_state = "playing"
                    return "continue"
    return "level_up"

def show_game_over_screen():
    screen.fill(BLACK)
    title_font = pygame.font.Font(None, 74)
    info_font = pygame.font.Font(None, 48)

    title_text = title_font.render("GAME OVER", True, WHITE)
    score_text = info_font.render(f"Score: {score}", True, WHITE)
    killed_text = info_font.render(f"Killed: {killed_enemies}", True, WHITE)
    
    screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, SCREEN_HEIGHT/4))
    screen.blit(score_text, (SCREEN_WIDTH/2 - score_text.get_width()/2, SCREEN_HEIGHT/2 - 50))
    screen.blit(killed_text, (SCREEN_WIDTH/2 - killed_text.get_width()/2, SCREEN_HEIGHT/2))

    # Restart 버튼
    mouse_x, mouse_y = pygame.mouse.get_pos()
    restart_button = pygame.Rect(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT * 0.7, 200, 50)
    
    button_color = (100, 100, 100)
    if restart_button.collidepoint(mouse_x, mouse_y):
        button_color = (150, 150, 150)

    pygame.draw.rect(screen, button_color, restart_button)
    restart_text = font.render("Restart", True, WHITE)
    screen.blit(restart_text, (restart_button.centerx - restart_text.get_width()/2, restart_button.centery - restart_text.get_height()/2))
    
    pygame.display.flip()

    # 재시작 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.mouse.get_pressed()[0]: # 마우스 왼쪽 버튼 클릭
            if restart_button.collidepoint(mouse_x, mouse_y):
                return "restart"
    return "game_over"
    screen.fill(BLACK)
    title_font = pygame.font.Font(None, 74)
    info_font = pygame.font.Font(None, 48)

    title_text = title_font.render("GAME OVER", True, WHITE)
    score_text = info_font.render(f"Score: {score}", True, WHITE)
    killed_text = info_font.render(f"Killed: {killed_enemies}", True, WHITE)
    
    screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, SCREEN_HEIGHT/4))
    screen.blit(score_text, (SCREEN_WIDTH/2 - score_text.get_width()/2, SCREEN_HEIGHT/2 - 50))
    screen.blit(killed_text, (SCREEN_WIDTH/2 - killed_text.get_width()/2, SCREEN_HEIGHT/2))

    # Restart 버튼
    mouse_x, mouse_y = pygame.mouse.get_pos()
    restart_button = pygame.Rect(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT * 0.7, 200, 50)
    
    button_color = (100, 100, 100)
    if restart_button.collidepoint(mouse_x, mouse_y):
        button_color = (150, 150, 150)

    pygame.draw.rect(screen, button_color, restart_button)
    restart_text = font.render("Restart", True, WHITE)
    screen.blit(restart_text, (restart_button.centerx - restart_text.get_width()/2, restart_button.centery - restart_text.get_height()/2))
    
    pygame.display.flip()

    # 재시작 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.MOUSEBUTTONDOWN:
            if restart_button.collidepoint(mouse_x, mouse_y):
                return "restart"
    return "game_over"


# --- 4. 메인 게임 루프 ---
game_state = "playing"
reset_game() # 게임 첫 시작
running = True
while running:
    if game_state == "playing":
        clock.tick(60)
        current_time = pygame.time.get_ticks()

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            player.shoot()

        # --- 게임 로직 ---
        elapsed_time_seconds = (current_time - start_time) / 1000

        # 1. 2초마다 적 생성 (20초마다 생성량 증가)
        if current_time - last_enemy_spawn_time > 2000:
            for _ in range(enemies_per_spawn):
                enemy = Enemy(enemy_base_health)
                all_sprites.add(enemy)
                enemies.add(enemy)
            last_enemy_spawn_time = current_time

        # 20초마다 생성되는 적의 수 증가
        if elapsed_time_seconds > enemies_per_spawn * 20:
            enemies_per_spawn += 1

        # 2. 10초마다 적 체력 증가
        if current_time - last_health_increase_time > 10000:
            enemy_base_health += 1
            last_health_increase_time = current_time

        # 3. 15초마다 아이템 등장 (미사일 레벨업)
        if current_time - last_item_spawn_time > 15000:
            item = Item()
            all_sprites.add(item)
            items.add(item)
            last_item_spawn_time = current_time

        # 스프라이트 업데이트
        all_sprites.update()

        # 충돌 감지
        # 총알과 적 충돌
        hits = pygame.sprite.groupcollide(bullets, enemies, False, False) # 총알이 관통하도록 False
        for bullet, hit_enemies in hits.items():
            for enemy in hit_enemies:
                enemy.health -= bullet.damage
                if enemy.health <= 0:
                    enemy.kill()
                    score += 100 * enemy.max_health
                    killed_enemies += 1
                    if player.gain_xp(1):
                        available_upgrades = get_upgrade_options()
                        if available_upgrades:
                            game_state = "level_up"
            bullet.kill() # 총알은 한 번 충돌하면 사라지도록

        # 플레이어와 아이템 충돌
        hits = pygame.sprite.spritecollide(player, items, True)
        for hit in hits:
            if player.missile_level < 5:
                player.missile_level += 1
                consecutive_item_xp_bonus = 0 # 미사일 레벨업 시 보너스 초기화
            else:
                consecutive_item_xp_bonus += 5 # 연속 획득 보너스 증가
                if player.gain_xp(consecutive_item_xp_bonus):
                    available_upgrades = get_upgrade_options()
                    if available_upgrades:
                        game_state = "level_up"

        # 아이템이 화면 아래로 사라지면 연속 획득 보너스 초기화
        # (충돌하지 않고 사라진 아이템에 대해서만 적용)
        for item in items:
            if item.rect.top > SCREEN_HEIGHT:
                item.kill() # 화면 밖으로 나간 아이템 제거
                consecutive_item_xp_bonus = 0 # 보너스 초기화

        # 플레이어와 적 충돌 (게임 오버 또는 무적 발동)
        hits = pygame.sprite.spritecollide(player, enemies, False)
        if hits:
            if player.shield_active_timer > 0: # 현재 무적 상태라면
                for enemy in hits:
                    enemy.kill()
                    killed_enemies += 1
                    score += 50 # 무적 상태에서 적 제거 시 점수 보너스
            else: # 무적 상태가 아니라면
                if player.upgrade_levels["resistance"] > 0: # 방어 업그레이드가 있다면 무적 발동
                    player.shield_active_timer = player.invulnerability_duration
                    for enemy in hits:
                        enemy.kill()
                        killed_enemies += 1
                        score += 50 # 무적 발동 시 적 제거 및 점수 보너스
                else: # 방어 업그레이드가 없다면 게임 오버
                    game_state = "game_over"

        # --- 그리기 ---
        screen.fill(BLACK)
        
        # 별 그리기
        for star in stars:
            star.update()
            star.draw(screen)

        all_sprites.draw(screen)

        # 보조 기체 그리기
        if player.upgrade_levels["submissile"] > 0:
            player.draw_aux_ship(screen)

        # 방어막 그리기
        if player.shield_active_timer > 0:
            shield_surface = pygame.Surface((player.rect.width * 1.5, player.rect.height * 1.5), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 255, 255, 100), (shield_surface.get_width()/2, shield_surface.get_height()/2), player.rect.width * 0.7)
            screen.blit(shield_surface, (player.rect.centerx - shield_surface.get_width()/2, player.rect.centery - shield_surface.get_height()/2))

        for enemy in enemies:
            enemy.draw_health_bar(screen)

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        level_text = font.render(f"Missile LV: {player.missile_level}", True, WHITE)
        screen.blit(level_text, (10, 50))

        enemy_health_text = font.render(f"Enemy HP: x{enemy_base_health}", True, WHITE)
        screen.blit(enemy_health_text, (SCREEN_WIDTH - enemy_health_text.get_width() - 10, 10))
        
        # XP 바 그리기
        if player.xp_to_next_level > 0:
            xp_bar_width = SCREEN_WIDTH * (player.xp / player.xp_to_next_level)
            pygame.draw.rect(screen, (100, 0, 100), (0, SCREEN_HEIGHT - 10, SCREEN_WIDTH, 10))
            pygame.draw.rect(screen, (200, 0, 200), (0, SCREEN_HEIGHT - 10, xp_bar_width, 10))
        level_text_hud = font.render(f"LV: {player.level}", True, WHITE)
        screen.blit(level_text_hud, (10, SCREEN_HEIGHT - 45))

        pygame.display.flip()

    elif game_state == "level_up":
        result = show_level_up_screen()
        if result == "quit":
            running = False

    elif game_state == "game_over":
        result = show_game_over_screen()
        if result == "quit":
            running = False
        elif result == "restart":
            reset_game()

# --- 5. 게임 종료 ---
pygame.quit()
