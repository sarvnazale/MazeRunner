import arcade
import random
from numpy.random import randint

# Screen constants
WIDTH = 1000
HEIGHT = 800
TITLE = "Maze Game"

# Constants used to scale sprites from their original size
BUNNY_SCALING = 0.05
TURTLE_SCALING = 0.8
TILE_SCALING = 0.5
COIN_SCALING = 0.35

SPRITE_SCALING = 0.25
DIVIDER_SCALING = 0.50
SPRITE_SIZE = 32

# Speed constant 
PLAYER_MOVEMENT_SPEED = 5

TILE_EMPTY = 0
TILE_CRATE = 1

# Maze must have an ODD number of rows and columns.
# Walls go on EVEN rows/columns.
# Openings go on ODD rows/columns

MAZE_HEIGHT = 51
MAZE_WIDTH = 51


MERGE_SPRITES = True

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 200

#set booleans for game control
start_game = True
run_game = False
end_game = False
pause = False


#Create maze
def create_empty_grid(width, height, default_value=TILE_EMPTY):
    """ Create an empty grid. """
    grid = []
    for row in range(height):
        grid.append([])
        for column in range(width):
            grid[row].append(default_value)
    return grid


def create_outside_walls(maze):
    """ Create outside border walls."""

    # Create left and right walls
    for row in range(len(maze)):
        maze[row][0] = TILE_CRATE
        maze[row][len(maze[row])-1] = TILE_CRATE

    # Create top and bottom walls
    for column in range(1, len(maze[0]) - 1):
        maze[0][column] = TILE_CRATE
        maze[len(maze) - 1][column] = TILE_CRATE


def make_maze_recursive_call(maze, top, bottom, left, right):
    """
    Recursive function to divide up the maze in four sections
    and create three gaps.
    Walls can only go on even numbered rows/columns.
    Gaps can only go on odd numbered rows/columns.
    Maze must have an ODD number of rows and columns.
    """

    # Figure out where to divide horizontally
    start_range = bottom + 2
    end_range = top - 1
    y = random.randrange(start_range, end_range, 2)

    # Do the division
    for column in range(left + 1, right):
        maze[y][column] = TILE_CRATE

    # Figure out where to divide vertically
    start_range = left + 2
    end_range = right - 1
    x = random.randrange(start_range, end_range, 2)

    # Do the division
    for row in range(bottom + 1, top):
        maze[row][x] = TILE_CRATE

    # Now we'll make a gap on 3 of the 4 walls.
    # Figure out which wall does NOT get a gap.
    wall = random.randrange(4)
    if wall != 0:
        gap = random.randrange(left + 1, x, 2)
        maze[y][gap] = TILE_EMPTY

    if wall != 1:
        gap = random.randrange(x + 1, right, 2)
        maze[y][gap] = TILE_EMPTY

    if wall != 2:
        gap = random.randrange(bottom + 1, y, 2)
        maze[gap][x] = TILE_EMPTY

    if wall != 3:
        gap = random.randrange(y + 1, top, 2)
        maze[gap][x] = TILE_EMPTY

    # If there's enough space, to a recursive call.
    if top > y + 3 and x > left + 3:
        make_maze_recursive_call(maze, top, y, left, x)

    if top > y + 3 and x + 3 < right:
        make_maze_recursive_call(maze, top, y, x, right)

    if bottom + 3 < y and x + 3 < right:
        make_maze_recursive_call(maze, y, bottom, x, right)

    if bottom + 3 < y and x > left + 3:
        make_maze_recursive_call(maze, y, bottom, left, x)


def make_maze_recursion(maze_width, maze_height):
    """ Make the maze by recursively splitting it into four rooms. """
    maze = create_empty_grid(maze_width, maze_height)
    # Fill in the outside walls
    create_outside_walls(maze)

    # Start the recursive process
    make_maze_recursive_call(maze, maze_height - 1, 0, 0, maze_width - 1)
    return maze


def draw_main_screen(x: int, y: int):
    # sets a new background, draws title text
    scale = 1
    texture = arcade.load_texture("mainscreen.png")
    arcade.draw_texture_rectangle(x, y, scale * texture.width,
                                  scale * texture.height, texture, 0)


def draw_background():
    arcade.set_background_color(arcade.csscolor.LIGHT_GOLDENROD_YELLOW)

def draw_end_screen(x: int, y: int, winner):
    scale = 3
    #sets a new background, draws end game text
    texture = arcade.load_texture("endscreen.png")
    arcade.draw_texture_rectangle(x, y, scale * texture.width,
                                  scale * texture.height, texture, 0)

    arcade.draw_text("GAME OVER!", 270, 500, arcade.color.BLACK, 65)
    arcade.draw_text("The winner of the game is...", 270, 300, arcade.color.BLACK, 30)
    arcade.draw_text(winner, 420, 230, arcade.color.BLACK, 30)
    


def pause_screen():
    """ creates a pause screen """
    scale = 1
    texture = arcade.load_texture("pausescreen.png")
    arcade.draw_texture_rectangle (500, 400, scale * texture.width,
                                  scale * texture.height, texture, 0)


#Main application class
class MyGame(arcade.Window):

    #this method is used to create sprites 
    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(WIDTH, HEIGHT, TITLE)
       
        #create empty lists for variables 
        self.coin_list = None
        self.wall_list = None
        self.player_list = None

        #variables holding the two players
        self.bunny_sprite = None
        self.turtle_sprite = None
        
        #coin variable
        self.coin = None
        
        #physics engine for each player
        self.physics_engine_bunny = None
        self.physics_engine_turtle = None

        # Keep track of the score
        self.score_bunny = 0
        self.score_turtle = 0
    

        # Load sounds
        self.collect_coin_sound_bunny = arcade.load_sound("coin1.wav")
        self.collect_coin_sound_turtle = arcade.load_sound("coin5.wav")
        
        self.total_time = 00.0

    def setup(self):
        #used to set up the game and restart when the game is over
        self.total_time = 00.0

        # Keep track of the score
        self.score_bunny = 0
        self.score_turtle = 0


        #creating the sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True) #spatial_hash is used because 
        self.coin_list = arcade.SpriteList(use_spatial_hash=True) #the wall and coins won't move
        


        #Creates the ground
        for x in range(0, 1250, 64):
            wall = arcade.Sprite("dirtCenter.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 0
            self.wall_list.append(wall)


        #creates the top part
        for x in range(0, 1250, 64):
            wall = arcade.Sprite("dirtCenter.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 800
            self.wall_list.append(wall)

        # Create the maze
        maze = make_maze_recursion(MAZE_WIDTH, MAZE_HEIGHT)
        

        # Create the right wall
        for x in range(0, 1000, 10):
            wall = arcade.Sprite("dirtCenter.png",  TILE_SCALING)
            wall.center_x = 1000
            wall.center_y = x
            self.wall_list.append(wall)

        # Create sprites based on 2D grid
        for row in range(MAZE_HEIGHT):
                for column in range(MAZE_WIDTH):
                    if maze[row][column] == 1:
                        wall = arcade.Sprite(":resources:images/tiles/dirtCenter.png", SPRITE_SCALING)
                        wall.center_x = column * SPRITE_SIZE + SPRITE_SIZE / 2
                        wall.center_y = row * SPRITE_SIZE + SPRITE_SIZE / 2
                        self.wall_list.append(wall)
        #set up bunny
        image_source_1 = "bunny.png"
        self.bunny_sprite = arcade.Sprite(image_source_1, BUNNY_SCALING)
        self.player_list.append(self.bunny_sprite)
        
        #set up turtle character
        image_source_2 = "turtle.png"
        self.turtle_sprite = arcade.Sprite(image_source_2, TURTLE_SCALING)
        self.player_list.append(self.turtle_sprite)
        
        # Ensure bunny or turtle aren't placed on a wall 
        # I had to use this because sometimes they would be placed on the wall in the begginning
        # And then they couldn't move at all
        players_placed = False
        while players_placed == False:
            
            #place bunny
            self.bunny_sprite.center_x = randint(40, 600)
            self.bunny_sprite.center_y = randint(60, 600)

            #place turtle
            self.turtle_sprite.center_x = randint(40, 600)
            self.turtle_sprite.center_y = randint(60, 600)

            #Check to see if sprites would be placed in wall
            walls_hit_bunny = arcade.check_for_collision_with_list(self.bunny_sprite, self.wall_list)
            walls_hit_turtle = arcade.check_for_collision_with_list(self.turtle_sprite, self.wall_list)
            if len(walls_hit_bunny) == 0 and len(walls_hit_turtle) == 0:
                players_placed = True
            
    
        
        self.physics_engine_bunny = arcade.PhysicsEngineSimple(self.bunny_sprite, self.wall_list)
        self.physics_engine_turtle = arcade.PhysicsEngineSimple(self.turtle_sprite, self.wall_list)

        """ place coins randomly, and ensure that they aren't placed on walls"""     
        for x in range(128, 1250, 50):
            coin_placed = False
            while coin_placed == False:
                self.coin = arcade.Sprite(":resources:images/items/coinGold.png", COIN_SCALING)
                self.coin.center_x = randint(50, 900)
                self.coin.center_y = randint(50, 750)
                wall_hit_coin = arcade.check_for_collision_with_list(self.coin, self.wall_list)
                if len(wall_hit_coin) == 0:
                    self.coin_list.append(self.coin)
                    coin_placed = True             
   

        

    def on_key_press(self, key, modifiers):
        global start_game, run_game, pause

        """"computes if a key is pressed and if it is, the action assigned to the key is executed"""
        
        #keys for player sprites
        if key == arcade.key.UP:
            self.bunny_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.bunny_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.bunny_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.bunny_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.W:
            self.turtle_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.S: 
            self.turtle_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.A:
            self.turtle_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.D: 
            self.turtle_sprite.change_x = PLAYER_MOVEMENT_SPEED

        #pauses game
        if key == arcade.key.ESCAPE:
            pause = True

        #unpauses game
        if key == arcade.key.SPACE:
            pause = False
            run_game = True
           
    def on_key_release(self, key, modifiers):
        """"computes if a key is released after being pressed and if it is, no new action is executed"""

        #keys for bunny sprite
        if key == arcade.key.UP:
            self.bunny_sprite.change_y = 0
        elif key == arcade.key.DOWN:
            self.bunny_sprite.change_y = 0
        elif key == arcade.key.LEFT:
            self.bunny_sprite.change_x = 0
        elif key == arcade.key.RIGHT:
            self.bunny_sprite.change_x = 0

        #keys for turtle sprite
        if key == arcade.key.W:
            self.turtle_sprite.change_y = 0
        elif key == arcade.key.S:
            self.turtle_sprite.change_y = 0
        elif key == arcade.key.A:
            self.turtle_sprite.change_x = 0
        elif key == arcade.key.D:
            self.turtle_sprite.change_x = 0
        

    def on_draw(self):
        global start_game, run_game, pause, end_game
        #render screen
        arcade.start_render()


        if start_game:  # draws the main screen when the start_game variable is true (only at the beginning)
            draw_main_screen(500, 375)

        if run_game:
            # stops the drawing of the main screen
            start_game = False
           
            #sets background to the right color
            draw_background()

            # Draw sprites
            self.wall_list.draw()
            self.coin_list.draw()
            self.player_list.draw()

             # Draw score on the screen
            score_text_bunny = f"Bunny Score: {self.score_bunny}"
            arcade.draw_text(score_text_bunny, 20, 7, arcade.csscolor.BLACK, 16)
            #self.score_text.draw()
            #arcade.draw_text(score_text)
    
            score_text_turtle = f"Turtle Score: {self.score_turtle}"
            arcade.draw_text(score_text_turtle, 
                         200 ,7,
                         arcade.color.BLACK, 16)

            # Calculate minutes
            minutes = int(self.total_time) // 60

            # Calculate seconds by using a modulus (remainder)
            seconds = int(self.total_time) % 60

            # Figure out our output
            output = f"Time: {minutes:02d}:{seconds:02d}"

            # Output the timer text.
            arcade.draw_text(output, 600, 7, arcade.color.BLACK, 16)

        if self.total_time >= 60:
            run_game = False
            end_game = True
            
        
        if pause:
            pause_screen()

        if end_game:
            if self.score_bunny > self.score_turtle:
                draw_end_screen(500, 375, "Bunny!")
            elif self.score_turtle > self.score_bunny:
                draw_end_screen(500, 375, "Turtle!")
            else:
                draw_end_screen(500, 375, "It's a tie!")
            

   
    def on_update(self, delta_time):
        global run_game, end_game

        """used for movement and game logic, updated 60 times per second """
        
        #Start the game
        if run_game: 
            self.physics_engine_bunny.update()
            self.physics_engine_turtle.update()

            # See if we hit any coins
            coin_hit_list_bunny = arcade.check_for_collision_with_list(self.bunny_sprite,
                                                             self.coin_list)

            coin_hit_list_turtle = arcade.check_for_collision_with_list(self.turtle_sprite,
                                                             self.coin_list)

            # Loop through each coin hit by the bunny and remove it
            for coin in coin_hit_list_bunny:
            # Remove the coin
                coin.remove_from_sprite_lists()
            # Play a sound
                arcade.play_sound(self.collect_coin_sound_bunny)
            # Add one to the score
                self.score_bunny += 1
            
            #Loop through each coin hit by the turtle and remove it
            for coin in coin_hit_list_turtle:
                # Remove the coin
                coin.remove_from_sprite_lists()
                # Play a sound
                arcade.play_sound(self.collect_coin_sound_turtle)
                # Add one to the score
                self.score_turtle += 1
            
            self.total_time += delta_time

def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()

# calls the main function to get the program started
if __name__ == "__main__":
    main()