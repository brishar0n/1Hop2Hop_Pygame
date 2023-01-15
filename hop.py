import pygame # importing the libraries
import random
import os
from spritesheet import SpriteSheet
from enemy import Enemy

pygame.init() #initialise pygame

SCREEN_WIDTH = 400 # all caps since it's for constants
SCREEN_HEIGHT = 600

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # creating the game screen with our constants
pygame.display.set_caption('1 Hop 2 Hop') 
clock = pygame.time.Clock() # setting the frame rate
FPS = 60

SCROLL_THRESH = 200 # game variables
GRAVITY = 1
MAX_PLATFORMS = 10
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0

if os.path.exists('score.txt'):
	with open('score.txt', 'r') as file:
		high_score = int(file.read())
else:
	high_score = 0

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PANEL = (125,192,255)

font_small = pygame.font.SysFont('Arial', 20) # loading in the fonts
font_big = pygame.font.SysFont('Arial', 21)
avatar_image = pygame.image.load('images/avatar.png').convert_alpha() # loading in the images
bg_image = pygame.image.load('images/bg.png').convert_alpha()
platform_image = pygame.image.load('images/wood.png').convert_alpha()
#bird spritesheet
bird_sheet_img = pygame.image.load('images/bird.png').convert_alpha()
bird_sheet = SpriteSheet(bird_sheet_img)

def draw_text(text, font, text_col, x, y): # function for outputting text onto the window
	img = font.render(text, True, text_col)
	window.blit(img, (x, y))

def draw_panel(): # function for drawing info panel
	pygame.draw.rect(window, PANEL, (0, 0, SCREEN_WIDTH, 30))
	pygame.draw.line(window, WHITE, (0, 30), (SCREEN_WIDTH, 30), 2)
	draw_text('SCORE: ' + str(score), font_small, WHITE, 0, 0)

def draw_bg(bg_scroll): # function for drawing the background
	window.blit(bg_image, (0, 0 + bg_scroll))
	window.blit(bg_image, (0, -600 + bg_scroll))

class Player():
	def __init__(self, x, y): # x and y are the starting coordinates of the avatar/player
		self.image = pygame.transform.scale(avatar_image, (45, 45))
		self.width = 25
		self.height = 40
		self.rect = pygame.Rect(0, 0, self.width, self.height) # used for avatar for functionality
		self.rect.center = (x, y)
		self.vel_y = 0
		self.flip = False # flips the character based on the direction they're going

	def move(self):
		scroll = 0 # to reset the variables (d for delta means change)
		dx = 0
		dy = 0

		key = pygame.key.get_pressed() # keypress for moving to the left
		if key[pygame.K_a]:
			dx = -9
			self.flip = False
		if key[pygame.K_d]: # keypress for moving to the right
			dx = 9
			self.flip = True

		self.vel_y += GRAVITY # every iteration of the game loop, gravity increases by 1
		dy += self.vel_y 

		if self.rect.left + dx < 0: # ensure the character doesn't go out of the screen
			dx = -self.rect.left
		if self.rect.right + dx > SCREEN_WIDTH:
			dx = SCREEN_WIDTH - self.rect.right

		for platform in platform_group: # check collision with platforms
			#collision in the y direction
			if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				if self.rect.bottom < platform.rect.centery: #checking if above the platform
					if self.vel_y > 0:
						self.rect.bottom = platform.rect.top
						dy = 0
						self.vel_y = -20

		if self.rect.top <= SCROLL_THRESH: # check if the player has bounced to the top of the screen
			if self.vel_y < 0: #if player is jumping
				scroll = -dy

		self.rect.x += dx # to update the rectangle's position
		self.rect.y += dy + scroll

		self.mask = pygame.mask.from_surface(self.image) # update mask

		return scroll

	def draw(self): # basically to enable the character to have collisions (set the rect as character outline)
		window.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 12, self.rect.y - 5))

avatar = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150) # player instance for calling the functions

class Platform(pygame.sprite.Sprite): # built in support for sprites (objects with diff properties and it can move in diff directions)
	def __init__(self, x, y, width, moving):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(platform_image, (width, 10)) # resize image
		self.moving = moving # some will move and some will not
		self.move_counter = random.randint(0, 50)
		self.direction = random.choice([-1, 1])
		self.speed = random.randint(1, 2)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

	def update(self, scroll):
		if self.moving == True: # moving platform side to side
			self.move_counter += 1
			self.rect.x += self.direction * self.speed

		if self.move_counter >= 100 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH: # change platform direction if it has moved fully or hit a wall
			self.direction *= -1
			self.move_counter = 0

		self.rect.y += scroll # update platform's position

		if self.rect.top > SCREEN_HEIGHT: # check if platform has gone out of the screen
			self.kill()

platform_group = pygame.sprite.Group() # creating sprite groups
enemy_group = pygame.sprite.Group()

platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False) # creating the starting platform
platform_group.add(platform)

run = True # loop
while run:
	clock.tick(FPS) 
	if game_over == False:
		scroll = avatar.move()

		bg_scroll += scroll # making the background
		if bg_scroll >= 600:
			bg_scroll = 0
		draw_bg(bg_scroll)

		if len(platform_group) < MAX_PLATFORMS: # generate platforms
			p_w = random.randint(40, 60)
			p_x = random.randint(0, SCREEN_WIDTH - p_w)
			p_y = platform.rect.y - random.randint(80, 120)
			p_type = random.randint(1, 2)
			if p_type == 1 and score > 500:
				p_moving = True
			else:
				p_moving = False
			platform = Platform(p_x, p_y, p_w, p_moving)
			platform_group.add(platform)

		platform_group.update(scroll) # updating platforms

		if len(enemy_group) == 0 and score > 1500: # make enemies
			enemy = Enemy(SCREEN_WIDTH, 100, bird_sheet, 1.5)
			enemy_group.add(enemy)

		enemy_group.update(scroll, SCREEN_WIDTH) # updating enemies

		if scroll > 0: # update the score
			score += scroll

		pygame.draw.line(window, WHITE, (0, score - high_score + SCROLL_THRESH), (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 3) # line indicator for previous high score
		draw_text('HIGH SCORE', font_small, WHITE, SCREEN_WIDTH - 130, score - high_score + SCROLL_THRESH)

		platform_group.draw(window) # drawing sprites
		enemy_group.draw(window)
		avatar.draw()

		draw_panel() # drawing the panel

		if avatar.rect.top > SCREEN_HEIGHT: #checking for game over
			game_over = True
		if pygame.sprite.spritecollide(avatar, enemy_group, False): # checking for collision with bird
			if pygame.sprite.spritecollide(avatar, enemy_group, False, pygame.sprite.collide_mask):
				game_over = True
	else:
		if fade_counter < SCREEN_WIDTH:
			fade_counter += 5
			for y in range(0, 6, 2):
				pygame.draw.rect(window, BLACK, (0, y * 100, fade_counter, 100))
				pygame.draw.rect(window, BLACK, (SCREEN_WIDTH - fade_counter, (y + 1) * 100, SCREEN_WIDTH, 100))
		else:
			draw_text('GAME OVER!', font_big, WHITE, 130, 200)
			draw_text('SCORE: ' + str(score), font_big, WHITE, 130, 250)
			draw_text('PRESS SPACE TO PLAY AGAIN', font_big, WHITE, 40, 300)
			if score > high_score: # update the high score
				high_score = score
				with open('score.txt', 'w') as file:
					file.write(str(high_score))
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE]:
				game_over = False # reset variables
				score = 0
				scroll = 0
				fade_counter = 0
				avatar.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150) # reposition the avatar
				enemy_group.empty() # reset the bird enemies
				platform_group.empty() # reset the platforms
				platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False) # making the starting platform
				platform_group.add(platform)

	for event in pygame.event.get(): # driver
		if event.type == pygame.QUIT: # clicking the X button to quit
			if score > high_score: # update the high score
				high_score = score
				with open('score.txt', 'w') as file:
					file.write(str(high_score))
			run = False

	pygame.display.update() # update the screen
	
pygame.quit()