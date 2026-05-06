
import asyncio
import math
import os
import random
import pygame

BASE_W, BASE_H = 900, 600
PLAYER_SIZE, VIRUS_SIZE, BOSS_SIZE = 50, 45, 90
BASE_DIR = os.path.dirname(__file__)

GREEN = (0, 255, 70)
DARK = (10, 10, 10)
RED = (255, 50, 50)
CYAN = (50, 200, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 255)
WHITE = (255, 255, 255)
ORANGE = (255, 160, 0)
GREY = (80, 80, 80)
PINK = (255, 100, 150)
DKGRN = (0, 180, 50)
DKRED = (140, 0, 0)
GOLD = (255, 215, 0)
SHIELD_COL = (80, 160, 255)
SLOT_EMPTY = (40, 40, 60)
SLOT_BORDER = (60, 60, 100)

screen = None
clock = None
FONT = None
SFONT = None
BFONT = None
TFONT = None
HFONT = None
XFONT = None
player_img = None
virus_img = None
boss_img = None


def sw():
    return screen.get_width()


def sh():
    return screen.get_height()


def make_screen(fullscreen):
    if fullscreen:
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return pygame.display.set_mode((BASE_W, BASE_H))


def make_fallback_sprite(size, color, symbol):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    rect = surf.get_rect()
    pygame.draw.rect(surf, (8, 16, 12), rect, border_radius=8)
    pygame.draw.rect(surf, color, rect.inflate(-2, -2), 3, border_radius=8)
    pygame.draw.circle(surf, (*color, 60), rect.center, min(size) // 2 - 2)
    label = BFONT.render(symbol, True, color)
    surf.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))
    return surf


def load_img(name, size, color, symbol):
    path = os.path.join(BASE_DIR, "assets", name)
    if os.path.exists(path):
        return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)
    return make_fallback_sprite(size, color, symbol)


def init_runtime():
    global screen, clock, FONT, SFONT, BFONT, TFONT, HFONT, XFONT
    global player_img, virus_img, boss_img
    if screen is not None:
        return
    pygame.init()
    screen = pygame.display.set_mode((BASE_W, BASE_H))
    pygame.display.set_caption("Hacker Terminal")
    clock = pygame.time.Clock()
    FONT = pygame.font.SysFont("consolas", 18)
    SFONT = pygame.font.SysFont("consolas", 13)
    BFONT = pygame.font.SysFont("consolas", 40)
    TFONT = pygame.font.SysFont("consolas", 11)
    HFONT = pygame.font.SysFont("consolas", 72)
    XFONT = pygame.font.SysFont("consolas", 22)
    player_img = load_img("main-char.png", (PLAYER_SIZE, PLAYER_SIZE), GREEN, ">")
    virus_img = load_img("virus-char.png", (VIRUS_SIZE, VIRUS_SIZE), RED, "V")
    boss_img = load_img("hacker-char.png", (BOSS_SIZE, BOSS_SIZE), PURPLE, "H")

BOSS_WAVES = [
    {"score": 150, "count": 1, "hp_base": 20, "speed_base": 1.4, "dpt": 0.4, "color": RED, "label": "HACKER"},
    {"score": 400, "count": 1, "hp_base": 40, "speed_base": 1.6, "dpt": 0.6, "color": ORANGE, "label": "WORM"},
    {"score": 800, "count": 2, "hp_base": 45, "speed_base": 1.8, "dpt": 0.7, "color": PURPLE, "label": "ROOTKIT"},
    {"score": 1400, "count": 1, "hp_base": 80, "speed_base": 2.6, "dpt": 0.9, "color": (255, 0, 100), "label": "TROJAN"},
    {"score": 2200, "count": 3, "hp_base": 55, "speed_base": 2.2, "dpt": 0.9, "color": CYAN, "label": "BOTNET"},
    {"score": 3200, "count": 1, "hp_base": 160, "speed_base": 2.0, "dpt": 1.2, "color": GOLD, "label": "ZERO-DAY"},
    {"score": 4400, "count": 2, "hp_base": 100, "speed_base": 2.8, "dpt": 1.3, "color": WHITE, "label": "KERNEL"},
    {"score": 5800, "count": 4, "hp_base": 80, "speed_base": 2.9, "dpt": 1.3, "color": GREEN, "label": "HYDRA"},
    {"score": 7500, "count": 1, "hp_base": 260, "speed_base": 2.3, "dpt": 1.6, "color": (255, 80, 200), "label": "MEGABYTE"},
    {"score": 9500, "count": 3, "hp_base": 130, "speed_base": 3.2, "dpt": 1.7, "color": (200, 255, 50), "label": "DAEMON"},
    {"score": 12000, "count": 5, "hp_base": 100, "speed_base": 3.0, "dpt": 1.6, "color": (255, 50, 200), "label": "SWARM.EXE"},
    {"score": 15000, "count": 1, "hp_base": 200, "speed_base": 4.0, "dpt": 2.0, "color": (0, 255, 200), "label": "PHANTOM"},
    {"score": 18500, "count": 2, "hp_base": 280, "speed_base": 2.6, "dpt": 2.2, "color": GOLD, "label": "FORTRESS"},
    {"score": 23000, "count": 6, "hp_base": 140, "speed_base": 3.4, "dpt": 2.5, "color": (255, 0, 0), "label": "APOCALYPSE"},
]

MOD_DEFS = {
    "dmg_up": {"name": "DMG +1", "short": "DMG+", "color": RED, "price": 80, "stat": "damage", "delta": 1, "max_per_gun": 5},
    "dmg_up2": {"name": "DMG +3", "short": "DMG++", "color": (255, 80, 30), "price": 200, "stat": "damage", "delta": 3, "max_per_gun": 3},
    "rate_up": {"name": "Fire Rate+", "short": "RATE+", "color": CYAN, "price": 100, "stat": "fire_rate", "delta": -2, "max_per_gun": 5},
    "rate_up2": {"name": "Rapid Fire", "short": "RAPID", "color": (0, 200, 220), "price": 250, "stat": "fire_rate", "delta": -5, "max_per_gun": 2},
    "spd_up": {"name": "Bullet Spd+", "short": "SPD+", "color": YELLOW, "price": 80, "stat": "bullet_speed", "delta": 3, "max_per_gun": 5},
    "spread_up": {"name": "Wide Shot", "short": "WIDE", "color": ORANGE, "price": 150, "stat": "spread", "delta": 1, "max_per_gun": 3},
    "pierce": {"name": "Piercing", "short": "PRCNG", "color": PURPLE, "price": 300, "stat": "piercing", "delta": True, "max_per_gun": 1},
}
MOD_ORDER = ["dmg_up", "dmg_up2", "rate_up", "rate_up2", "spd_up", "spread_up", "pierce"]
MAX_SLOTS = 4

CHEST_ITEMS = {
    "magnet": {"name": "XP Magnet", "desc": "Sucks all XP orbs instantly", "color": CYAN, "symbol": "M"},
    "bomb": {"name": "Nova Bomb", "desc": "Destroys every enemy", "color": RED, "symbol": "B"},
    "shield": {"name": "Shield", "desc": "Grants shield HP bar", "color": SHIELD_COL, "symbol": "S"},
}
CHEST_ITEM_KEYS = list(CHEST_ITEMS.keys())
CHEST_SIZE = 22
SPIN_DURATION = 90
CHEST_DROP_CHANCE = 30
BOSS_CHEST_CHANCE = 3
MAX_SHIELD = 60

GUNS = {
    "pistol": {"name": "Pistol", "desc": "Standard sidearm. Free.", "color": CYAN, "symbol": "P", "price": 0, "damage": 1, "fire_rate": 10, "bullet_speed": 8, "spread": 1, "piercing": False},
    "shotgun": {"name": "Shotgun", "desc": "3-pellet spread.", "color": ORANGE, "symbol": "S", "price": 150, "damage": 2, "fire_rate": 22, "bullet_speed": 9, "spread": 3, "piercing": False},
    "smg": {"name": "SMG", "desc": "Rapid fire.", "color": GREEN, "symbol": "M", "price": 200, "damage": 1, "fire_rate": 4, "bullet_speed": 10, "spread": 1, "piercing": False},
    "sniper": {"name": "Sniper", "desc": "Slow, massive damage.", "color": YELLOW, "symbol": "N", "price": 300, "damage": 6, "fire_rate": 35, "bullet_speed": 20, "spread": 1, "piercing": False},
    "laser": {"name": "Laser", "desc": "Shots pierce enemies.", "color": PURPLE, "symbol": "L", "price": 500, "damage": 3, "fire_rate": 14, "bullet_speed": 15, "spread": 1, "piercing": True},
}
GUN_ORDER = ["pistol", "shotgun", "smg", "sniper", "laser"]

UPGRADE_META = {
    "damage": {"name": "Damage Boost", "symbol": "!", "color": RED},
    "attack_speed": {"name": "Attack Speed", "symbol": ">>", "color": CYAN},
    "move_speed": {"name": "Move Speed", "symbol": ">", "color": GREEN},
    "bullet_speed": {"name": "Bullet Speed", "symbol": "~", "color": YELLOW},
    "max_hp": {"name": "Max HP Up", "symbol": "+", "color": PINK},
}
upgrades_list = [{"name": meta["name"], "effect": effect} for effect, meta in UPGRADE_META.items()]


def virus_stats(wave_num):
    hp = 1.0 * (1.28 ** wave_num)
    speed = 1.8 + wave_num * 0.18
    dpt = 0.30 + wave_num * 0.09
    return max(1, hp), min(speed, 5.5), min(dpt, 3.0)


def boss_stats(wave_idx, repeat):
    wave = BOSS_WAVES[wave_idx % len(BOSS_WAVES)]
    cycle_bonus = (wave_idx // len(BOSS_WAVES)) * 0.25
    hp = wave["hp_base"] * (1.0 + repeat * 0.60 + cycle_bonus)
    speed = min(wave["speed_base"] + repeat * 0.30, 6.0)
    dpt = min(wave["dpt"] + repeat * 0.25 + cycle_bonus * 0.1, 4.0)
    return hp, speed, dpt


class Particle:
    def __init__(self, x, y, color, vx, vy, life):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08
        self.life -= 1

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = int(255 * self.life / self.max_life)
        radius = max(1, int(4 * self.life / self.max_life))
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (radius, radius), radius)
        surf.blit(s, (int(self.x) - radius, int(self.y) - radius))


class Enemy:
    def __init__(self, x, y, hp, speed, kind, dpt=0.5, color=RED, label=""):
        self.x = float(x)
        self.y = float(y)
        self.kind = kind
        size = BOSS_SIZE if kind == "boss" else VIRUS_SIZE
        self.rect = pygame.Rect(x, y, size, size)
        self.hp = float(hp)
        self.max_hp = float(hp)
        self.speed = speed
        self.dpt = dpt
        self.color = color
        self.label = label

    def move(self, target):
        dx = target.centerx - self.x
        dy = target.centery - self.y
        dist = math.hypot(dx, dy)
        if dist:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)


class Chest:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(int(x), int(y), CHEST_SIZE, CHEST_SIZE)
        self.state = "closed"
        self.spin_timer = 0
        self.spin_item = random.choice(CHEST_ITEM_KEYS)
        self.revealed_item = random.choice(CHEST_ITEM_KEYS)

    def open(self):
        if self.state == "closed":
            self.state = "spinning"
            self.spin_timer = 0

    def update(self):
        if self.state != "spinning":
            return
        self.spin_timer += 1
        interval = max(2, int(4 + (self.spin_timer / SPIN_DURATION) * 18))
        if self.spin_timer % interval == 0:
            self.spin_item = random.choice(CHEST_ITEM_KEYS)
        if self.spin_timer >= SPIN_DURATION:
            self.spin_item = self.revealed_item
            self.state = "open"

    def draw(self, surf):
        cx, cy = self.rect.center
        pygame.draw.rect(surf, (100, 65, 18), self.rect, border_radius=3)
        pygame.draw.rect(surf, GOLD if self.state != "open" else (110, 80, 30), self.rect, 2, border_radius=3)
        if self.state == "closed":
            pygame.draw.circle(surf, GOLD, (cx, cy), 4)
            lbl = TFONT.render("!", True, GOLD)
            surf.blit(lbl, (cx - lbl.get_width() // 2, self.rect.y - 14))
        else:
            key = self.spin_item if self.state == "spinning" else self.revealed_item
            meta = CHEST_ITEMS[key]
            sym = SFONT.render(meta["symbol"], True, meta["color"])
            surf.blit(sym, (cx - sym.get_width() // 2, cy - sym.get_height() // 2))
            if self.state == "spinning":
                t = pygame.time.get_ticks() / 200
                for deg in range(0, 360, 45):
                    ang = math.radians(deg + t * 60)
                    pygame.draw.circle(surf, GOLD, (cx + int(18 * math.cos(ang)), cy + int(18 * math.sin(ang))), 2)
            else:
                nm = TFONT.render(meta["name"], True, meta["color"])
                surf.blit(nm, (cx - nm.get_width() // 2, self.rect.y - 14))


class Game:
    def __init__(self):
        self.fullscreen = False
        self.running = True
        self.scene = "main_menu"
        self.settings_open = False
        self.dev_panel_open = False
        self.credits = 0
        self.owned_guns = {"pistol"}
        self.equipped_gun = "pistol"
        self.gun_mods = {gid: [] for gid in GUN_ORDER}
        self.mod_inventory = {key: 0 for key in MOD_ORDER}
        self.cust_selected_gun = "pistol"
        self.cust_drag_mod = None
        self.cust_drag_from_inventory = False
        self.reset_game()

    def panel_x(self):
        return sw() - 175

    def get_gun_effective(self, gid):
        base = GUNS[gid]
        damage = base["damage"]
        fire_rate = base["fire_rate"]
        bullet_speed = base["bullet_speed"]
        spread = base["spread"]
        piercing = base["piercing"]
        for mod_key in self.gun_mods[gid]:
            mod = MOD_DEFS[mod_key]
            stat = mod["stat"]
            if stat == "damage":
                damage += mod["delta"]
            elif stat == "fire_rate":
                fire_rate = max(2, fire_rate + mod["delta"])
            elif stat == "bullet_speed":
                bullet_speed += mod["delta"]
            elif stat == "spread":
                spread = min(8, spread + mod["delta"])
            elif stat == "piercing":
                piercing = True
        return {"damage": damage, "fire_rate": fire_rate, "bullet_speed": bullet_speed, "spread": spread, "piercing": piercing}

    def reset_game(self):
        self.player = pygame.Rect(sw() // 2, sh() // 2, PLAYER_SIZE, PLAYER_SIZE)
        self.player_speed = 5
        self.max_hp = 100
        self.player_hp = 100.0
        self.shield_hp = 0.0
        eff = self.get_gun_effective(self.equipped_gun)
        self.bullet_speed = eff["bullet_speed"]
        self.bullet_damage = eff["damage"]
        self.fire_rate = eff["fire_rate"]
        self.gun_piercing = eff["piercing"]
        self.gun_spread = eff["spread"]
        self.bullets = []
        self.viruses = []
        self.hackers = []
        self.orbs = []
        self.chests = []
        self.particles = []
        self.active_item_fx = []
        self.xp = 0
        self.level = 1
        self.xp_to_next = 50
        self.boss_active = False
        self.boss_wave_idx = 0
        self.boss_repeat = 0
        self.wave_num = 0
        self.virus_timer = 0
        self.shoot_timer = 0
        self.score = 0
        self.upgrade_counts = {key: 0 for key in UPGRADE_META}
        self.choosing_upgrade = False
        self.current_choices = []
        self.game_over = False
        self.paused = False
        self.boss_announce = ""
        self.boss_announce_timer = 0

    def calc_xp_for_level(self, level):
        return int(50 * (1.45 ** (level - 1)))

    def spawn_particles(self, x, y, color, count=20):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 5)
            self.particles.append(Particle(x, y, color, math.cos(angle) * speed, math.sin(angle) * speed, random.randint(20, 45)))

    def spawn_orb(self, x, y, value):
        self.orbs.append({"x": float(x), "y": float(y), "rect": pygame.Rect(int(x), int(y), 10, 10), "value": value})

    def check_level_up(self):
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = self.calc_xp_for_level(self.level)
            self.choosing_upgrade = True
            self.current_choices = upgrades_list[:]

    def apply_upgrade(self, effect):
        self.upgrade_counts[effect] += 1
        if effect == "damage":
            self.bullet_damage += 1
        elif effect == "attack_speed":
            self.fire_rate = max(3, self.fire_rate - 2)
        elif effect == "move_speed":
            self.player_speed += 1
        elif effect == "bullet_speed":
            self.bullet_speed += 2
        elif effect == "max_hp":
            self.max_hp += 20
            self.player_hp += 20

    def apply_item(self, item_key):
        if item_key == "magnet":
            for orb in self.orbs[:]:
                self.xp += orb["value"]
                self.score += orb["value"]
                self.spawn_particles(orb["rect"].x, orb["rect"].y, CYAN, 6)
            self.orbs.clear()
            self.active_item_fx.append({"kind": "magnet", "timer": 60, "max": 60})
            self.check_level_up()
        elif item_key == "bomb":
            for enemy in self.viruses[:] + self.hackers[:]:
                self.spawn_particles(enemy.rect.centerx, enemy.rect.centery, ORANGE, 30)
                self.spawn_orb(enemy.rect.centerx, enemy.rect.centery, 50 if enemy.kind == "boss" else 10)
            self.viruses.clear()
            self.hackers.clear()
            self.boss_active = False
            self.active_item_fx.append({"kind": "bomb", "timer": 50, "max": 50})
        elif item_key == "shield":
            self.shield_hp = MAX_SHIELD
            self.spawn_particles(self.player.centerx, self.player.centery, SHIELD_COL, 25)
            self.active_item_fx.append({"kind": "shield", "timer": 40, "max": 40})

    def shoot(self, angle):
        for i in range(self.gun_spread):
            offset = math.radians((i - self.gun_spread // 2) * 12) if self.gun_spread > 1 else 0.0
            a = angle + offset
            self.bullets.append({
                "rect": pygame.Rect(self.player.centerx - 3, self.player.centery - 3, 6, 6),
                "dx": math.cos(a) * self.bullet_speed,
                "dy": math.sin(a) * self.bullet_speed,
                "piercing": self.gun_piercing,
                "hit_set": set(),
            })

    def toggle_fullscreen(self):
        global screen
        self.fullscreen = not self.fullscreen
        screen = make_screen(self.fullscreen)

    def try_spawn_boss(self):
        if self.boss_active:
            return
        real_idx = self.boss_wave_idx % len(BOSS_WAVES)
        wave = BOSS_WAVES[real_idx]
        threshold = wave["score"] * (1 + self.boss_repeat * 0.7)
        if self.score < threshold:
            return
        self.boss_active = True
        self.viruses.clear()
        hp, speed, dpt = boss_stats(real_idx, self.boss_repeat)
        count = wave["count"]
        if self.boss_repeat >= 2:
            count += self.boss_repeat - 1
        for i in range(count):
            off_x = (i - count // 2) * 110
            self.hackers.append(Enemy(sw() // 2 + off_x, 60, hp, speed, "boss", dpt, wave["color"], wave["label"]))
        loop_str = f" [LOOP {self.boss_repeat + 1}]" if self.boss_repeat > 0 else ""
        self.boss_announce = f"WARNING: {wave['label']}{loop_str} INCOMING!"
        self.boss_announce_timer = 200
        self.wave_num += 1

    def on_boss_killed(self):
        self.boss_active = False
        self.boss_wave_idx += 1
        if self.boss_wave_idx >= len(BOSS_WAVES):
            self.boss_wave_idx = 0
            self.boss_repeat += 1

    def draw_bar(self, surf, x, y, w, h, ratio, bg, fg, border=WHITE, label="", bw=2):
        pygame.draw.rect(surf, bg, (x, y, w, h))
        fill_w = max(0, int(w * max(0.0, min(1.0, ratio))))
        if fill_w:
            pygame.draw.rect(surf, fg, (x, y, fill_w, h))
        pygame.draw.rect(surf, border, (x, y, w, h), bw)
        if label:
            lbl = TFONT.render(label, True, WHITE)
            surf.blit(lbl, (x + w // 2 - lbl.get_width() // 2, y + h // 2 - lbl.get_height() // 2))

    def draw_button(self, surf, rect, text, color=GREEN, hover=False, font=None):
        if font is None:
            font = FONT
        pairs = {
            GREEN: ((30, 50, 30), (15, 25, 15)),
            YELLOW: ((40, 40, 10), (20, 20, 5)),
            RED: ((50, 10, 10), (25, 5, 5)),
            CYAN: ((10, 40, 50), (5, 20, 25)),
            PURPLE: ((30, 10, 40), (15, 5, 20)),
            GREY: ((40, 40, 40), (20, 20, 20)),
            ORANGE: ((50, 35, 5), (25, 18, 2)),
        }
        bg = pairs.get(color, ((30, 30, 30), (15, 15, 15)))[0 if hover else 1]
        pygame.draw.rect(surf, bg, rect, border_radius=6)
        pygame.draw.rect(surf, color, rect, 2, border_radius=6)
        t = font.render(text, True, color)
        surf.blit(t, (rect.x + rect.w // 2 - t.get_width() // 2, rect.y + rect.h // 2 - t.get_height() // 2))

    def draw_settings_panel(self, surf, mx, my, x, y):
        panel = pygame.Rect(x, y, 280, 110)
        s = pygame.Surface(panel.size, pygame.SRCALPHA)
        s.fill((8, 8, 24, 245))
        surf.blit(s, panel)
        pygame.draw.rect(surf, CYAN, panel, 2, border_radius=6)
        surf.blit(SFONT.render("SETTINGS", True, CYAN), (x + 10, y + 10))
        pygame.draw.line(surf, (40, 80, 100), (x + 8, y + 28), (x + panel.w - 8, y + 28), 1)
        fs_btn = pygame.Rect(x + 8, y + 36, panel.w - 16, 36)
        self.draw_button(surf, fs_btn, "FULLSCREEN:  [ON]" if self.fullscreen else "FULLSCREEN:  [OFF]", GREEN if self.fullscreen else GREY, fs_btn.collidepoint(mx, my), SFONT)
        hint = TFONT.render("Press F11 to toggle anytime", True, (60, 80, 60))
        surf.blit(hint, (x + 10, y + 80))
        return fs_btn

    def draw_main_menu(self, surf, mx, my):
        surf.fill(DARK)
        for y in range(0, sh(), 4):
            pygame.draw.line(surf, (0, 18, 0), (0, y), (sw(), y))
        title1 = HFONT.render("HACKER", True, GREEN)
        title2 = HFONT.render("TERMINAL", True, DKGRN)
        surf.blit(title1, (sw() // 2 - title1.get_width() // 2, 60))
        surf.blit(title2, (sw() // 2 - title2.get_width() // 2, 135))
        subtitle = FONT.render("Survive the virus swarm", True, GREY)
        surf.blit(subtitle, (sw() // 2 - subtitle.get_width() // 2, 210))
        credits = FONT.render(f"Credits: {self.credits}", True, YELLOW)
        surf.blit(credits, (sw() // 2 - credits.get_width() // 2, 236))
        cx = sw() // 2 - 130
        buttons = [
            pygame.Rect(cx, 278, 260, 52),
            pygame.Rect(cx, 342, 260, 52),
            pygame.Rect(cx, 406, 260, 52),
            pygame.Rect(cx, 470, 260, 46),
            pygame.Rect(cx, 528, 260, 42),
        ]
        labels = [("PLAY GAME", GREEN), ("GUN SHOP", YELLOW), ("CUSTOMISE GUNS", CYAN), ("SETTINGS", GREY), ("QUIT", RED)]
        for rect, (label, color) in zip(buttons, labels):
            self.draw_button(surf, rect, label, color, rect.collidepoint(mx, my))
        fs_btn = self.draw_settings_panel(surf, mx, my, cx + 266, 462) if self.settings_open else None
        return (*buttons, fs_btn)

    def draw_shop(self, surf, mx, my):
        surf.fill((8, 8, 18))
        pygame.draw.rect(surf, DKGRN, (0, 0, sw(), sh()), 3)
        title = BFONT.render("GUN SHOP", True, YELLOW)
        surf.blit(title, (sw() // 2 - title.get_width() // 2, 14))
        credits = FONT.render(f"Credits: {self.credits}", True, GREEN)
        surf.blit(credits, (sw() // 2 - credits.get_width() // 2, 62))
        card_w, card_h, gap = 148, 205, 14
        total_w = len(GUN_ORDER) * card_w + (len(GUN_ORDER) - 1) * gap
        sx = sw() // 2 - total_w // 2
        buy_rects, equip_rects = {}, {}
        for i, gid in enumerate(GUN_ORDER):
            gun = GUNS[gid]
            col = gun["color"]
            rect = pygame.Rect(sx + i * (card_w + gap), 100, card_w, card_h)
            owned = gid in self.owned_guns
            equipped = gid == self.equipped_gun
            bg = pygame.Surface(rect.size, pygame.SRCALPHA)
            bg.fill((*col, 55 if rect.collidepoint(mx, my) else 20))
            surf.blit(bg, rect)
            pygame.draw.rect(surf, col, rect, 3 if equipped else 1, border_radius=6)
            if equipped:
                eb = TFONT.render("EQUIPPED", True, YELLOW)
                surf.blit(eb, (rect.centerx - eb.get_width() // 2, rect.y + 4))
            sym = BFONT.render(f"[{gun['symbol']}]", True, col)
            surf.blit(sym, (rect.centerx - sym.get_width() // 2, rect.y + 20))
            nm = FONT.render(gun["name"], True, WHITE)
            surf.blit(nm, (rect.centerx - nm.get_width() // 2, rect.y + 74))
            eff = self.get_gun_effective(gid)
            lines = [f"DMG:  {eff['damage']}", f"RATE: {eff['fire_rate']}", f"SPD:  {eff['bullet_speed']}", f"SPRD: {eff['spread']}", "PIERCE" if eff["piercing"] else f"MODS: {len(self.gun_mods[gid])}/{MAX_SLOTS}"]
            for si, line in enumerate(lines):
                surf.blit(TFONT.render(line, True, (160, 160, 160)), (rect.x + 10, rect.y + 98 + si * 13))
            btn = pygame.Rect(rect.x + 8, rect.y + card_h - 34, card_w - 16, 26)
            if owned:
                if equipped:
                    self.draw_button(surf, btn, "EQUIPPED", GREY, False, SFONT)
                else:
                    equip_rects[gid] = btn
                    self.draw_button(surf, btn, "EQUIP", CYAN, btn.collidepoint(mx, my), SFONT)
            else:
                buy_rects[gid] = btn
                can_buy = self.credits >= gun["price"]
                self.draw_button(surf, btn, f"BUY  ${gun['price']}", GREEN if can_buy else GREY, btn.collidepoint(mx, my) and can_buy, SFONT)
        back = pygame.Rect(18, sh() - 50, 150, 36)
        self.draw_button(surf, back, "< BACK", GREY, back.collidepoint(mx, my))
        return buy_rects, equip_rects, back

    def chip_rects(self):
        rects = {}
        for i, key in enumerate(MOD_ORDER):
            rects[key] = pygame.Rect(10 + (i % 2) * 130, 100 + (i // 2) * 44, 120, 36)
        return rects

    def draw_mod_chip(self, surf, rect, key, count=None, hover=False):
        mod = MOD_DEFS[key]
        color = mod["color"]
        pygame.draw.rect(surf, (50, 50, 50) if hover else (30, 30, 30), rect, border_radius=4)
        pygame.draw.rect(surf, color, rect, 2, border_radius=4)
        surf.blit(SFONT.render(mod["short"], True, color), (rect.x + 6, rect.y + rect.h // 2 - 7))
        if count is not None:
            cnt = TFONT.render(f"x{count}", True, WHITE if count > 0 else GREY)
            surf.blit(cnt, (rect.right - cnt.get_width() - 5, rect.y + rect.h // 2 - cnt.get_height() // 2))

    def draw_customise(self, surf, mx, my):
        surf.fill((6, 6, 16))
        pygame.draw.rect(surf, CYAN, (0, 0, sw(), sh()), 2)
        title = BFONT.render("GUN CUSTOMISE", True, CYAN)
        surf.blit(title, (sw() // 2 - title.get_width() // 2, 12))
        surf.blit(SFONT.render("Drag chips onto slots  |  Right-click slot to remove", True, GREY), (sw() // 2 - 190, 54))
        surf.blit(FONT.render(f"Credits: {self.credits}", True, YELLOW), (sw() - 130, 12))
        pygame.draw.rect(surf, (12, 12, 28), (0, 70, 270, sh() - 70))
        surf.blit(FONT.render("MOD CHIPS", True, CYAN), (10, 78))
        chips = self.chip_rects()
        buy_rects = {}
        for key, rect in chips.items():
            self.draw_mod_chip(surf, rect, key, self.mod_inventory[key], rect.collidepoint(mx, my) and self.cust_drag_mod is None)
            mod = MOD_DEFS[key]
            price = TFONT.render(f"${mod['price']}", True, GOLD if self.credits >= mod["price"] else GREY)
            surf.blit(price, (rect.right - price.get_width() - 4, rect.y - 12))
            buy = pygame.Rect(rect.right + 4, rect.y, 38, rect.h)
            buy_rects[key] = buy
            self.draw_button(surf, buy, "BUY", GREEN if self.credits >= mod["price"] else GREY, buy.collidepoint(mx, my) and self.credits >= mod["price"], TFONT)
        cx = 275
        gun = GUNS[self.cust_selected_gun]
        eff = self.get_gun_effective(self.cust_selected_gun)
        pygame.draw.rect(surf, (10, 10, 24), (cx, 70, 330, sh() - 70))
        pygame.draw.rect(surf, gun["color"], (cx, 70, 330, sh() - 70), 1)
        surf.blit(XFONT.render(gun["name"], True, gun["color"]), (cx + 10, 80))
        surf.blit(SFONT.render(f"Slots: {len(self.gun_mods[self.cust_selected_gun])}/{MAX_SLOTS}", True, GREY), (cx + 10, 108))
        stats = [("DAMAGE", gun["damage"], eff["damage"], RED), ("FIRE RATE", gun["fire_rate"], eff["fire_rate"], CYAN), ("BULLET SPD", gun["bullet_speed"], eff["bullet_speed"], YELLOW), ("SPREAD", gun["spread"], eff["spread"], ORANGE), ("PIERCING", gun["piercing"], eff["piercing"], PURPLE)]
        for i, (label, base, value, color) in enumerate(stats):
            y = 128 + i * 22
            surf.blit(TFONT.render(label + ":", True, GREY), (cx + 10, y))
            surf.blit(SFONT.render(str(base), True, WHITE), (cx + 110, y))
            surf.blit(SFONT.render(f"-> {value}" if value != base else "(base)", True, color if value != base else GREY), (cx + 140, y))
        slot_rects = []
        surf.blit(SFONT.render("MOD SLOTS", True, GREY), (cx + 10, 248))
        for i in range(MAX_SLOTS):
            slot = pygame.Rect(cx + 40, 262 + i * 48, 130, 38)
            slot_rects.append(slot)
            occupied = i < len(self.gun_mods[self.cust_selected_gun])
            if occupied:
                self.draw_mod_chip(surf, slot, self.gun_mods[self.cust_selected_gun][i], hover=slot.collidepoint(mx, my))
                surf.blit(TFONT.render("RMB remove", True, GREY), (slot.right + 6, slot.y + 12))
            else:
                border = CYAN if self.cust_drag_mod and slot.collidepoint(mx, my) else SLOT_BORDER
                pygame.draw.rect(surf, SLOT_EMPTY, slot, border_radius=4)
                pygame.draw.rect(surf, border, slot, 2 if self.cust_drag_mod and slot.collidepoint(mx, my) else 1, border_radius=4)
                surf.blit(TFONT.render(f"SLOT {i + 1} -- empty --", True, border), (slot.x + 6, slot.y + 13))
        clear = pygame.Rect(cx + 40, sh() - 50, 130, 34)
        self.draw_button(surf, clear, "CLEAR ALL", RED, clear.collidepoint(mx, my) and self.cust_drag_mod is None)
        rx = 610
        tab_rects = {}
        pygame.draw.rect(surf, (10, 10, 24), (rx, 70, sw() - rx, sh() - 70))
        surf.blit(SFONT.render("SELECT GUN", True, GREY), (rx + 8, 78))
        for i, gid in enumerate(GUN_ORDER):
            tab = pygame.Rect(rx + 6, 96 + i * 50, sw() - rx - 12, 42)
            tab_rects[gid] = tab
            color = GUNS[gid]["color"]
            selected = gid == self.cust_selected_gun
            owned = gid in self.owned_guns
            pygame.draw.rect(surf, (20, 35, 35) if selected else (14, 14, 24), tab, border_radius=4)
            pygame.draw.rect(surf, color if owned else GREY, tab, 2 if selected else 1, border_radius=4)
            surf.blit(SFONT.render(GUNS[gid]["name"], True, color if owned else GREY), (tab.x + 6, tab.y + 6))
            surf.blit(TFONT.render(f"{len(self.gun_mods[gid])}/{MAX_SLOTS} mods", True, GOLD if self.gun_mods[gid] else GREY), (tab.x + 6, tab.y + 22))
        back = pygame.Rect(rx + 6, sh() - 50, sw() - rx - 12, 36)
        self.draw_button(surf, back, "< BACK", GREY, back.collidepoint(mx, my) and self.cust_drag_mod is None)
        if self.cust_drag_mod:
            self.draw_mod_chip(surf, pygame.Rect(mx - 60, my - 18, 120, 36), self.cust_drag_mod)
        return chips, buy_rects, slot_rects, tab_rects, back, clear

    def draw_hud(self, surf):
        self.draw_bar(surf, 20, 16, 210, 18, self.player_hp / self.max_hp, (60, 0, 0), RED, label=f"HP {int(self.player_hp)}/{self.max_hp}")
        if self.shield_hp > 0:
            self.draw_bar(surf, 20, 38, 210, 10, self.shield_hp / MAX_SHIELD, (10, 20, 50), SHIELD_COL, border=(60, 120, 220), label=f"SHIELD {int(self.shield_hp)}")
            xp_y = 52
        else:
            xp_y = 38
        self.draw_bar(surf, 20, xp_y, 210, 18 if xp_y == 38 else 14, self.xp / self.xp_to_next, (0, 30, 0), (0, 200, 80), border=(0, 180, 60), label=f"LVL {self.level}  {self.xp}/{self.xp_to_next} XP")
        surf.blit(FONT.render(f"Score:{self.score}  Credits:{self.credits}  Wave:{self.wave_num}", True, GREEN), (20, 62))
        gun = GUNS[self.equipped_gun]
        surf.blit(SFONT.render(f"Gun: {gun['name']}", True, gun["color"]), (20, 84))
        real_idx = self.boss_wave_idx % len(BOSS_WAVES)
        threshold = int(BOSS_WAVES[real_idx]["score"] * (1 + self.boss_repeat * 0.7))
        if not self.boss_active:
            self.draw_bar(surf, 20, 100, 210, 10, self.score / threshold, (30, 0, 30), (180, 0, 180), border=(120, 0, 120), label=f"BOSS: {self.score}/{threshold}")

    def draw_ability_panel(self, surf):
        px, py, pw, ph = self.panel_x(), 10, 165, sh() - 20
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((14, 14, 24, 220))
        surf.blit(panel, (px, py))
        pygame.draw.rect(surf, DKGRN, (px, py, pw, ph), 2)
        title = FONT.render("ABILITIES", True, GREEN)
        surf.blit(title, (px + pw // 2 - title.get_width() // 2, py + 8))
        y = py + 38
        for effect, meta in UPGRADE_META.items():
            count = self.upgrade_counts[effect]
            color = meta["color"]
            surf.blit(SFONT.render(f"[{meta['symbol']}]", True, color if count else GREY), (px + 8, y + 4))
            surf.blit(TFONT.render(meta["name"], True, WHITE if count else GREY), (px + 36, y + 4))
            surf.blit(SFONT.render(f"x{count}" if count else "-- locked --", True, color if count else GREY), (px + 36, y + 20))
            y += 44
        bottom = py + ph - 118
        gun = GUNS[self.equipped_gun]
        eff = self.get_gun_effective(self.equipped_gun)
        surf.blit(TFONT.render("EQUIPPED GUN", True, GREY), (px + 8, bottom))
        surf.blit(SFONT.render(gun["name"], True, gun["color"]), (px + 8, bottom + 14))
        surf.blit(TFONT.render(f"DMG:{eff['damage']}  SPD:{eff['bullet_speed']}", True, WHITE), (px + 8, bottom + 30))
        surf.blit(TFONT.render(f"RATE:{eff['fire_rate']}{'  PRCNG' if eff['piercing'] else ''}", True, WHITE), (px + 8, bottom + 44))
        level_y = py + ph - 52
        lv = FONT.render(f"LEVEL {self.level}", True, YELLOW)
        surf.blit(lv, (px + pw // 2 - lv.get_width() // 2, level_y))
        self.draw_bar(surf, px + 10, level_y + 22, pw - 20, 13, self.xp / self.xp_to_next, (20, 40, 20), (80, 255, 120), border=DKGRN, label=f"{self.xp}/{self.xp_to_next} XP")

    def draw_enemy_hp(self, surf, enemy):
        x, y, w = enemy.rect.x, enemy.rect.y - 9, enemy.rect.width
        ratio = max(0, enemy.hp / enemy.max_hp)
        pygame.draw.rect(surf, DKRED, (x, y, w, 5))
        pygame.draw.rect(surf, (0, 220, 0) if ratio > 0.5 else ORANGE if ratio > 0.25 else RED, (x, y, int(w * ratio), 5))
        pygame.draw.rect(surf, WHITE, (x, y, w, 5), 1)
        if enemy.kind == "boss":
            name = TFONT.render(f"{enemy.label}  {int(enemy.hp)}/{int(enemy.max_hp)}", True, enemy.color)
            surf.blit(name, (x, y - 13))

    def draw_upgrade_screen(self, surf, mx, my):
        overlay = pygame.Surface((sw(), sh()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        surf.blit(overlay, (0, 0))
        title = BFONT.render("LEVEL UP!", True, YELLOW)
        surf.blit(title, (sw() // 2 - title.get_width() // 2, 20))
        card_w, card_h, gap = 228, 128, 16
        rows = [self.current_choices[:3], self.current_choices[3:]]
        rects = {}
        for row_i, row in enumerate(rows):
            total_w = len(row) * card_w + (len(row) - 1) * gap
            x = sw() // 2 - total_w // 2
            y = 106 + row_i * (card_h + gap)
            for col_i, choice in enumerate(row):
                effect = choice["effect"]
                meta = UPGRADE_META[effect]
                color = meta["color"]
                rect = pygame.Rect(x + col_i * (card_w + gap), y, card_w, card_h)
                rects[effect] = rect
                hover = rect.collidepoint(mx, my)
                bg = pygame.Surface(rect.size, pygame.SRCALPHA)
                bg.fill((*color, 60 if hover else 25))
                surf.blit(bg, rect)
                pygame.draw.rect(surf, color, rect, 3 if hover else 2)
                surf.blit(BFONT.render(f"[{meta['symbol']}]", True, color), (rect.x + 8, rect.y + 8))
                surf.blit(FONT.render(meta["name"], True, WHITE), (rect.x + 72, rect.y + 12))
                count = self.upgrade_counts[effect]
                surf.blit(SFONT.render("[ UNLOCK ]" if count == 0 else f"[ UPGRADE  lv{count}->lv{count + 1} ]", True, GREEN if count == 0 else color), (rect.x + 72, rect.y + 36))
        return rects

    def draw_pause(self, surf, mx, my):
        overlay = pygame.Surface((sw(), sh()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        surf.blit(overlay, (0, 0))
        title = BFONT.render("PAUSED", True, CYAN)
        surf.blit(title, (sw() // 2 - title.get_width() // 2, sh() // 2 - 160))
        buttons = [pygame.Rect(sw() // 2 - 125, sh() // 2 - 80 + i * 60, 250, 50) for i in range(4)]
        labels = [("RESUME", GREEN), ("MAIN MENU", YELLOW), ("SETTINGS", GREY), ("QUIT GAME", RED)]
        for rect, (label, color) in zip(buttons, labels):
            self.draw_button(surf, rect, label, color, rect.collidepoint(mx, my))
        hint = TFONT.render("Press F1 to resume  |  F11 = fullscreen", True, GREY)
        surf.blit(hint, (sw() // 2 - hint.get_width() // 2, sh() // 2 + 165))
        fs_btn = self.draw_settings_panel(surf, mx, my, sw() // 2 + 131, sh() // 2 + 32) if self.settings_open else None
        return (*buttons, fs_btn)

    def draw_game_over(self, surf, mx, my):
        overlay = pygame.Surface((sw(), sh()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 215))
        surf.blit(overlay, (0, 0))
        title = BFONT.render("GAME OVER", True, RED)
        surf.blit(title, (sw() // 2 - title.get_width() // 2, sh() // 2 - 120))
        stats = FONT.render(f"Level {self.level}   Score {self.score}   Waves {self.wave_num}", True, YELLOW)
        surf.blit(stats, (sw() // 2 - stats.get_width() // 2, sh() // 2 - 65))
        play = pygame.Rect(sw() // 2 - 130, sh() // 2 + 10, 260, 52)
        menu = pygame.Rect(sw() // 2 - 130, sh() // 2 + 76, 260, 52)
        self.draw_button(surf, play, "PLAY AGAIN", GREEN, play.collidepoint(mx, my))
        self.draw_button(surf, menu, "MAIN MENU", YELLOW, menu.collidepoint(mx, my))
        return play, menu

    def update_playing(self, mx, my):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player.x -= self.player_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player.x += self.player_speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player.y -= self.player_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player.y += self.player_speed
        self.player.x = max(0, min(self.player.x, self.panel_x() - PLAYER_SIZE))
        self.player.y = max(0, min(self.player.y, sh() - PLAYER_SIZE))
        angle = math.atan2(my - self.player.centery, mx - self.player.centerx)
        self.shoot_timer += 1
        if pygame.mouse.get_pressed()[0] and self.shoot_timer > self.fire_rate:
            self.shoot(angle)
            self.shoot_timer = 0
        self.virus_timer += 1
        spawn_interval = max(10, 40 - self.wave_num * 2)
        if self.virus_timer > spawn_interval and not self.boss_active:
            self.virus_timer = 0
            side = random.randint(0, 3)
            if side == 0:
                ex, ey = random.randint(0, max(0, self.panel_x())), -VIRUS_SIZE
            elif side == 1:
                ex, ey = random.randint(0, max(0, self.panel_x())), sh()
            elif side == 2:
                ex, ey = -VIRUS_SIZE, random.randint(0, sh())
            else:
                ex, ey = self.panel_x(), random.randint(0, sh())
            hp, speed, dpt = virus_stats(self.wave_num)
            count = 1 + (self.wave_num > 3) + (self.wave_num > 7) + (2 if self.wave_num > 12 else 0) + (2 if self.wave_num > 18 else 0)
            for _ in range(count):
                self.viruses.append(Enemy(ex + random.randint(-40, 40), ey + random.randint(-40, 40), hp, speed, "virus", dpt, RED))
        self.try_spawn_boss()
        for enemy in self.viruses + self.hackers:
            enemy.move(self.player)
            if self.player.colliderect(enemy.rect):
                if self.shield_hp > 0:
                    self.shield_hp = max(0, self.shield_hp - enemy.dpt)
                else:
                    self.player_hp -= enemy.dpt
        dead_v, dead_h = [], []
        for enemy in self.viruses + self.hackers:
            for bullet in self.bullets[:]:
                enemy_id = id(enemy)
                if bullet["rect"].colliderect(enemy.rect) and enemy_id not in bullet["hit_set"]:
                    enemy.hp -= self.bullet_damage
                    bullet["hit_set"].add(enemy_id)
                    if not bullet["piercing"] and bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
            if enemy.hp <= 0:
                value = self.score // 10 + 50 if enemy.kind == "boss" else max(10, self.wave_num * 4)
                self.spawn_orb(enemy.rect.centerx, enemy.rect.centery, value)
                if enemy.kind == "boss" and random.randint(1, BOSS_CHEST_CHANCE) == 1:
                    self.chests.append(Chest(enemy.rect.centerx - CHEST_SIZE // 2, enemy.rect.centery - CHEST_SIZE // 2))
                elif enemy.kind == "virus" and random.randint(1, CHEST_DROP_CHANCE) == 1:
                    self.chests.append(Chest(enemy.rect.centerx - CHEST_SIZE // 2, enemy.rect.centery - CHEST_SIZE // 2))
                self.spawn_particles(enemy.rect.centerx, enemy.rect.centery, enemy.color if enemy.kind == "boss" else RED, 25 if enemy.kind == "boss" else 8)
                (dead_h if enemy.kind == "boss" else dead_v).append(enemy)
        for enemy in dead_v:
            if enemy in self.viruses:
                self.viruses.remove(enemy)
        boss_cleared = False
        for enemy in dead_h:
            if enemy in self.hackers:
                self.hackers.remove(enemy)
                boss_cleared = True
        if boss_cleared and not self.hackers:
            self.on_boss_killed()
        for bullet in self.bullets[:]:
            bullet["rect"].x += bullet["dx"]
            bullet["rect"].y += bullet["dy"]
            if not screen.get_rect().colliderect(bullet["rect"]):
                self.bullets.remove(bullet)
        for orb in self.orbs[:]:
            dx = self.player.centerx - orb["x"]
            dy = self.player.centery - orb["y"]
            dist = math.hypot(dx, dy)
            if dist < 120 and dist:
                orb["x"] += (dx / dist) * 2
                orb["y"] += (dy / dist) * 2
            orb["rect"].x = int(orb["x"])
            orb["rect"].y = int(orb["y"])
            if self.player.colliderect(orb["rect"]):
                self.xp += orb["value"]
                self.score += orb["value"]
                self.orbs.remove(orb)
        for chest in self.chests[:]:
            chest.update()
            if chest.state == "closed" and self.player.colliderect(chest.rect):
                chest.open()
                self.spawn_particles(chest.rect.centerx, chest.rect.centery, GOLD, 15)
            elif chest.state == "open" and self.player.colliderect(chest.rect):
                self.apply_item(chest.revealed_item)
                self.spawn_particles(chest.rect.centerx, chest.rect.centery, CHEST_ITEMS[chest.revealed_item]["color"], 20)
                self.chests.remove(chest)
        self.check_level_up()
        self.boss_announce_timer = max(0, self.boss_announce_timer - 1)
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
        if self.player_hp <= 0:
            self.game_over = True
            self.credits += self.score

    def draw_world(self, surf):
        surf.fill(DARK)
        for orb in self.orbs:
            radius = int(5 + 2 * math.sin(pygame.time.get_ticks() / 200 + orb["x"]))
            pygame.draw.circle(surf, YELLOW, (orb["rect"].x, orb["rect"].y), radius)
        for enemy in self.viruses:
            surf.blit(virus_img, enemy.rect)
            self.draw_enemy_hp(surf, enemy)
        for enemy in self.hackers:
            surf.blit(boss_img, enemy.rect)
            self.draw_enemy_hp(surf, enemy)
        color = GUNS[self.equipped_gun]["color"]
        for bullet in self.bullets:
            pygame.draw.rect(surf, color, bullet["rect"])
        for chest in self.chests:
            chest.draw(surf)
        for particle in self.particles:
            particle.draw(surf)
        if self.shield_hp > 0:
            radius = int(PLAYER_SIZE // 2 + 8 + 3 * math.sin(pygame.time.get_ticks() / 150))
            aura = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(aura, (*SHIELD_COL, int(60 + 40 * (self.shield_hp / MAX_SHIELD))), (radius + 2, radius + 2), radius, 4)
            surf.blit(aura, (self.player.centerx - radius - 2, self.player.centery - radius - 2))
        surf.blit(player_img, self.player)
        self.draw_hud(surf)
        self.draw_ability_panel(surf)
        self.draw_item_fx(surf)
        if self.boss_announce_timer > 0:
            banner = BFONT.render(self.boss_announce, True, RED)
            bg = pygame.Surface((banner.get_width() + 20, banner.get_height() + 10), pygame.SRCALPHA)
            bg.fill((0, 0, 0, min(200, self.boss_announce_timer * 4)))
            x = sw() // 2 - bg.get_width() // 2
            y = sh() // 2 - 60
            surf.blit(bg, (x, y))
            surf.blit(banner, (x + 10, y + 5))
        if self.dev_panel_open:
            x, y = 20, sh() - 160
            pygame.draw.rect(surf, (20, 20, 20), (x - 4, y - 4, 300, 110))
            pygame.draw.rect(surf, PURPLE, (x - 4, y - 4, 300, 110), 1)
            surf.blit(FONT.render("[DEV] F4 to close", True, PURPLE), (x, y))
            surf.blit(SFONT.render("1-Dmg 2-AtkSpd 3-Mvspd 4-Bspd 5-HP", True, GREY), (x, y + 22))
            surf.blit(SFONT.render(f"Lvl:{self.level} XP:{self.xp}/{self.xp_to_next} Wave:{self.wave_num} BossIdx:{self.boss_wave_idx} Rep:{self.boss_repeat}", True, WHITE), (x, y + 42))
            surf.blit(SFONT.render(f"Shld:{int(self.shield_hp)} Score:{self.score} VirHP:{round(virus_stats(self.wave_num)[0], 1)} VirDPT:{round(virus_stats(self.wave_num)[2], 2)}", True, WHITE), (x, y + 62))
            surf.blit(SFONT.render(f"SpawnInterval:{max(10, 40 - self.wave_num * 2)}  F11=fullscreen", True, WHITE), (x, y + 82))

    def draw_item_fx(self, surf):
        labels = {"magnet": "XP MAGNET!", "bomb": "NOVA BOMB!", "shield": "SHIELD UP!"}
        colors = {"magnet": CYAN, "bomb": ORANGE, "shield": SHIELD_COL}
        for fx in self.active_item_fx[:]:
            fx["timer"] -= 1
            ratio = fx["timer"] / fx["max"]
            color = colors.get(fx["kind"], WHITE)
            flash = pygame.Surface((sw(), sh()), pygame.SRCALPHA)
            flash.fill((*color, int(110 * ratio)))
            surf.blit(flash, (0, 0))
            label = BFONT.render(labels.get(fx["kind"], ""), True, color)
            surf.blit(label, (sw() // 2 - label.get_width() // 2, sh() // 2 - label.get_height() // 2))
            if fx["timer"] <= 0:
                self.active_item_fx.remove(fx)

    def handle_event(self, event, mx, my):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self.toggle_fullscreen()
                return
            if self.scene == "main_menu" and event.key == pygame.K_ESCAPE:
                self.settings_open = False
            elif self.scene in {"shop", "customise"} and event.key == pygame.K_ESCAPE:
                self.cust_drag_mod = None
                self.scene = "main_menu"
            elif self.scene == "playing":
                if event.key == pygame.K_F1 and not self.game_over and not self.choosing_upgrade:
                    self.paused = not self.paused
                    self.settings_open = False
                if event.key == pygame.K_F4:
                    self.dev_panel_open = not self.dev_panel_open
                if self.dev_panel_open and not self.game_over and not self.paused:
                    mapping = {pygame.K_1: "damage", pygame.K_2: "attack_speed", pygame.K_3: "move_speed", pygame.K_4: "bullet_speed", pygame.K_5: "max_hp"}
                    if event.key in mapping:
                        self.apply_upgrade(mapping[event.key])
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_down(event, mx, my)
        if self.scene == "customise" and event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.cust_drag_mod:
            _, _, slots, _, _, _ = self.draw_customise(screen, mx, my)
            self.drop_mod(slots, mx, my)

    def handle_mouse_down(self, event, mx, my):
        if self.scene == "main_menu":
            play, shop, customise, settings, quit_btn, fs_btn = self.draw_main_menu(screen, mx, my)
            if fs_btn and fs_btn.collidepoint(mx, my):
                self.toggle_fullscreen()
                self.settings_open = False
            elif settings.collidepoint(mx, my):
                self.settings_open = not self.settings_open
            elif play.collidepoint(mx, my):
                self.reset_game()
                self.scene = "playing"
                self.settings_open = False
            elif shop.collidepoint(mx, my):
                self.scene = "shop"
                self.settings_open = False
            elif customise.collidepoint(mx, my):
                self.cust_selected_gun = self.equipped_gun
                self.scene = "customise"
                self.settings_open = False
            elif quit_btn.collidepoint(mx, my):
                self.running = False
            else:
                self.settings_open = False
        elif self.scene == "shop":
            buy_rects, equip_rects, back = self.draw_shop(screen, mx, my)
            if back.collidepoint(mx, my):
                self.scene = "main_menu"
            for gid, rect in buy_rects.items():
                if rect.collidepoint(mx, my) and self.credits >= GUNS[gid]["price"]:
                    self.credits -= GUNS[gid]["price"]
                    self.owned_guns.add(gid)
            for gid, rect in equip_rects.items():
                if rect.collidepoint(mx, my):
                    self.equipped_gun = gid
        elif self.scene == "customise":
            chips, buys, slots, tabs, back, clear = self.draw_customise(screen, mx, my)
            if event.button == 1:
                if back.collidepoint(mx, my) and not self.cust_drag_mod:
                    self.scene = "main_menu"
                elif clear.collidepoint(mx, my) and not self.cust_drag_mod:
                    for mod in self.gun_mods[self.cust_selected_gun]:
                        self.mod_inventory[mod] += 1
                    self.gun_mods[self.cust_selected_gun].clear()
                else:
                    for key, rect in buys.items():
                        if rect.collidepoint(mx, my) and self.credits >= MOD_DEFS[key]["price"]:
                            self.credits -= MOD_DEFS[key]["price"]
                            self.mod_inventory[key] += 1
                            return
                    for gid, rect in tabs.items():
                        if rect.collidepoint(mx, my) and gid in self.owned_guns:
                            self.cust_selected_gun = gid
                            return
                    for key, rect in chips.items():
                        if rect.collidepoint(mx, my) and self.mod_inventory[key] > 0:
                            self.cust_drag_mod = key
                            self.cust_drag_from_inventory = True
                            return
                    for i, rect in enumerate(slots):
                        if rect.collidepoint(mx, my) and i < len(self.gun_mods[self.cust_selected_gun]):
                            self.cust_drag_mod = self.gun_mods[self.cust_selected_gun].pop(i)
                            self.cust_drag_from_inventory = False
                            return
            elif event.button == 3:
                for i, rect in enumerate(slots):
                    if rect.collidepoint(mx, my) and i < len(self.gun_mods[self.cust_selected_gun]):
                        removed = self.gun_mods[self.cust_selected_gun].pop(i)
                        self.mod_inventory[removed] += 1
                        return
        elif self.scene == "playing":
            if self.game_over:
                play, menu = self.draw_game_over(screen, mx, my)
                if play.collidepoint(mx, my):
                    self.reset_game()
                    self.scene = "playing"
                elif menu.collidepoint(mx, my):
                    self.scene = "main_menu"
            elif self.paused:
                resume, menu, settings, quit_btn, fs_btn = self.draw_pause(screen, mx, my)
                if fs_btn and fs_btn.collidepoint(mx, my):
                    self.toggle_fullscreen()
                    self.settings_open = False
                elif resume.collidepoint(mx, my):
                    self.paused = False
                    self.settings_open = False
                elif menu.collidepoint(mx, my):
                    self.scene = "main_menu"
                    self.settings_open = False
                elif settings.collidepoint(mx, my):
                    self.settings_open = not self.settings_open
                elif quit_btn.collidepoint(mx, my):
                    self.running = False
                else:
                    self.settings_open = False
            elif self.choosing_upgrade:
                rects = self.draw_upgrade_screen(screen, mx, my)
                for effect, rect in rects.items():
                    if rect.collidepoint(mx, my):
                        self.apply_upgrade(effect)
                        self.choosing_upgrade = False
                        return

    def drop_mod(self, slots, mx, my):
        mods = self.gun_mods[self.cust_selected_gun]
        dropped = False
        for i, rect in enumerate(slots):
            if rect.collidepoint(mx, my):
                mod = MOD_DEFS[self.cust_drag_mod]
                if i <= len(mods) and len(mods) < MAX_SLOTS and mods.count(self.cust_drag_mod) < mod["max_per_gun"]:
                    if i == len(mods):
                        mods.append(self.cust_drag_mod)
                    else:
                        mods.insert(i, self.cust_drag_mod)
                    if self.cust_drag_from_inventory:
                        self.mod_inventory[self.cust_drag_mod] -= 1
                else:
                    if not self.cust_drag_from_inventory:
                        self.mod_inventory[self.cust_drag_mod] += 1
                dropped = True
                break
        if not dropped and not self.cust_drag_from_inventory:
            self.mod_inventory[self.cust_drag_mod] += 1
        self.cust_drag_mod = None
        self.cust_drag_from_inventory = False

    def update_and_draw(self, mx, my):
        if self.scene == "main_menu":
            self.draw_main_menu(screen, mx, my)
        elif self.scene == "shop":
            self.draw_shop(screen, mx, my)
        elif self.scene == "customise":
            self.draw_customise(screen, mx, my)
        elif self.scene == "playing":
            if not self.paused and not self.choosing_upgrade and not self.game_over:
                self.update_playing(mx, my)
            self.draw_world(screen)
            if self.choosing_upgrade and not self.game_over and not self.paused:
                self.draw_upgrade_screen(screen, mx, my)
            if self.paused and not self.game_over:
                self.draw_pause(screen, mx, my)
            if self.game_over:
                self.draw_game_over(screen, mx, my)


async def main():
    init_runtime()
    game = Game()
    while game.running:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            game.handle_event(event, mx, my)
        game.update_and_draw(mx, my)
        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
