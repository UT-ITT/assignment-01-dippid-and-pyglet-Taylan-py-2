import pyglet
import random
import os
import time
import math
from DIPPID import SensorUDP

# --- 1. DIPPID SETUP ---
PORT = 5700
sensor = SensorUDP(PORT, '0.0.0.0') 

# --- 2. WINDOW SETUP (FULLSCREEN) ---
window = pyglet.window.Window(fullscreen=True, caption="Face Invaders")
WIDTH = window.width
HEIGHT = window.height
batch = pyglet.graphics.Batch() 

# --- 3. ASSET LOADING ---
path = './sprites/cutout/'
img_closed = pyglet.image.load(os.path.join(path, 'img_mouth_closed.png'))
img_open = pyglet.image.load(os.path.join(path, 'img_mouth_open.png'))
img_ta_1 = pyglet.image.load(os.path.join(path, 'img_ta_1.png'))
img_ta_2 = pyglet.image.load(os.path.join(path, 'img_ta_2.png')) 
img_prof = pyglet.image.load(os.path.join(path, 'img_prof.png'))
img_dead = pyglet.image.load(os.path.join(path, 'img_player_dead.png'))

# Load Sounds (Routing to the sounds directory)
sound_path = 'sounds'

# Short sound effects (loaded directly into memory)
sound_shoot = pyglet.media.load(os.path.join(sound_path, 'pew.wav'), streaming=False)
sound_die = pyglet.media.load(os.path.join(sound_path, 'ohnoooo.wav'), streaming=False)
sound_score = pyglet.media.load(os.path.join(sound_path, 'destroy.wav'), streaming=False)

# Background Music Setup
bg_music = pyglet.media.load(os.path.join(sound_path, 'TempleOS_Hymn-Risen.wav'), streaming=True)
bg_player = pyglet.media.Player()
bg_player.queue(bg_music)
bg_player.loop = True     
bg_player.volume = 0.1    # Made it even quieter (10% volume)
bg_player.play()          

# --- 4. GAME STATE & LISTS ---
player_bullets = []
enemy_bullets = []
enemies = []
bunkers = []
stars = []

is_dead = False
score = 0
level = 1
enemy_speed = 100
enemy_direction = 1 
pending_shots = 0
bunker_timer = 0.0 # Timer to track laptop respawns

score_label = pyglet.text.Label(f"SCORE: {score}", font_name='Courier', font_size=28,
                                x=30, y=HEIGHT-40, batch=batch)
level_label = pyglet.text.Label(f"LEVEL: {level}", font_name='Courier', font_size=28,
                                x=WIDTH-200, y=HEIGHT-40, batch=batch)

# --- 5. INITIALIZE STATIC MENU ELEMENTS ---
game_over_title = pyglet.text.Label("THE UNIVERSITY WINS!", font_name='Arial', font_size=60, color=(255,0,0,255),
                                            x=WIDTH//2, y=HEIGHT//2 + 50, anchor_x='center', anchor_y='center')
game_over_subtitle = pyglet.text.Label("TAYLAN WAS EXPELLED!", font_name='Arial', font_size=40, color=(255,100,100,255),
                                            x=WIDTH//2, y=HEIGHT//2 - 20, anchor_x='center', anchor_y='center')

# Respawn Button
respawn_rect = pyglet.shapes.Rectangle(WIDTH // 2 - 100, HEIGHT // 2 - 110, 200, 50, color=(128, 128, 128))
respawn_label = pyglet.text.Label("RESPAWN", font_name='Courier', font_size=36, color=(255, 255, 255, 255),
                                  x=WIDTH//2, y=HEIGHT//2 - 85, anchor_x='center', anchor_y='center')

# Quit Button (Placed right below Respawn with a reddish tint)
quit_rect = pyglet.shapes.Rectangle(WIDTH // 2 - 100, HEIGHT // 2 - 180, 200, 50, color=(150, 50, 50))
quit_label = pyglet.text.Label("QUIT", font_name='Courier', font_size=36, color=(255, 255, 255, 255),
                                  x=WIDTH//2, y=HEIGHT//2 - 155, anchor_x='center', anchor_y='center')

# --- 6. CLASSES ---

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.randint(50, 150)
        self.size = random.randint(1, 3)
        self.sprite = pyglet.shapes.Rectangle(self.x, self.y, self.size, self.size, color=(255,255,255), batch=batch)

    def update(self, dt):
        self.y -= self.speed * dt
        if self.y < 0:
            self.y = HEIGHT
            self.x = random.randint(0, WIDTH)
        self.sprite.y = self.y

class Bunker:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 120
        self.height = 40
        self.health = 2 
        self.sprite = pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, color=(0, 255, 255), batch=batch)
        
    def take_damage(self):
        self.health -= 1
        if self.health == 1:
            self.sprite.color = (255, 0, 0) 

class Player:
    def __init__(self):
        self.width = 120  
        self.height = 120 
        self.x = WIDTH // 2 - (self.width // 2)
        self.y = 80
        self.speed = 1500
        
        self.target_width = self.width
        self.target_height = self.height
        
        self.sprite = pyglet.sprite.Sprite(img_closed, x=self.x, y=self.y, batch=batch)
        self._calculate_scaling(img_closed)
        
    def swap_image(self, new_image):
        self.sprite.image = new_image
        if new_image.width > 0 and new_image.height > 0:
            self._calculate_scaling(new_image)
        else:
            self.sprite.scale_x = 1.0 
            self.sprite.scale_y = 1.0

    def _calculate_scaling(self, image):
        self.sprite.scale_x = self.target_width / image.width
        self.sprite.scale_y = self.target_height / image.height

    def open_mouth(self):
        self.swap_image(img_open)
        pyglet.clock.schedule_once(self.close_mouth, 0.2)
        
    def close_mouth(self, dt=None):
        self.swap_image(img_closed)

    def update_position(self, dt):
        if not is_dead and sensor.has_capability('accelerometer'):
            tilt_y = float(sensor.get_value('accelerometer')['y'])
            self.x += tilt_y * self.speed * dt
            
            if self.x < 0: self.x = 0
            if self.x > WIDTH - self.width: self.x = WIDTH - self.width
            self.sprite.x = self.x

class Bullet:
    def __init__(self, x, y, is_enemy=False, char='0', color=(0,255,0,255), vx=0, vy=800):
        self.x = x
        self.y = y
        self.width = 15
        self.height = 20
        self.is_enemy = is_enemy
        self.vx = vx
        self.vy = vy
            
        self.label = pyglet.text.Label(char, font_name='Courier', font_size=24, color=color,
                                       x=self.x, y=self.y, batch=batch)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.label.x = self.x
        self.label.y = self.y

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 60
        self.enemy_type = enemy_type
        
        if enemy_type == "boss": 
            img = img_prof
            self.health = 3
        elif enemy_type == "ta2": 
            img = img_ta_2
            self.health = 2
        else: 
            img = img_ta_1
            self.health = 1
            
        self.sprite = pyglet.sprite.Sprite(img, x=self.x, y=self.y, batch=batch)
        self.sprite.scale_x = self.width / img.width
        self.sprite.scale_y = self.height / img.height

    def take_damage(self):
        self.health -= 1
        if self.health > 0:
            self.sprite.color = (255, 100, 100)

    def update_visuals(self):
        self.sprite.x = self.x
        self.sprite.y = self.y


# --- 7. INITIALIZATION FUNCTIONS ---
player = Player()

for _ in range(75):
    stars.append(Star())

def spawn_bunkers():
    bunkers.clear()
    bunker_spacing = WIDTH // 5
    for i in range(1, 5):
        bx = (i * bunker_spacing) - 60
        bunkers.append(Bunker(bx, 240))

def spawn_enemies():
    enemies.clear()
    columns = 8
    rows = 3 + level 
    grid_width = columns * 90
    start_x = (WIDTH - grid_width) // 2

    for row in range(rows):
        for col in range(columns):
            ex = start_x + (col * 90)
            ey = HEIGHT - 200 + (row * 70)
            
            if row == rows - 1:
                e_type = "boss"
            elif row % 2 == 0:
                e_type = "ta1"
            else:
                e_type = "ta2"
                
            enemies.append(Enemy(ex, ey, e_type))

# --- 8. RESET GAME FUNCTION ---
def reset_game():
    global is_dead, score, level, enemy_speed, enemy_direction, pending_shots, bunker_timer
    player_bullets.clear()
    enemy_bullets.clear()
    
    is_dead = False
    score = 0
    level = 1
    enemy_speed = 100
    enemy_direction = 1
    pending_shots = 0
    bunker_timer = 0.0 
    
    score_label.text = f"SCORE: {score}"
    level_label.text = f"LEVEL: {level}"
    
    spawn_bunkers()
    spawn_enemies()
    
    player.swap_image(img_closed)
    player.x = WIDTH // 2 - (player.width // 2)
    player.sprite.x = player.x
    player.sprite.y = player.y
    
    # Restart the music when respawning!
    bg_player.play()

# Start Game
reset_game()

# --- 9. DIPPID CALLBACK ---
def handle_button(data):
    global pending_shots
    if int(data) == 1 and not is_dead:
        pending_shots += 1

sensor.register_callback('button_1', handle_button)

# --- 10. COLLISION DETECTION ---
def check_collision(obj1, obj2):
    return (obj1.x < obj2.x + obj2.width and
            obj1.x + obj1.width > obj2.x and
            obj1.y < obj2.y + obj2.height and
            obj1.y + obj1.height > obj2.y)

# --- 11. GAME LOOP ---
def update(dt):
    global enemy_direction, is_dead, pending_shots, score, level, enemy_speed, bunker_timer

    if is_dead: 
        # Smooth bobbing animation for faces on the end screen
        t = time.time()
        # Bob player
        player.sprite.y = player.y + math.sin(t * 4) * 8
        # Bob enemies slightly out of phase with each other
        for i, e in enumerate(enemies):
            e.sprite.y = e.y + math.sin(t * 3 + i) * 6
        return 
    
    bunker_timer += dt
    if bunker_timer >= 20.0:
        spawn_bunkers() 
        bunker_timer = 0.0
    
    if len(enemies) == 0:
        level += 1
        level_label.text = f"LEVEL: {level}"
        enemy_speed = 100 + (level * 20) 
        spawn_enemies()
    
    for s in stars:
        s.update(dt)

    player.update_position(dt)
    
    while pending_shots > 0:
        bullet_x = player.x + (player.width / 2) - 5
        bullet_y = player.y + player.height
        char = random.choice(['0', '1'])
        player_bullets.append(Bullet(bullet_x, bullet_y, is_enemy=False, char=char, color=(0,255,0,255), vx=0, vy=800))
        player.open_mouth()
        sound_shoot.play() 
        pending_shots -= 1  

    for b in player_bullets[:]: 
        b.update(dt)
        if b.y > HEIGHT: player_bullets.remove(b)

    for b in enemy_bullets[:]:
        b.update(dt)
        if b.y < 0 or b.x < 0 or b.x > WIDTH: enemy_bullets.remove(b)

    move_down = False
    for e in enemies:
        e.x += enemy_speed * enemy_direction * dt
        e.update_visuals()
        
        if e.x > WIDTH - e.width or e.x < 0:
            move_down = True
            
        if random.random() < 0.001:
            bx = e.x + (e.width/2)
            by = e.y
            
            if e.enemy_type == "ta1":
                enemy_bullets.append(Bullet(bx, by, is_enemy=True, char='F', color=(255,0,0,255), vx=0, vy=-400))
            elif e.enemy_type == "ta2":
                enemy_bullets.append(Bullet(bx, by, is_enemy=True, char='0', color=(255,165,0,255), vx=0, vy=-700))
            elif e.enemy_type == "boss":
                enemy_bullets.append(Bullet(bx, by, is_enemy=True, char='?', color=(255,0,255,255), vx=-150, vy=-400))
                enemy_bullets.append(Bullet(bx, by, is_enemy=True, char='?', color=(255,0,255,255), vx=0, vy=-400))
                enemy_bullets.append(Bullet(bx, by, is_enemy=True, char='?', color=(255,0,255,255), vx=150, vy=-400))

    if move_down:
        enemy_direction *= -1
        for e in enemies:
            e.y -= 30
            e.update_visuals()
            for bunker in bunkers[:]:
                if check_collision(e, bunker):
                    bunker.sprite.x = -1000
                    bunkers.remove(bunker)
            
            if e.y <= player.y + player.height:
                if not is_dead: 
                    sound_die.play() 
                    bg_player.pause() # Stop the music!
                is_dead = True
                player.swap_image(img_dead)

    # --- RESOLVE COLLISIONS ---
    for b in player_bullets[:]:
        for e in enemies[:]:
            if check_collision(b, e):
                if b in player_bullets: player_bullets.remove(b)
                if e in enemies: 
                    e.take_damage()
                    if e.health <= 0:
                        sound_score.play() 
                        if e.enemy_type == "boss": score += 150
                        elif e.enemy_type == "ta2": score += 50
                        else: score += 10
                        
                        score_label.text = f"SCORE: {score}"
                        e.sprite.x = -1000 
                        enemies.remove(e)
                break

    for b in player_bullets[:]:
        for bunker in bunkers[:]:
            if check_collision(b, bunker):
                if b in player_bullets: player_bullets.remove(b)
                bunker.take_damage()
                if bunker.health <= 0:
                    bunker.sprite.x = -1000
                    bunkers.remove(bunker)
                break

    for b in enemy_bullets[:]:
        for bunker in bunkers[:]:
            if check_collision(b, bunker):
                if b in enemy_bullets: enemy_bullets.remove(b)
                bunker.take_damage()
                if bunker.health <= 0:
                    bunker.sprite.x = -1000
                    bunkers.remove(bunker)
                break
                
    for b in enemy_bullets[:]:
        if check_collision(b, player):
            if not is_dead: 
                sound_die.play()
                bg_player.pause() # Stop the music!
            is_dead = True
            player.swap_image(img_dead)


# --- 12. DRAW LOOP ---
@window.event
def on_draw():
    window.clear()
    batch.draw() 
    
    if is_dead:
        game_over_title.draw()
        game_over_subtitle.draw()
        respawn_rect.draw()
        respawn_label.draw()
        quit_rect.draw()
        quit_label.draw()
        
# --- 13. MOUSE EVENTS ---
@window.event
#def on_mouse_press(x, y, button, modifiers):
#    if is_dead and button == pyglet.window.mouse.LEFT:
#        # Check if Respawn was clicked
#        if respawn_rect.x <= x <= respawn_rect.x + respawn_rect.width and \
#           respawn_rect.y <= y <= respawn_rect.y + respawn_rect.height:
#            reset_game()
#        
#        # Check if Quit was clicked
#        elif quit_rect.x <= x <= quit_rect.x + quit_rect.width and \
#             quit_rect.y <= y <= quit_rect.y + quit_rect.height:
#            pyglet.app.exit()

def on_mouse_press(x, y, button, modifiers):
    if is_dead and button == pyglet.window.mouse.LEFT:
        # Check Respawn
        if (WIDTH//2 - 100 <= x <= WIDTH//2 + 100) and (HEIGHT//2 - 110 <= y <= HEIGHT//2 - 60):
            reset_game()
        # Check Quit
        elif (WIDTH//2 - 100 <= x <= WIDTH//2 + 100) and (HEIGHT//2 - 180 <= y <= HEIGHT//2 - 130):
            window.close() # Direct window closure is safer than app.exit()


pyglet.clock.schedule_interval(update, 1/60.0)

if __name__ == '__main__':
    pyglet.app.run()