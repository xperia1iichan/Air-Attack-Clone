"""
AIR ATTACK - a 2D air-combat shooter built with pygame.

Controls:
    Arrows / WASD ... move
    Space ........... fire
    P or Esc ........ pause
    Enter ........... start / restart

Install:  pip install pygame
"""

import sys
import math
import random

import pygame

# ------------------------------------------------------------------ setup
pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Air Attack")
clock = pygame.time.Clock()

# ------------------------------------------------------------------ colors
NIGHT   = (12, 16, 30)
WHITE   = (240, 245, 255)
CYAN    = (90, 220, 255)
BLUE    = (55, 110, 210)
RED     = (235, 70, 70)
ORANGE  = (255, 160, 50)
YELLOW  = (255, 220, 90)
GREEN   = (90, 230, 130)
MAGENTA = (220, 100, 230)
GREY    = (110, 120, 140)

font_s = pygame.font.SysFont("consolas", 18)
font_m = pygame.font.SysFont("consolas", 26, bold=True)
font_l = pygame.font.SysFont("consolas", 56, bold=True)


# ------------------------------------------------------------------ helpers
def make_stars(n=110):
    """A scrolling starfield: [x, y, speed, radius]."""
    return [[random.uniform(0, WIDTH), random.uniform(0, HEIGHT),
             random.uniform(0.6, 3.2), random.randint(1, 2)] for _ in range(n)]


# ------------------------------------------------------------------ entities
class Bullet:
    def __init__(self, x, y, vx, vy, color=CYAN, dmg=1, friendly=True):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.color = color
        self.dmg = dmg
        self.friendly = friendly
        self.dead = False

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if (self.y < -25 or self.y > HEIGHT + 25 or
                self.x < -25 or self.x > WIDTH + 25):
            self.dead = True

    def draw(self, surf):
        tail = (self.x - self.vx * 0.7, self.y - self.vy * 0.7)
        pygame.draw.line(surf, self.color, (self.x, self.y), tail, 3)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), 2)


class Particle:
    def __init__(self, x, y, color):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.0, 6.0)
        self.x, self.y = float(x), float(y)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.r = random.randint(2, 4)
        self.life = random.randint(18, 40)
        self.max_life = self.life
        self.dead = False

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.96
        self.vy = self.vy * 0.96 + 0.06      # slight gravity
        self.life -= 1
        if self.life <= 0:
            self.dead = True

    def draw(self, surf):
        t = self.life / self.max_life
        col = tuple(int(c * t) for c in self.color)
        radius = max(1, int(self.r * t))
        pygame.draw.circle(surf, col, (int(self.x), int(self.y)), radius)


class PowerUp:
    KINDS = ("power", "shield", "life")

    def __init__(self, x, y):
        self.kind = random.choices(self.KINDS, weights=(6, 3, 1))[0]
        self.x, self.y = float(x), float(y)
        self.t = 0.0
        self.vy = 1.8
        self.dead = False
        self.rect = pygame.Rect(0, 0, 26, 26)
        self.rect.center = (int(self.x), int(self.y))

    def update(self):
        self.t += 0.1
        self.y += self.vy
        self.rect.center = (int(self.x + math.sin(self.t) * 10), int(self.y))
        if self.y > HEIGHT + 30:
            self.dead = True

    def draw(self, surf):
        color = {"power": CYAN, "shield": GREEN, "life": RED}[self.kind]
        label = {"power": "P", "shield": "S", "life": "+"}[self.kind]
        pygame.draw.circle(surf, color, self.rect.center, 13, 2)
        pygame.draw.circle(surf, color, self.rect.center, 8)
        txt = font_s.render(label, True, NIGHT)
        surf.blit(txt, txt.get_rect(center=self.rect.center))


class Player:
    W, H = 46, 46

    def __init__(self):
        self.rect = pygame.Rect(0, 0, self.W, self.H)
        self.rect.center = (WIDTH // 2, HEIGHT - 70)
        self.speed = 6.0
        self.lives = 3
        self.power = 1          # 1 = single, 2 = twin, 3 = spread
        self.cooldown = 0
        self.invuln = 90        # frames of blinking invulnerability
        self.shield = 0         # frames of shield

    def update(self):
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - \
             (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - \
             (keys[pygame.K_UP] or keys[pygame.K_w])
        if dx and dy:                       # normalise diagonals
            dx *= 0.7071
            dy *= 0.7071

        self.rect.x += int(dx * self.speed)
        self.rect.y += int(dy * self.speed)
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        if self.cooldown > 0:
            self.cooldown -= 1
        if self.invuln > 0:
            self.invuln -= 1
        if self.shield > 0:
            self.shield -= 1

    def draw(self, surf):
        if self.invuln > 0 and (self.invuln // 5) % 2 == 0:
            return                          # blink while invulnerable

        x, y = self.rect.center

        # engine flame
        flame = random.randint(7, 15)
        pygame.draw.polygon(surf, ORANGE,
                            [(x - 6, y + 18), (x + 6, y + 18), (x, y + 18 + flame)])
        pygame.draw.polygon(surf, YELLOW,
                            [(x - 3, y + 18), (x + 3, y + 18), (x, y + 18 + flame * 0.6)])

        # wings
        pygame.draw.polygon(surf, BLUE,
                            [(x - 24, y + 4), (x + 24, y + 4),
                             (x + 14, y + 16), (x - 14, y + 16)])
        # fuselage
        pygame.draw.polygon(surf, CYAN,
                            [(x, y - 22), (x + 9, y + 8), (x + 7, y + 18),
                             (x - 7, y + 18), (x - 9, y + 8)])
        # cockpit
        pygame.draw.circle(surf, WHITE, (x, y - 6), 5)

        if self.shield > 0:
            pygame.draw.circle(surf, GREEN, (x, y), 32, 2)


class Enemy:
    def __init__(self, level):
        self.big = random.random() < 0.22
        self.w = 56 if self.big else 40
        self.h = 46 if self.big else 36

        self.x = float(random.randint(50, WIDTH - 50))
        self.y = float(-40)
        self.rect = pygame.Rect(0, 0, self.w, self.h)
        self.rect.center = (int(self.x), int(self.y))

        self.speed = (1.0 if self.big else 1.8) + level * 0.12
        self.hp = self.max_hp = 4 if self.big else 2
        self.amp = random.uniform(15, 45)
        self.freq = random.uniform(0.02, 0.05)
        self.t = random.uniform(0, math.tau)
        self.fire_timer = random.randint(50, 150)
        self.color = random.choice([RED, MAGENTA, ORANGE])
        self.score = 150 if self.big else 80
        self.dead = False

    def update(self, player):
        """Move, and possibly return a bullet aimed at the player."""
        self.t += self.freq
        self.x += math.sin(self.t) * self.amp * 0.03
        self.y += self.speed
        self.rect.center = (int(self.x), int(self.y))

        if self.rect.top > HEIGHT + 20:
            self.dead = True

        self.fire_timer -= 1
        if (self.fire_timer <= 0 and self.rect.bottom > 0
                and self.y < HEIGHT * 0.8 and random.random() < 0.6):
            self.fire_timer = random.randint(70, 160)
            dx = player.rect.centerx - self.x
            dy = player.rect.centery - self.y
            dist = math.hypot(dx, dy) or 1
            spd = 4.2
            return Bullet(self.x, self.rect.bottom,
                          dx / dist * spd, dy / dist * spd,
                          ORANGE, 1, friendly=False)
        return None

    def draw(self, surf):
        x, y = self.rect.center

        # wings
        pygame.draw.polygon(surf, (60, 60, 90),
                            [(x - 22, y - 6), (x + 22, y - 6),
                             (x + 12, y - 18), (x - 12, y - 18)])
        # fuselage
        pygame.draw.polygon(surf, self.color,
                            [(x, y + 20), (x + 8, y - 10),
                             (x + 6, y - 18), (x - 6, y - 18), (x - 8, y - 10)])
        # cockpit
        pygame.draw.circle(surf, YELLOW, (x, y + 4), 4)

        # damage bar
        if self.hp < self.max_hp:
            w = self.w
            pygame.draw.rect(surf, (40, 40, 60), (x - w // 2, y - 30, w, 4))
            pygame.draw.rect(surf, GREEN,
                             (x - w // 2, y - 30,
                              int(w * self.hp / self.max_hp), 4))


# ------------------------------------------------------------------ game
class Game:
    def __init__(self):
        self.best = 0
        self.state = "menu"
        self.new_game()

    def new_game(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.particles = []
        self.powerups = []
        self.stars = make_stars()
        self.score = 0
        self.level = 1
        self.spawn_timer = 40
        self.flash = 0

    # -------------------------------------------------- input
    def handle_key(self, key):
        if self.state == "menu":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.new_game()
                self.state = "playing"
        elif self.state == "playing":
            if key in (pygame.K_p, pygame.K_ESCAPE):
                self.state = "paused"
        elif self.state == "paused":
            if key in (pygame.K_p, pygame.K_ESCAPE, pygame.K_RETURN):
                self.state = "playing"
        elif self.state == "gameover":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.new_game()
                self.state = "playing"

    # -------------------------------------------------- update
    def update(self):
        # starfield always scrolls
        for s in self.stars:
            s[1] += s[2]
            if s[1] > HEIGHT:
                s[1] = -2
                s[0] = random.uniform(0, WIDTH)

        if self.flash > 0:
            self.flash -= 1

        if self.state != "playing":
            return

        p = self.player
        p.update()

        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.fire()

        # difficulty ramp
        self.level = 1 + self.score // 1500
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self.enemies.append(Enemy(self.level))
            self.spawn_timer = max(16, 65 - self.level * 4)

        # move bullets
        for b in self.bullets:
            b.update()

        # move enemies
        for e in self.enemies:
            shot = e.update(p)
            if shot:
                self.bullets.append(shot)

        self.check_collisions()

        # move power-ups
        for pu in self.powerups:
            pu.update()
            if pu.rect.colliderect(p.rect):
                pu.dead = True
                if pu.kind == "power":
                    p.power = min(3, p.power + 1)
                    self.score += 50
                elif pu.kind == "shield":
                    p.shield = 480
                else:
                    p.lives = min(5, p.lives + 1)

        for pt in self.particles:
            pt.update()

        # sweep dead objects
        self.bullets = [b for b in self.bullets if not b.dead]
        self.enemies = [e for e in self.enemies if not e.dead]
        self.powerups = [pu for pu in self.powerups if not pu.dead]
        self.particles = [pt for pt in self.particles if not pt.dead]

    def fire(self):
        p = self.player
        if p.cooldown > 0:
            return
        p.cooldown = 9
        cx, cy = p.rect.centerx, p.rect.top

        if p.power == 1:
            self.bullets.append(Bullet(cx, cy, 0, -13))
        elif p.power == 2:
            self.bullets.append(Bullet(cx - 10, cy + 6, 0, -13))
            self.bullets.append(Bullet(cx + 10, cy + 6, 0, -13))
        else:
            self.bullets.append(Bullet(cx, cy - 4, 0, -14))
            self.bullets.append(Bullet(cx - 12, cy + 8, -2.4, -12.5))
            self.bullets.append(Bullet(cx + 12, cy + 8, 2.4, -12.5))

    def check_collisions(self):
        p = self.player

        # player bullets vs enemies
        for b in self.bullets:
            if b.dead or not b.friendly:
                continue
            for e in self.enemies:
                if e.dead:
                    continue
                if e.rect.collidepoint(b.x, b.y):
                    b.dead = True
                    e.hp -= b.dmg
                    for _ in range(4):
                        self.particles.append(Particle(b.x, b.y, WHITE))
                    if e.hp <= 0:
                        e.dead = True
                        self.explode(e.rect.centerx, e.rect.centery, e.color, 22)
                        self.score += e.score
                        if random.random() < 0.18:
                            self.powerups.append(
                                PowerUp(e.rect.centerx, e.rect.centery))
                    break

        if p.invuln > 0:
            return

        # enemy bullets vs player
        hitbox = p.rect.inflate(-14, -14)
        for b in self.bullets:
            if b.dead or b.friendly:
                continue
            if hitbox.collidepoint(b.x, b.y):
                b.dead = True
                self.hit_player()
                return

        # enemy aircraft vs player
        for e in self.enemies:
            if e.dead:
                continue
            if p.rect.colliderect(e.rect):
                e.dead = True
                self.explode(e.rect.centerx, e.rect.centery, e.color, 20)
                self.hit_player()
                return

    def hit_player(self):
        p = self.player
        if p.shield > 0:                    # shield absorbs the hit
            p.shield = 0
            p.invuln = 60
            return

        p.lives -= 1
        p.power = max(1, p.power - 1)
        p.invuln = 120
        self.flash = 10
        self.explode(p.rect.centerx, p.rect.centery, CYAN, 30)

        if p.lives <= 0:
            self.state = "gameover"
            self.best = max(self.best, self.score)

    def explode(self, x, y, color, n):
        for _ in range(n):
            self.particles.append(Particle(x, y, color))

    # -------------------------------------------------- draw
    def draw(self, surf):
        surf.fill(NIGHT)

        for x, y, spd, r in self.stars:
            c = min(255, int(120 + spd * 45))
            pygame.draw.circle(surf, (c, c, min(255, c + 20)), (int(x), int(y)), r)

        if self.state == "menu":
            self.draw_menu(surf)
            return

        for pu in self.powerups:
            pu.draw(surf)
        for e in self.enemies:
            e.draw(surf)
        for b in self.bullets:
            b.draw(surf)
        for pt in self.particles:
            pt.draw(surf)
        if self.player.lives > 0:
            self.player.draw(surf)

        self.draw_hud(surf)

        if self.flash > 0:
            flash = pygame.Surface((WIDTH, HEIGHT))
            flash.set_alpha(self.flash * 12)
            flash.fill(RED)
            surf.blit(flash, (0, 0))

        if self.state == "paused":
            self.draw_center_text(surf, "PAUSED", "Press P to resume")
        elif self.state == "gameover":
            self.draw_gameover(surf)

    def draw_hud(self, surf):
        txt = font_m.render(f"SCORE {self.score}", True, WHITE)
        surf.blit(txt, (16, 12))

        txt = font_s.render(f"LEVEL {self.level}    BEST {self.best}", True, GREY)
        surf.blit(txt, (16, 44))

        # lives
        for i in range(self.player.lives):
            x = WIDTH - 30 - i * 30
            pygame.draw.polygon(surf, CYAN,
                                [(x, HEIGHT - 42), (x + 10, HEIGHT - 16),
                                 (x - 10, HEIGHT - 16)])

        # power meter
        surf.blit(font_s.render("POWER", True, GREY), (16, HEIGHT - 34))
        for i in range(3):
            col = CYAN if i < self.player.power else (45, 55, 75)
            pygame.draw.rect(surf, col, (88 + i * 22, HEIGHT - 32, 16, 14),
                             border_radius=3)

    def draw_menu(self, surf):
        title = font_l.render("AIR  ATTACK", True, CYAN)
        surf.blit(title, title.get_rect(center=(WIDTH // 2, 170)))

        lines = [
            "Move  :  Arrows / WASD",
            "Fire  :  Space",
            "Pause :  P or Esc",
            "",
            "P = weapon upgrade    S = shield    + = extra life",
        ]
        for i, line in enumerate(lines):
            color = YELLOW if line.startswith("P =") else GREY
            txt = font_s.render(line, True, color)
            surf.blit(txt, txt.get_rect(center=(WIDTH // 2, 290 + i * 30)))

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            prompt = font_m.render("Press ENTER to start", True, WHITE)
            surf.blit(prompt, prompt.get_rect(center=(WIDTH // 2, 500)))

    def draw_center_text(self, surf, big, small):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surf.blit(overlay, (0, 0))

        t = font_l.render(big, True, WHITE)
        surf.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
        s = font_m.render(small, True, GREY)
        surf.blit(s, s.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

    def draw_gameover(self, surf):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surf.blit(overlay, (0, 0))

        t = font_l.render("GAME OVER", True, RED)
        surf.blit(t, t.get_rect(center=(WIDTH // 2, 200)))

        s = font_m.render(f"SCORE   {self.score}", True, WHITE)
        surf.blit(s, s.get_rect(center=(WIDTH // 2, 290)))

        b = font_m.render(f"BEST    {self.best}", True, YELLOW)
        surf.blit(b, b.get_rect(center=(WIDTH // 2, 330)))

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            p = font_s.render("Press ENTER to fly again", True, GREY)
            surf.blit(p, p.get_rect(center=(WIDTH // 2, 430)))


# ------------------------------------------------------------------ main loop
def main():
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                game.handle_key(event.key)

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()