import pygame
from pygame.locals import *
import random
import time

pygame.init()

#window creation
width = 500
height = 500
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Car game')

#colors
gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)

#road and marker sizes
road_width = 416
marker_width = 5
marker_height = 50

#lane coordinates
left_lane = 104
middle_left_lane = 208
middle_right_lane = 312
right_lane = 416
lanes = [left_lane, middle_left_lane, middle_right_lane, right_lane]

#road and edge markers
road = (44, 0, road_width, height)
left_edge_marker = (50, 0, marker_width, height)
right_edge_marker = (450, 0, marker_width, height)

#for animating movement of the lane markers
lane_marker_move_y = 0

#player's starting coordinates
player_x = middle_left_lane
player_y = 400

#frame settings
clock = pygame.time.Clock()
fps = 120

#game settings
gameover = False
speed = 1
score = 0


class Vehicle(pygame.sprite.Sprite):

    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        #scale down
        image_scale = 100 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image,(new_height, new_width))

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class PlayerVehicle(Vehicle):

    def __init__(self, x, y):
        image = pygame.image.load('/home/vairo/vscode/py/games/traficar/vehicle_sprites/Audi.png')
        super().__init__(image, x, y)

#sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

#load player vehicle image
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

#load other vehicles images
image_filenames = ['Ambulance.png', 'Black_viper.png', 'Car.png', 'Mini_truck.png', 'Mini_van.png', 'Police.png', 'taxi.png']
vehicle_images = []
for image_filename in image_filenames:
    image = pygame.image.load('/home/vairo/vscode/py/games/traficar/vehicle_sprites/' + image_filename)
    vehicle_images.append(image)


#load crash image
crash = pygame.image.load('/home/vairo/vscode/py/games/traficar/crash_sprites/explosion0.png')
crash_rect = crash.get_rect()


#game loop
running = True
gameover = False

# Score timer
score_timer = pygame.time.get_ticks()  # Get initial time in milliseconds
score_interval = 1000  # 5 seconds interval (in milliseconds)

while running:
    
    clock.tick(fps)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            
        #control
        if event.type == KEYDOWN:
            if event.key == K_a:
                if player.rect.center[0] > left_lane:
                    player.rect.x -= 104
            elif event.key == K_d:
                if player.rect.center[0] < right_lane:
                    player.rect.x += 104

                
            #check side swipe collision
            for vehicle in vehicle_group:
                if player.rect.center[0] == vehicle.rect.center[0] and player.rect.colliderect(vehicle.rect):
                    # Collision occurred

                    
                    gameover = True
                    
                    # position of the crash 
                    if event.key == K_a:
                        player.rect.left = vehicle.rect.right
                        crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                    elif event.key == K_d:
                        player.rect.right = vehicle.rect.left
                        crash_rect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]

        
    #grass
    screen.fill(green)

    #road
    pygame.draw.rect(screen, gray, road)

    #edge markers
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)

    #lane markers
    lane_marker_move_y += speed * 2
    if lane_marker_move_y >=marker_height * 2:
        lane_marker_move_y = 0
    for y in range(marker_height * -2, height, marker_height * 2):
        pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (middle_left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (middle_right_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        


    #player car
    player_group.draw(screen)

    #add up to 7 vehicles
    if len(vehicle_group) < 7:

        #enough space between vehicles
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height:
                add_vehicle = False

        if add_vehicle:

            #random lane
            lane = random.choice(lanes)

            #random vehicle
            image = random.choice(vehicle_images)
            vehicle = Vehicle(image, lane, height / -5)
            vehicle_group.add(vehicle)


    #move vehicles
    for vehicle in vehicle_group:
        vehicle.rect.y += speed

        #remove vehicle on offscreen
        if vehicle.rect.top >= height:
            vehicle.kill()
            

    #draw vehicles
    vehicle_group.draw(screen)

    #score
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render('Score: ' + str(score), True, white)
    text_rect = text.get_rect()
    text_rect.center = (50, 450)
    screen.blit(text, text_rect)

    # Increase score every 1 seconds
    current_time = pygame.time.get_ticks()  # Get current time in milliseconds
    if current_time - score_timer >= score_interval:
        score += 1
        score_timer = current_time  # Reset the timer


    #head crash
    if pygame.sprite.spritecollide(player, vehicle_group, False, pygame.sprite.collide_rect_ratio(0.8)):
    # Collision occurred
        gameover = True
        crash_rect.center = [player.rect.center[0], player.rect.top]


    #crash
    if gameover:
        screen.blit(crash, crash_rect)

        pygame.draw.rect(screen, red, (0, 50, width, 100))
        
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Game over. Play again? (y/n)', True, white)
        text_rect = text.get_rect()
        text_rect.center = (width / 2, 100)
        screen.blit(text, text_rect)


    pygame.display.update()

    #play again
    while gameover:

        clock.tick(fps)

        for event in pygame.event.get():

            if event.type == QUIT:
                gameover = False
                running = False
            
            #player's input
            if event.type == KEYDOWN:
                if event.key == K_y:
                    #restart
                    gameover = False
                    speed = 1
                    score = 0
                    vehicle_group.empty()
                    player.rect.center = (player_x, player_y)
                elif event.key == K_n:
                    gameover = False
                    running = False

pygame.quit()