try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
from random import shuffle, choice, random, randrange as r
from math import ceil


# GLOBALS
CANVAS_SIZE = 900, 600
SCORE_HEIGHT = 20
APPNAME = "Simplegui TRON Light Cycle"

game = None
speed = 2.
pause = False


class Motorbike:
    
    CPU, PLAYER = 1, 2  # rider type
    UP, LEFT, DOWN, RIGHT = (0,-1), (-1,0), (0,1), (1,0)  # directions
    DIRECTIONS = ( UP, LEFT, DOWN, RIGHT )  # directions tuple for choice
    
    def __init__( self, position, rider=PLAYER, speed=4, color="red" ):
        self.__rider = rider
        self.__speed = speed
        self.__color = color
        self.__position = position
        self.__old_position = position
        self.__direction = Motorbike.LEFT if self.__rider is Motorbike.CPU else Motorbike.RIGHT
        self.__keys = None
        if self.__rider == Motorbike.PLAYER:
            self.__keys = { "up": "up", "down": "down", "left": "left", "right": "right" }
        
    def get_rider( self ):
        return self.__rider
    
    def get_speed( self ):
        return self.__speed

    def get_color( self ):
        return self.__color
    
    def set_color( self, color ):
        self.__color = color
    
    def get_position( self ):
        return self.__position

    def set_position( self, position ):
        self.__position = position

    def get_old_position( self ):
        return self.__old_position

    def set_old_position( self, old_position ):
        self.__old_position = old_position
        
    def get_direction( self ):
        return self.__direction
    
    def set_direction( self, direction ):
        self.__direction = direction
        
    def get_keymap( self ):
        return self.__keys
    
    def set_keymap( self, keymap ):
        self.__keys = keymap
        

class Game:
    
    def __init__( self, grid_size, players=1, enemies=1, speed=1. ):
        self.__enemies = [ Motorbike( 
                             ( grid_size[0] * 0.75, grid_size[1] / ( enemies + 1 ) * ( i + 1 ) ),
                             Motorbike.CPU, speed=speed, color="red" )
                           for i in range( enemies ) ]
        self.__players = [ Motorbike(
                             ( grid_size[0] * 0.25, grid_size[1] / ( players + 1 ) * ( 1 + i ) ),
                             Motorbike.PLAYER, speed=speed, color="cyan" )
                           for i in range( players ) ]
        if players == 2:
            self.__players[1].set_keymap( { "up": "w", "down": "s", "left": "a", "right": "d" } )
            self.__players[1].set_color( "lime" )
        self.__matrix = [ [True] * grid_size[0] ]
        for _ in range( grid_size[1] - 2 ):
            self.__matrix += [ [True] + [False] * ( grid_size[0] - 2 ) + [True] ]
        self.__matrix += [ [True] * grid_size[0] ]
        self.__time = 0

    def get_time( self ):
        return self.__time
        
    def get_enemies( self ):
        return self.__enemies
    
    def get_players( self ):
        return self.__players
    
    def is_game_over( self ):
        return len( self.__players ) == 0 or \
            len( self.__players ) == 1 and len( self.__enemies ) == 0
        
    def next_tick( self ):
        
        def check_collision( direction ):
            # check for near walls
            if direction is Motorbike.UP:
                for row in range( int( new_y - speed * 2 ), new_y ):
                    if self.__matrix[row][new_x]:
                        return True
            elif direction is Motorbike.DOWN:
                for row in range( new_y, int( ceil( new_y + speed * 2 ) + 1 ) ):
                    if self.__matrix[row][new_x]:
                        return True
            elif direction is Motorbike.LEFT:
                for col in range( int( new_x - speed * 2 ), new_x ):
                    if self.__matrix[new_y][col]:
                        return True
            elif direction is Motorbike.RIGHT:
                for col in range( new_x, int( ceil( new_x + speed * 2 ) + 1 ) ):
                    if self.__matrix[new_y][col]:
                        return True
                    
            return False                

        for motorbike in self.__enemies + self.__players:
            # move motorbike
            pos = motorbike.get_position()
            direction = motorbike.get_direction()
            new_pos = ( pos[0] + motorbike.get_speed() * direction[0], 
                        pos[1] + motorbike.get_speed() * direction[1] )
            motorbike.set_position( new_pos )
            motorbike.set_old_position( pos )
            
            # check crashes and set trail
            x = int( pos[0] )
            y = int( pos[1] )
            new_x = int( new_pos[0] )
            new_y = int( new_pos[1] )
            crash = False
            
            if ( x, y ) != ( new_x, new_y ):  # set trail 
                if direction is Motorbike.UP:
                    for row in range( y, new_y, -1 ):
                        if self.__matrix[row][new_x]:  # crashes
                            crash = True
                            break
                        else:
                            self.__matrix[row][new_x] = True
                elif direction is Motorbike.DOWN:
                    for row in range( y, new_y ):
                        if self.__matrix[row][new_x]:  # crashes
                            crash = True
                            break
                        else:
                            self.__matrix[row][new_x] = True
                elif direction is Motorbike.LEFT:
                    for col in range( x, new_x, -1 ):
                        if self.__matrix[new_y][col]:  # crashes
                            crash = True
                            break
                        else:
                            self.__matrix[new_y][col] = True
                elif direction is Motorbike.RIGHT:
                    for col in range( x, new_x ):
                        if self.__matrix[new_y][col]:  # crashes
                            crash = True
                            break
                        else:
                            self.__matrix[new_y][col] = True
                            
                # eliminate motorbike
                if crash:
                    if motorbike in self.__enemies:
                        self.__enemies.remove( motorbike )
                    else:
                        self.__players.remove( motorbike )
                        
                # IA
                elif motorbike.get_rider() is Motorbike.CPU:
                    # sometimes change direction randomly
                    if random() < 0.001:
                        if direction in ( Motorbike.UP, Motorbike.DOWN ):
                            motorbike.set_direction(
                                choice( ( Motorbike.LEFT, Motorbike.RIGHT ) ) )
                        else:
                            motorbike.set_direction(
                                choice( ( Motorbike.UP, Motorbike.DOWN ) ) )
                        direction = motorbike.get_direction()
                    # sometimes change direction towards a players
                    if random() < 0.01 and game.get_players():
                        p_pos = choice( game.get_players() ).get_position()
                        if random() < 0.5:
                            motorbike.set_direction( Motorbike.LEFT ) \
                            if p_pos[0] < pos[0] \
                            else motorbike.set_direction( Motorbike.RIGHT ) 
                        else:
                            motorbike.set_direction( Motorbike.UP ) \
                            if p_pos[1] < pos[1] \
                            else motorbike.set_direction( Motorbike.DOWN ) 
                        direction = motorbike.get_direction()
                    # detect collision    
                    if check_collision( direction ):
                        if direction in ( Motorbike.UP, Motorbike.DOWN ):
                            choices = [ Motorbike.LEFT, Motorbike.RIGHT ]
                        elif direction in ( Motorbike.RIGHT, Motorbike.LEFT ):
                            choices = [ Motorbike.UP, Motorbike.DOWN ]
                        # select alternative direction
                        shuffle( choices )
                        for direction in choices:
                            motorbike.set_direction( direction )
                            if not check_collision( direction ):
                                break
        
        # increase time
        self.__time += 1
        
        
    def get_enemies( self ):
        return self.__enemies
    
    def get_players( self ):
        return self.__players
    

def new_game( players, enemies ):
    global game
    game = Game( ( CANVAS_SIZE[0], CANVAS_SIZE[1] - 20 ), players, enemies, speed )

    
def key_handler( key ):
    global pause
    if key == simplegui.KEY_MAP["p"]:
        pause = not pause
    else:
        pause = False
    
    for motorbike in game.get_players():
       if key == simplegui.KEY_MAP[ motorbike.get_keymap()["up"] ] \
          and motorbike.get_direction() != Motorbike.DOWN:
            motorbike.set_direction( Motorbike.UP )
       elif key == simplegui.KEY_MAP[ motorbike.get_keymap()["down"] ] \
          and motorbike.get_direction() != Motorbike.UP:
            motorbike.set_direction( Motorbike.DOWN )
       elif key == simplegui.KEY_MAP[ motorbike.get_keymap()["left"] ] \
          and motorbike.get_direction() != Motorbike.RIGHT:
            motorbike.set_direction( Motorbike.LEFT )
       elif key == simplegui.KEY_MAP[ motorbike.get_keymap()["right"] ] \
          and motorbike.get_direction() != Motorbike.LEFT:
            motorbike.set_direction( Motorbike.RIGHT )


def draw( canvas ):

    # game not started or paused
    if game is None or pause:
        return

    # draw background on frame 0
    if game.get_time() == 0:
        canvas.draw_polygon( ( ( 0, SCORE_HEIGHT ), 
                               ( CANVAS_SIZE[0], SCORE_HEIGHT ),
                               ( CANVAS_SIZE[0], CANVAS_SIZE[1] ),
                               ( 0, CANVAS_SIZE[1] ) ), 
                             5, "#a33", "#1d3442" )

        for i in range( 0, CANVAS_SIZE[0], 40 ):
            canvas.draw_line( ( i, SCORE_HEIGHT ), ( i, CANVAS_SIZE[1] ), 1, "#d3d1dc" )
        for i in range( SCORE_HEIGHT, CANVAS_SIZE[1], 40 ):
            canvas.draw_line( ( 0, i ), ( CANVAS_SIZE[0], i ), 1, "#d3d1dc" )        
        
    # draw scoreboard
    canvas.draw_polygon( ( ( 0, 0 ), 
                           ( CANVAS_SIZE[0], 0 ),
                           ( CANVAS_SIZE[0], SCORE_HEIGHT - 1 ),
                           ( 0, SCORE_HEIGHT - 1 ) ), 
                         1, "lime", "green" )
    textwidth = frame.get_canvas_textwidth( APPNAME, 14, "monospace" )
    canvas.draw_text( APPNAME, 
                      ( ( CANVAS_SIZE[0] - textwidth ) / 2, 14 ),
                      16, "black", "monospace" )
    textwidth = frame.get_canvas_textwidth( "Time %.2f" % ( game.get_time() / 60. ), 12 )
    canvas.draw_text( "Time %.2f" % ( game.get_time() / 60. ), 
                      ( CANVAS_SIZE[0] - textwidth - 4, 14 ),
                      12, "yellow" )
    
    pos = 10
    for motorbike in game.get_players() + game.get_enemies():
        canvas.draw_circle( ( pos, 10 ), 7, 1, motorbike.get_color(), motorbike.get_color() )
        pos += 30
    
    # next tick
    if not game.is_game_over():
        game.next_tick()
    else:
        text = "Player wins" if len( game.get_players() ) > 0 else "GAME OVER"
        textwidth = frame.get_canvas_textwidth( text, 50 )
        canvas.draw_text( text, 
                          ( ( CANVAS_SIZE[0] - textwidth ) / 2, 
                            ( CANVAS_SIZE[1] + 50 ) / 2 ), 
                          50, "rgb(%i,%i,%i)" % ( r(256), r(256), r(256) ) )
    
    # draw motorbikes
    for motorbike in game.get_enemies() + game.get_players():
        old_pos = motorbike.get_old_position()
        pos = motorbike.get_position()
        canvas.draw_line( ( old_pos[0], old_pos[1] + SCORE_HEIGHT ), 
                          ( pos[0], pos[1] + SCORE_HEIGHT ),
                          3, motorbike.get_color() )
    
    
def set_speed( new_speed ):
    global speed
    if new_speed > 0.1:
        speed = new_speed
        label_speed.set_text( "<<<<< " + str( int( round( speed * 60 ) ) ) + " pps >>>>>" )

        
# create GUI
frame = simplegui.create_frame( APPNAME, CANVAS_SIZE[0], CANVAS_SIZE[1], 150 )
frame.set_canvas_background( "rgba(0,0,0,0)" )
frame.add_button( "1 enemy game", lambda: new_game( 1, 1 ), 150)
frame.add_button( "2 enemies game", lambda: new_game( 1, 2 ), 150 )
frame.add_button( "3 enemies game", lambda: new_game( 1, 3 ), 150 )
frame.add_button( "4 enemies game", lambda: new_game( 1, 4 ), 150 )
frame.add_button( "5 enemy game", lambda: new_game( 1, 5 ), 150 )
frame.add_button( "6 enemies game", lambda: new_game( 1, 6 ), 150 )
frame.add_button( "7 enemies game", lambda: new_game( 1, 7 ), 150 )
frame.add_button( "8 enemies game", lambda: new_game( 1, 8 ), 150 )
frame.add_label( "" )
frame.add_button( "2 players", lambda: new_game( 2, 0 ), 150 )
frame.add_button( "2 players, 1 enemy", lambda: new_game( 2, 1 ), 150 )
frame.add_button( "2 players, 2 enemies.", lambda: new_game( 2, 2 ), 150 )
frame.add_button( "2 players, 3 enemies", lambda: new_game( 2, 3 ), 150 )
frame.add_button( "2 players, 4 enemies", lambda: new_game( 2, 4 ), 150 )
frame.add_button( "2 players, 5 enemy", lambda: new_game( 2, 5 ), 150 )
frame.add_button( "2 players, 6 enemy", lambda: new_game( 2, 6 ), 150 )
frame.add_button( "2 players, 7 enemy", lambda: new_game( 2, 7 ), 150 )
frame.add_button( "2 players, 8 enemy", lambda: new_game( 2, 8 ), 150 )
frame.add_label( "" )
frame.add_label( "" )
frame.add_label( "=================" )
frame.add_button( "+Speed", lambda: set_speed( speed + 1. / 6 ), 150 )
label_speed = frame.add_label( "" )
set_speed( speed )
frame.add_button( "-Speed", lambda: set_speed( speed - 1. / 6 ), 150 )
frame.add_label( "=================" )

# define handlers
frame.set_draw_handler( draw )
frame.set_keydown_handler( key_handler )

# start GUI
frame.start()
