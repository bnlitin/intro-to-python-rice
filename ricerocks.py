'''
File:   ricerocks.py
Class:  Intro to Python - Rice University
Author: Boris Litinsky
Date:   11/10/2014
Description: Prequel to Asteroids
'''

# implementation of Spaceship - program template for RiceRocks
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
started = False
ship_group = set()
rock_group = set()
missile_group = set()
explosion_group = set()
        
class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_blue.png")

# sound assets purchased from sounddogs.com, please do not redistribute
# .ogg versions of sounds are also available, just replace .mp3 by .ogg
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
soundtrack.set_volume(1)
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")
explosion_sound.set_volume(.9)

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

# start new game
def new_game():
    global lives, score, time, started, missile_group, rock_group, explosion_group, ship_group
    lives = 3
    score = 0
    time = 0
    started = False
    missile_group   = set()
    rock_group      = set()
    explosion_group = set()
    ship_group      = set()
    
    # restart soundtrack
    soundtrack.rewind()
    soundtrack.play()
    
# Ship class
class Ship:

    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        
    def draw(self,canvas):
        if self.thrust:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0], self.image_center[1]] , self.image_size,
                              self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)
        # canvas.draw_circle(self.pos, self.radius, 1, "White", "White")

    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        # update velocity
        if self.thrust:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * .1
            self.vel[1] += acc[1] * .1
            
        self.vel[0] *= .99
        self.vel[1] *= .99

    def set_thrust(self, on):
        self.thrust = on
        if on:
            ship_thrust_sound.rewind()
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.pause()
       
    def increment_angle_vel(self):
        self.angle_vel += .05
        
    def decrement_angle_vel(self):
        self.angle_vel -= .05
        
    def shoot(self):
        global missile_group
        # limit shooting to 4 missile_group at a time
        if (len(missile_group) < 4):
            forward = angle_to_vector(self.angle)
            missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
            missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
            a_missile = Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound)
            missile_group.add(a_missile)
        
# Sprite class (used for rocks, missiles, and explosions)
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        self.dim = [24,0]
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        global time
        if (self.lifespan > 0):
            # if Sprite is animated, select the next tile to display
            if self.animated == True:
                anim_index = [ time % self.dim[0], self.dim[1]]
            else:
                anim_index = [0,0]
                
            canvas.draw_image(self.image, 
                                [self.image_center[0] + anim_index[0] * self.image_size[0], 
                                 self.image_center[1] + anim_index[1] * self.image_size[1]], 
                                 self.image_size, self.pos, self.image_size, self.angle)

    def collision(self, sprite):
        if dist(self.pos, sprite.pos) - (self.radius + sprite.radius) < 0:
            return True
        else:
            return False
        
    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
  
        if (self.lifespan > 0):
            self.lifespan -= 1  
        
# key handlers to control ship   
def keydown(key):
    global ship_group
    if len(ship_group) > 0:
        my_ship = min(ship_group)
        if key == simplegui.KEY_MAP['left']:
            my_ship.decrement_angle_vel()
        elif key == simplegui.KEY_MAP['right']:
            my_ship.increment_angle_vel()
        elif key == simplegui.KEY_MAP['up']:
            my_ship.set_thrust(True)
        elif key == simplegui.KEY_MAP['space']:
            my_ship.shoot()
        
def keyup(key):
    global ship_group
    if len(ship_group) > 0:
        my_ship = min(ship_group)
        if key == simplegui.KEY_MAP['left']:
            my_ship.increment_angle_vel()
        elif key == simplegui.KEY_MAP['right']:
            my_ship.decrement_angle_vel()
        elif key == simplegui.KEY_MAP['up']:
            my_ship.set_thrust(False)
        
# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        new_game()
        started = True

# process sprite group
def process_sprite_group(canvas, sprite_group):
    for sprite in list(sprite_group):
        sprite.draw(canvas)
        sprite.update()
        if sprite.lifespan < 1:
            sprite_group.remove(sprite)  
        
# draw sprites, update positions, and detect collisions
def draw(canvas):
    global time, started, lives, score, ship_group, rock_group, missile_group, explosion_group
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw UI
    canvas.draw_text("Lives", [50, 50], 22, "White")
    canvas.draw_text("Score", [680, 50], 22, "White")
    canvas.draw_text(str(lives), [50, 80], 22, "White")
    canvas.draw_text(str(score), [680, 80], 22, "White")

    process_sprite_group(canvas,ship_group)
    process_sprite_group(canvas,rock_group)
    process_sprite_group(canvas,missile_group)
    process_sprite_group(canvas,explosion_group)
    
    # check for collisions between ship, missiles, and rock_group
    for rock in rock_group:

        # if a ship exists
        if len(ship_group) > 0:
            my_ship = min(ship_group)
            
            # if a ship collided with a rock
            if rock.collision(my_ship):
                ship_group.remove(my_ship)
                lives -= 1
                if (lives < 1):
                    started = False
                    rock_group = set()
                    
                # create an explosion sprite at the location of the ship
                explosion = Sprite(my_ship.pos, my_ship.vel, 0, 0, explosion_image, explosion_info, explosion_sound)
                explosion_group.add(explosion)
                
        for missile in missile_group:
            # if a missile hit a rock
            if rock.collision(missile):
                score +=1
                missile_group.remove(missile)
                rock_group.remove(rock)
                
                # create an explosion sprite at the location of the rock
                explosion = Sprite(rock.pos, rock.vel, 0,0, explosion_image, explosion_info, explosion_sound)
                explosion_group.add(explosion)
    
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())


# timer handler that spawns a rock    
def rock_spawner():
    global rock_group, score
    if started and len(rock_group) < 12:
        # speed up rock velocity as game progresses based on player score
        speedup = (score // 10) * 1.0 + 1.0
        rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
        
        # prevent rocks spawning at the same location as the ship
        if len(ship_group) > 0:
            my_ship = min(ship_group)
            if abs(my_ship.pos[0] - rock_pos[0]) < my_ship.radius:
                rock_pos[0] = rock_pos[0] + 2 * my_ship.radius
            if abs(my_ship.pos[1] - rock_pos[1]) < my_ship.radius:
                rock_pos[1] = rock_pos[1] + 2 * my_ship.radius                
                      
        rock_vel = [(random.random() * .6 - .3)*speedup, (random.random() * .6 - .3)*speedup]
        rock_avel = random.random() * .2 - .1
        a_rock = Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image, asteroid_info)
        rock_group.add(a_rock)

# spawn a new ship after explosion
def ship_spawner():
    global ship_group, time
    if started and len(ship_group) < 1:
        my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
        ship_group.add(my_ship)
            
# main game routine
def main():
    # initialize stuff
    frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)
    
    # register handlers
    frame.set_keyup_handler(keyup)
    frame.set_keydown_handler(keydown)
    frame.set_mouseclick_handler(click)
    frame.set_draw_handler(draw)
    
    timer1 = simplegui.create_timer(1000.0, rock_spawner)
    timer2 = simplegui.create_timer(1000.0, ship_spawner)
    
    # get things rolling
    timer1.start()
    timer2.start()
    frame.start()
    
    # start game
    new_game()
    
if __name__ == '__main__':
    main()