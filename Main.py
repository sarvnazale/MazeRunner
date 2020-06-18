import arcade
import timeit
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
def _create_grid_with_cells(width, height):
    """ Create a grid with empty cells on odd row/column combinations. """
    grid = []
    for row in range(height):
        grid.append([])
        for column in range(width):
            if column % 2 == 1 and row % 2 == 1:
                grid[row].append(TILE_EMPTY)
            elif column == 0 or row == 0 or column == width - 1 or row == height - 1:
                grid[row].append(TILE_CRATE)
            else:
                grid[row].append(TILE_CRATE)
    return grid

def make_maze_depth_first(maze_width, maze_height):
    maze = _create_grid_with_cells(maze_width, maze_height)

    w = (len(maze[0]) - 1) // 2
    h = (len(maze) - 1) // 2
    vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]

    def walk(x: int, y: int):
        vis[y][x] = 1

        d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
        random.shuffle(d)
        for (xx, yy) in d:
            if vis[yy][xx]:
                continue
            if xx == x:
                maze[max(y, yy) * 2][x * 2 + 1] = TILE_EMPTY
            if yy == y:
                maze[y * 2 + 1][max(x, xx) * 2] = TILE_EMPTY

            walk(xx, yy)

    walk(random.randrange(w), random.randrange(h))

    return maze


def draw_main_screen(x: int, y: int):
    # sets a new background, draws title text
    scale = 1
    texture = arcade.load_texture("mainscreen.png")
    arcade.draw_texture_rectangle(x, y, scale * texture.width,
                                  scale * texture.height, texture, 0)


def draw_background():
    arcade.set_background_color(arcade.csscolor.LIGHT_GOLDENROD_YELLOW)

def draw_end_screen(x: int, y: int):
    scale = 1.1
    #sets a new background, draws end game text
    texture = arcade.load_texture("endscreen.png")
    arcade.draw_texture_rectangle(x, y, scale * texture.width,
                                  scale * texture.height, texture, 0)

    arcade.draw_text("GAME OVER!", 270, 500, arcade.color.WHITE, 65)

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
        
        self.coin = None
        
        #physics engine
        self.physics_engine_bunny = None
        self.physics_engine_turtle = None

        # Keep track of the score
        self.score_bunny = 0
        self.score_turtle = 0
        

        # Load sounds
        self.collect_coin_sound_bunny = arcade.load_sound("coin1.wav")
        self.collect_coin_sound_turtle = arcade.load_sound("coin5.wav")
        

    def setup(self):
        #used to set up the game and restart when the game is over
        
        # Keep track of the score
        self.score_bunny = 0
        self.score_turtle = 0


        #creating the sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True) #spatial_hash is used because 
        self.coin_list = arcade.SpriteList(use_spatial_hash=True) #the wall and coins won't move
        self.coin = arcade.SpriteList()


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
        maze = make_maze_depth_first(MAZE_WIDTH, MAZE_HEIGHT)
        
        # Create the divider
        for x in range(0, 1000, 10):
            wall = arcade.Sprite("dirtCenter.png",  TILE_SCALING)
            wall.center_x = x
            wall.center_y = 400
            self.wall_list.append(wall)

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
        while not players_placed:
            
            #place bunny
            self.bunny_sprite.center_x = randint(40, 50)
            self.bunny_sprite.center_y = randint(60, 70)

            #place turtle
            self.turtle_sprite.center_x = randint(40, 50)
            self.turtle_sprite.center_y = randint(680, 700)

            #Check to see if sprites would be placed in wall
            walls_hit_bunny = arcade.check_for_collision_with_list(self.bunny_sprite, self.wall_list)
            walls_hit_turtle = arcade.check_for_collision_with_list(self.turtle_sprite, self.wall_list)
            if len(walls_hit_bunny) == 0 and len(walls_hit_turtle) == 0:
                players_placed = True
            
    
        
        self.physics_engine_bunny = arcade.PhysicsEngineSimple(self.bunny_sprite, self.wall_list)
        self.physics_engine_turtle = arcade.PhysicsEngineSimple(self.turtle_sprite, self.wall_list)


        """  the following two loops had to be separated so that I could 
        have an equal number of coins for each player """
        #set up coins randomly for bunny and make sure they aren't on a wall
        for x in range(128, 1250, 100):
            coin = arcade.Sprite(":resources:images/items/coinGold.png", COIN_SCALING)
            coin.center_x = x
            coin.center_y = randint(50, 300)
            self.coin_list.append(coin) 
                       
        for x in range(128, 1250, 100):
            coin = arcade.Sprite(":resources:images/items/coinGold.png", COIN_SCALING)
            coin.center_x = x
            coin.center_y = randint(500, 700)
            self.coin_list.append(coin) 

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
        global start_game, run_game, pause
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
            arcade.draw_text(score_text_bunny, 20, 7, arcade.csscolor.WHITE, 16)
            #self.score_text.draw()
            #arcade.draw_text(score_text)
    
            score_text_turtle = f"Turtle Score: {self.score_turtle}"
            arcade.draw_text(score_text_turtle, 
                         20,
                         HEIGHT - 420,
                         arcade.color.WHITE, 16)
        if pause:
            pause_screen()

   
    def on_update(self, delta_time):
        global run_game 

        """used for movement and game logic, updated 60 times per second """
        
        start_time = timeit.default_timer()
        
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

            if len(self.coin_list) == 0:
                run_game = False
              
            



def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()

# calls the main function to get the program started
if __name__ == "__main__":
    main()