import os
import pygame
from pygame.locals import *
from pygame.compat import geterror
import itertools
import math
import copy
import winsound
import time
import threading

if not pygame.font:
    print('Warning, fonts disabled')
if not pygame.mixer:
    print('Warning, sound disabled')


main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir,'data')



#High level notes.

#I do a lot of fucking around with the following sort of stuff
# find thing in list
# list[list.index(thing)].attribute = value
# Look into using enumerate iterator instead of not doing that to keep
# track of position and eliminate all that indexing garbage.
#Cause, what is this, MATLAB?

#I make a big deal out of keeping track of 'clicked' and
#'may_be_clicked' attributes.  Possibly I can just use an
#iterator here too?  Just yield the next guy and only look at clicks of
#that?  I think this removes a lot of my
#list_to_look_at = [thing for thing in biggerlist if thing.look_at_me]
#Especially with the fact taht generators allow you to sort of move them around
#with __send__() 

#itertools.tee returns copies of iterators that
#can be gone through independently

#functools.partial returns a new function that is a function with
#some arguments filled in


#resource functions
#no these aren't totally copied
#shut up.  They look useful

def load_image(name, colorkey = None):
    fullname = os.path.join(data_dir,name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print("Can't load image ", fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey,RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print ('Cannot load sound: %s' % fullname)
        raise SystemExit(str(geterror()))
    return sound

#playing functions

def play_accented_beat(bps):
    winsound.Beep(Constants.DOWN_FREQ,int(Constants.DURATION * 1000))
    time.sleep(bps - Constants.DURATION)

def play_unaccented_beat(bps):
    winsound.Beep(Constants.OFF_FREQ,int(Constants.DURATION * 1000))
    time.sleep(bps - Constants.DURATION)

def combine_accent_and_beat(accent_patterns,beat_squares_list):
    retooled_beat_list = [convert_color_to_number(x.color) for x in beat_squares_list]
    retooled_accent_list = [change_accent_pattern_to_numbers(x.pattern) for x in accent_patterns]

    beat_list = []
    BPM_list = []
    for x in retooled_beat_list:
        if x is not None:
            beat_list.append(retooled_accent_list[x])
            BPM_list.append(accent_patterns[x].BPM)
        else:
            beat_list.append(Constants.NOT_USED)
            BPM_list.append(Constants.NOT_USED)

    

    
    return beat_list,BPM_list
        
        
    
def play(beat_list,BPM_list):
##    arg[0] = beat_list
##    arg[1] = BPM_list
    
    for ii,group in enumerate(beat_list):
        if group != 1.5:
            for beat in group:
                if beat:
                    play_accented_beat(BPM_list[ii])
                elif not beat:
                    play_unaccented_beat(BPM_list[ii])
                if Constants.STOP_FLAG:
                    return
                
        
        
    
    
    


    

#other functions
def convert_color_to_number(color):
    if color == Constants.BG_COLOR:
        return None
    else:
        return Constants.COLORS.index(color)

def change_accent_pattern_to_numbers(alist):

    temp = []
    for x in alist:
        if x.color == Constants.BLACK:
            temp.append(0)
        elif x.color is not Constants.BG_COLOR:
            temp.append(1)
    return temp


def get_numeric_input():
    #only takes 4 digits
    #because God decreed 4 digits to be the correct amount
    #also because thats all that will fit, graphically
    #and also because can't go over ~400 BPM any way (**)
    #but mostly because 4 is a pretty sweet number
        
    grabbed = []
    while len(grabbed) < 4:
        for event in pygame.event.get():
            if event.type == QUIT:
                return Constants.QUIT
            if event.type == MOUSEBUTTONDOWN:
                return Constants.NEW_CLICK
            if event.type is KEYDOWN:
                if event.key is K_RETURN:
                    return grabbed
                elif event.key in range(48,58):
                    grabbed.append(pygame.key.name(event.key))
                elif event.key is K_BACKSPACE:
                    if grabbed:
                        grabbed.pop()

        
        
    return grabbed

def show_awaiting_input(button,input_list,background):
    
    coords = convert_input_button_list_to_human_terms(input_list,button)
    spot = Rect(590,175,396,198)

    pygame.draw.rect(background,Constants.BG_COLOR,spot)
    pygame.display.update(spot)

    font = pygame.font.Font(None,30)
    if coords[1] == 1:
        #left button
        string = 'Awaiting input from BPM Button, Row ' + str(coords[0])
    elif coords[1] == 2:
        string = 'Awaiting input from Number of Beats Button, Row ' + str(coords[0])
    text = font.render(string,1,Constants.BLACK,Constants.BG_COLOR)
    background.blit(text,spot)
    pygame.display.update(spot)
    
    

    
    

def show_text_bpm_pane(input_text,clicked_button_rect,background):
    font = pygame.font.Font(None,30)
    
    text_input_blanker = pygame.Surface((50,20))
    text_input_blanker.fill(Constants.BG_COLOR)
    button_pos = clicked_button_rect.topleft
    text_pos = (button_pos[0] + 36, button_pos[1] + 10)
    background.blit(text_input_blanker,text_pos)
    text = font.render(''.join(input_text),1,Constants.BLACK,
                                 Constants.BG_COLOR)
    background.blit(text,text_pos)

    rect_to_update = Rect(text_pos,text_input_blanker.get_size())
    return rect_to_update



def activate_next_button(button_list,sub_list,button):
    #takes in a list of lists of buttons, and sets the next one in sequence
    #to be clickable.  If current button is last button, does nothing.  Returns
    #nothing in any case.

    #NO LONGER USED.  CHANGED IMPLEMENTATION OF BUTTON LIST
    
    len1 = len(button_list)
    sub_list_spot = button_list.index(sub_list)
    button_spot = sub_list.index(button)
    if sub_list_spot == (len1 - 1):
        return
    elif button_spot == 0:
        sub_list[1].may_be_clicked = True
    elif button_spot == 1:
        button_list[sub_list_spot+1][0].may_be_clicked = True
    return

def convert_input_button_list_to_human_terms(input_list,button):
    #Ideally, I want a matrix of buttons.  But I'm going to have a flat list
    #This just converts indices from list to matrix (**INDEXED BY ONE, SO
    #THAT FUCKING PEOPLE CAN READ IT, NOT BY ZERO LIKE THIS FUCKING
    #STUPID ASS WORLD THINKS IS GOOD**), in order to use fewer
    #loops when checking through the buttons.  Returns a list, [row,column]
    #Returns None if 'button' not in input list

    try:
        spot = input_list.index(button)

        column =  (spot % 2) + 1
        row = math.floor(spot/2) + 1
        
    except ValueError:
        return None

    return [row,column]

def convert_accent_square_to_human(accent_list,selected):
    #same as above, but for the accent squares list.  Yes these 3 functions should
    #all be one function with and inputable grid size or something
    #Nobody asked your opinion
    try:
        spot = accent_list.index(selected)

        row = 1 + (spot % 4)
        column = 1 + math.floor(spot/4)
    except ValueError:
        return None

    return [row,column]

def convert_beat_square_to_human(beat_list,selected):
    #see above
    try:
        spot = beat_list.index(selected)

        column = 1 + (spot % 12)
        row = 1 + math.floor(spot/12)
    except ValueError:
        return None
    #its backwards because of the way the list is initially filled
    #my for loops go down and then across because Pluto was in the 3rd house

    return [column,row]
def activate_appropriate_accent_boxes(pattern_obj):
    BPC = pattern_obj.BPC
    for x in pattern_obj.pattern:
        x.color = Constants.BG_COLOR

    #I have to make this transformation because the accent squares list
    #indices are transposed from what I meant them to be
    #because all programming languages should be MATLAB and
    #transpositions should be trivial
    

    true_list = [x + y*4 for x in range(0,4) for y in range(0,12)]
    
    
    

    for x in range(0,BPC):
        pattern_obj.pattern[true_list[x]].color = Constants.BLACK
        pattern_obj.pattern[true_list[x]].may_be_clicked = True

    return
        


def flip_accent_box_color(box,indicator,background):
    if box.color == Constants.BLACK:
        pygame.draw.rect(background,indicator.color,box.inflate(-3,-7).move(1,1))
        box.color = indicator.color
    elif box.color == indicator.color:
        pygame.draw.rect(background,Constants.BLACK,box.inflate(-3,-7).move(1,1))
        box.color = Constants.BLACK
    return box

def flip_beat_box_color(box,indicator,background):
    if box.color is not indicator.color:
        pygame.draw.rect(background,indicator.color,box.inflate(-7,-3).move(1,1))
        box.color = indicator.color
    elif box.color == indicator.color:
        pygame.draw.rect(background,Constants.BG_COLOR,box.inflate(-7,-3).move(1,1))
        box.color = Constants.BG_COLOR

    return box

def update_previous_beat_boxes(box,beat_squares_list,background):

    
    
    box_spot = beat_squares_list.index(box)
    active_color = box.color

    if box_spot == 0:
        return None
    
    potential_list = beat_squares_list[0:box_spot]
    potential_list = potential_list[::-1] #reverses the list

    for i,box in enumerate(potential_list):
        if box.color is not Constants.BG_COLOR:
            spot = i
            break
        else:
            spot = len(potential_list) - 1

    if spot==0:
        return None

    

    for x in potential_list[0:spot]:
##        x.color = potential_list[spot].color
##        pygame.draw.rect(background,potential_list[spot].color,x.inflate(-7,-3).move(1,1))
        x.color = active_color
        pygame.draw.rect(background,active_color,x.inflate(-7,-3).move(1,1))

    return potential_list[0:spot]
            
        

    
        

def blank_accent_zone(background,accent_list):
    for x in accent_list:
        pygame.draw.rect(background,Constants.BG_COLOR,x.inflate(-3,-7).move(1,1))
    return

def draw_accent_zone_from_load(background,accent_list):

    for x in accent_list:
        pygame.draw.rect(background,x.color,x.inflate(-3,-7).move(1,1))

    return




                         
             
def deepcopy(x):  
    new = MyRect(x.left,x.top,x.width,x.height)
    new.color = x.color
    new.clicked = x.clicked
    new.may_be_clicked = x.may_be_clicked
    return new

def validate_spb(spb):
    if spb - Constants.DURATION < 0:
        raise BPMError('BPM too high',spb)
            
##Classes

class Button(pygame.sprite.Sprite):
    def __init__(self,name,pos = (0,0), colorkey = None):
        pygame.sprite.Sprite.__init__(self)
        self.image,self.rect = load_image(name, colorkey)
        self.rect.topleft = pos
        self.may_be_clicked = False


class Metronome():
    def __init__(self):
        self.playing = False

class Drawing():

    def make_rect_outline(background,topleft,height,width,line_width):
        one = topleft
        two = (topleft[0] + width,topleft[1])
        three = (two[0],two[1] + height)
        four = (topleft[0],topleft[1] + height)
        pygame.draw.lines(background,
                          Constants.BLACK,
                          True,
                          [one,two,three,four],
                          line_width)
class MyRect(pygame.Rect):
    #I just need a couple of more pieces of info on my rectangles

    def __init__(self,left,top,width,height):
        pygame.Rect.__init__(self,left,top,width,height)
        self.may_be_clicked = False
        self.clicked = False
        self.color = Constants.BG_COLOR


    
    
        
class Constants():
    QUIT = 1 #when the user wants to quite while in an input function/loop
    NEW_CLICK = 2 #when user clicks a new button to abort input
    NOT_USED = 1.5 #GUARANTEED TO NEVER BE A NON NONE SKIPPABLE VALUE
    BPM_ERROR = -1 #If validate_spb() fails.  Need to not take input in this case
    THICK_LINE_WIDTH = 3
    THIN_LINE_WIDTH = 1

    BG_COLOR = (250,250,250)
    BLACK = (0,0,0)
    WHITE = (255,255,255)
    RED = (255,0,0)
    GREEN = (0,255,0)
    BLUE = (0,0,255)
    YELLOW = (255,255,0)
    PURPLE = (128,0,128)
    ORANGE = (255,165,0)
    PINK = (255,110,180)
    
    #A list of colors, just in case I need that
    #I totally need that!  Gj, me
    
    COLORS = [RED,GREEN,BLUE,YELLOW,PURPLE,ORANGE,PINK,BLACK,WHITE]
    NUM_COLORS = len(COLORS)

    DURATION = .1
    DOWN_FREQ = int(660)
    OFF_FREQ = int(DOWN_FREQ / (3/2))
    

    STOP_FLAG = True
    

    
##
class AccentPattern():
    def __init__(self,pattern,color):
        self.pattern = [deepcopy(x) for x in pattern]
        self.color = color
        self.BPM = 0
        self.BPC = 0

    def save(self,pattern):
        self.pattern = [deepcopy(x) for x in pattern]

    def load(self):
        return self.pattern

         
class BPMError(Exception):
    '''Exception for BPM too high'''
    pass
        


    
##El Maino
def main():
    # setup and create the window
    pygame.init()
    screen = pygame.display.set_mode((1000,580))
    pygame.display.set_caption("Danny's Sexy-Ass Metronome, For Justin's Sexy Ass")

    #create background surface
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(Constants.BG_COLOR)
    
    #set up bpm/bpc pane

    #there is room for 7 double rows.  The there is a thick line every
    #80 pixels (6 of them), and a thin one every 80 (7 of them), offset by one.
    #Due to main border, start from y = 3
    input_button_list = []
    bpm_pane_static_text = pygame.font.Font(None,30).render('Color',
                                                            1,
                                                            Constants.BLACK,
                                                            Constants.BG_COLOR)
   

    
    thickstart = 3
    thinstart = 43

    for ii in range(0,7):
        #should I convert all these to list comprehensions
        #or the variety of specially built sexy python functions that operate on lists and such?
        #yes.
        #Will I?  Maybe
        

        #set up the BPM pane grid
        pygame.draw.line(background,Constants.BLACK,
                         (0,thinstart + (ii * 80)),
                         (200,thinstart + (ii * 80)),
                          Constants.THIN_LINE_WIDTH)
        pygame.draw.line(background,Constants.BLACK,
                         (0,thickstart + ((ii+1) * 80)),
                         (200,thickstart + ((ii+1) * 80)),
                         Constants.THICK_LINE_WIDTH)

        #instantiate the BPM/BPC buttons
        buttons_to_add = [Button('right-arrow.png',(16,7 + (ii * 80))),
                          Button('right-arrow.png',(107,7 + (ii * 80)))]
        input_button_list.append(buttons_to_add)
        #Draw the word 'Color'
        background.blit(bpm_pane_static_text,(16,thinstart + 10 + (ii * 80)))

    #Draw the (initially 'invisible' clickable color boxes
    color_box_list = [MyRect(107,49 + (ii*80),30,30) for ii in range(0,7)]
    [pygame.draw.rect(background,Constants.BG_COLOR,rect) for rect in color_box_list]

        
       
    #finish up the border of the BPM pane
    pygame.draw.lines(background,Constants.BLACK,False,
                      [(0,0),(200,0),(200,562)],Constants.THICK_LINE_WIDTH)
    pygame.draw.line(background,Constants.BLACK,(0,562),(0,0),
                     Constants.THICK_LINE_WIDTH)


    #You can only enter text into a button if you have used the ones before it:
    #The BPC button in each row can only be clicked if the BPM one is,
    #and a row can only be used if the one above it has been
    #So set the first one up to be clickable

    input_button_list[0][0].may_be_clicked = True
    #Collapse the nested list into one list, for ease of looping later
    input_button_list = ([x for x in
                          itertools.chain.from_iterable(input_button_list)])

    

    #Set up Accent Zone
    #There is a grid of 48 rectangles.  When the BPC is specified, the correct
    #amount of them will turn black or something, and then clicking on them will
    #turn them whatever color that BPC is assigned, signifying an accent
    #There is also a rectangle that turns the active color

    
    #Draw the text 'Accent Zone
    accent_zone_static_text = pygame.font.Font(None,
                                               30).render('Accent Zone',
                                                          1,
                                                          Constants.BLACK,
                                                          Constants.BG_COLOR)
    text_rect = accent_zone_static_text.get_rect()
    background.blit(accent_zone_static_text,(203,3))

    #Draw thick borders
    Drawing.make_rect_outline(background,
                              (200,0),
                              text_rect.height+5,
                              text_rect.width+5,
                              Constants.THICK_LINE_WIDTH)
    Drawing.make_rect_outline(background,
                              (200,0),
                              163,
                              361,
                              Constants.THICK_LINE_WIDTH)
    accent_squares_list = []
    #draw the grid
    for ii in range(0,12):
        for jj in range(0,4):
            Drawing.make_rect_outline(background,
                                      (200 + ii * 30,45 + jj * 30),
                                      30,
                                      30,
                                      Constants.THIN_LINE_WIDTH)
            accent_squares_list.append(MyRect(200 + ii*30,
                                                   45 + jj*30,
                                                   30,
                                                   30))
    
    #indicator zone
    accent_zone_indicator = MyRect(350,3,150,40)
    pygame.draw.rect(background,Constants.BG_COLOR,accent_zone_indicator)

    #instantiate pattern objects
    accent_patterns = [AccentPattern(accent_squares_list,x) for x in Constants.COLORS]
    
            
            
    
    
    
    #Set up Beat Order Zone
    #Similar deal to the Accent Zone.  144 (12x12) boxes.  Clicking on them
    #changes them to the color of whatever beat is selected.  Blank spaces
    #in between beats repeat the one preceding the blank.  Blank spots at the
    #end of the pattern are ignored

    #Draw the text 'Beat Zone'
    beat_zone_static_text = pygame.font.Font(None,
                                             30).render('Beat Zone',
                                                        1,
                                                        Constants.BLACK,
                                                        Constants.BG_COLOR)
    text_rect = beat_zone_static_text.get_rect()
    background.blit(beat_zone_static_text,(203,170))

    #Draw the borders
    Drawing.make_rect_outline(background,
                              (200,164),
                              text_rect.height + 5,
                              text_rect.width + 5,
                              Constants.THICK_LINE_WIDTH)
    Drawing.make_rect_outline(background,
                              (200,164),
                              399,
                              361,
                              Constants.THICK_LINE_WIDTH)
    beat_squares_list = []
    #Draw the grid
    for jj in range(0,12):
        for ii in range(0,12):
            Drawing.make_rect_outline(background,
                                      (200 + ii * 30,203 + jj * 30),
                                      30,
                                      30,
                                      Constants.THIN_LINE_WIDTH)
            beat_squares_list.append(MyRect(200 + ii*30,
                                                 203 + jj*30,
                                                 30,
                                                 30))
    #Draw the indicator zone
    beat_zone_indicator = MyRect(330,170,150,30)
    pygame.draw.rect(background,Constants.BG_COLOR,beat_zone_indicator)
            
                                  
                              


    #Set up the right Pane

    #Do Not Loop Checkbox
    #Measure Counter
    #Pattern Indicator
    #Interesting and Cool Animation Related to What The Nome is Doing, Maybe
    #(depends on if frame rate can go fast enough, which I think it can not?)
    #Play and Stop Buttons
    play_button = Button('play_button.png',(700,500))
    play_button.may_be_clicked = False
    stop_button = Button('StopButton.png',(800,500))
    stop_button.may_be_clicked = False


    #paste background onto screen, draw all sprites (ie, buttons and the
    #cool animation), and do the initial flip 
    screen.blit(background,(0,0))

    business_card = Button('businesscard.png',pos = (590,175),colorkey = (Constants.WHITE))
    allsprites = pygame.sprite.RenderPlain((input_button_list,
                                            play_button,
                                            stop_button,
                                            business_card))
    allsprites.draw(screen)
    pygame.display.flip()

    
    

    #the game loop
    go = True
    while go:
        dirty_rects = []
        for event in pygame.event.get():
            if event.type == QUIT:
                go = False
                break
            elif event.type == MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                #see what button the user clicked
                
                #first check input buttons
                #only need to check clickable ones
                clickable_list = ([x for x in input_button_list
                                   if x.may_be_clicked])
                for button in clickable_list:
                    if button.rect.collidepoint(mouse):
                        
                        #Stop the metronome from playing, if it is
                        Constants.STOP_FLAG = True
                        
                        #make the input zone gray or something, to show
                        #that it is awaiting input
                        ##MISSING
                        #This may literally be impossible.  That's the third failure.
                        
                        coord = convert_input_button_list_to_human_terms(input_button_list,
                                                                         button)
                        #get keyboard input
                        input_text = get_numeric_input()


                        
                        

                        
                        if input_text == Constants.QUIT:
                            go = False
                            break
                        if input_text == Constants.NEW_CLICK:
                            mouse = pygame.mouse.get_pos()
                            continue

                        if coord[1] == 1:
                            bpm = int(''.join(input_text))
                            spb = 60/bpm
                            try:
                                validate_spb(spb)
                            except BPMError:
                                break
                        elif coord[1] == 2:
                            bpc = int(''.join(input_text))
                            if bpc > 48:
                                break
                        
                        #activate next button
                        try:
                            input_button_list[input_button_list.index(button)+1].may_be_clicked = True
                        except IndexError:
                            pass
                        

                        #Assign a color to this combination, make colorbox clickable,
                        #add colorbox rect to dirty_rects
                        
                        # store the BPM or BPC to the relevant accent pattern object,
                        #change colors of appropriate rectangles, and activate appropriate ones
                        #do not draw.  rectangles are drawn only on colorbox click
                        
                        
                        if coord[1] == 1:
                            text = ''.join(input_text)
                            accent_patterns[coord[0] - 1].BPM = 60 / int(text)
                            
                        if coord[1] == 2:
                            text = ''.join(input_text)
                            
                            accent_patterns[coord[0] - 1].BPC = int(text)
                            activate_appropriate_accent_boxes(accent_patterns[coord[0] - 1])
                            
                            row = coord[0] - 1 #I index by 1 in human readable terms
                            pygame.draw.rect(background,
                                             Constants.COLORS[row],
                                             color_box_list[row])
                            color_box_list[row].may_be_clicked = True
                            color_box_list[row].color = Constants.COLORS[row]

                            dirty_rects.append(color_box_list[row])
                        


                        #show the text
                        dirty_rects.append(show_text_bpm_pane(input_text,
                                                              button.rect,
                                                              background))


                #end cycling through input pane buttons

                        
                #next check if the BPM pane color square has been clicked
                clickable_squares = [x for x in color_box_list if x.may_be_clicked]
                for square in clickable_squares:
                    if square.collidepoint(mouse):
                        #Here I won't stop the metronome, because I might want to just
                        #verify the patterns playing
                        
                        #save current accent pane pattern to last color clicked
                        try:
                            #check which button was clicked before this one
                            previous_clicked = next(itertools.filterfalse(lambda x: not x.clicked,
                                                                          clickable_squares))
                        except StopIteration:
                            #if there wasn't one
                            previous_clicked = None

                            #if there was a button already clicked, probably some
                            #accent buttons are colored.  Save the whole lot of them
                        if previous_clicked is not None:
                            prev_color = previous_clicked.color
                            accent_pattern = next(x for x in accent_patterns if x.color == prev_color)
                            accent_pattern.save(accent_squares_list)
                            
                        
                        
                        
                        
                        #reload clicked pattern
                        cur_color = square.color
                        accent_pattern = next(x for x in accent_patterns if x.color==cur_color)
                        
                        accent_squares_list = accent_pattern.load()

                        
                        blank_accent_zone(background,accent_squares_list)
                        draw_accent_zone_from_load(background,accent_squares_list)
                        dirty_rects.extend(accent_squares_list)
                        
                        
                        

                        
                       
                        
                        spot = color_box_list.index(square)
                        for x in color_box_list:
                            x.clicked = False
                                              
                        square.clicked = True

                        #show this color in accent zone indicator
                        pygame.draw.rect(background,
                                         Constants.COLORS[spot],
                                         accent_zone_indicator)
                        accent_zone_indicator.color = Constants.COLORS[spot]
                        dirty_rects.append(accent_zone_indicator)

                        


                        #show color in beat zone indicator
                        pygame.draw.rect(background,
                                         Constants.COLORS[spot],
                                         beat_zone_indicator)
                        beat_zone_indicator.color = Constants.COLORS[spot]
                        dirty_rects.append(beat_zone_indicator)



                        
                #end checking if color box was clicked
                        
                        


                #next check the accent zone.
                #Only bother if at least 1 BPM and BPC entered
                # and only check those that are colored in (ie only the ones
                #that are under BPC)    
               
                if (len(clickable_list) > 2
                    and accent_zone_indicator.color is not Constants.BG_COLOR): #meaning at least 2 input buttons clicked
                    active_color_idx = Constants.COLORS.index(accent_zone_indicator.color)
                    accent_squares_list = accent_patterns[active_color_idx].pattern
                    clickable_accent_boxes = [x for x in accent_squares_list if x.may_be_clicked]

                    for box in clickable_accent_boxes: #set up whenever a colorbox is clicked
                        if box.collidepoint(mouse):
                            #stop the metronome from playing
                            Constants.STOP_FLAG = True
                            
                            box.clicked = True
                        #flip its color state between accented/not accented
                        #and add box to dirty_rects
                            dirty_rects.append(flip_accent_box_color(box,
                                                                     accent_zone_indicator,
                                                                     background))
                            
                            

                #next check the beat zone
                #only bother if at least one BPM and BPC entered
                #
                if len(clickable_list) > 2: #meaning at least 2 input buttons clicked
                    for box in beat_squares_list:
                        if box.collidepoint(mouse):
                            #stop the metronome from clicking
                            Constants.STOP_FLAG = True
                            
                            box.clicked = True
                      

                            #toggle its color between active and background
                            #add to dirty rects

                            active_color = beat_zone_indicator.color
                            dirty_rects.append(flip_beat_box_color(box,
                                                                   beat_zone_indicator,
                                                                   background))

                            #change color of everything preceding it to
                            #first previous nonblank square
                            update_list = update_previous_beat_boxes(box,beat_squares_list,background)
                            if update_list is not None:
                                dirty_rects.extend(update_list)


                            play_button.may_be_clicked = True

                            

                            
                            

                #next check the play button
                #only bother if at least 1 BPM, BPC entered and at least 1
                #box in beat pattern clicked
                
                if (play_button.rect.collidepoint(mouse)
                    and play_button.may_be_clicked
                    and len(clickable_list) > 2
                    and accent_zone_indicator.color is not Constants.BG_COLOR):

                    target_args = combine_accent_and_beat(accent_patterns,
                                                      beat_squares_list)

                    Constants.STOP_FLAG = False
                    player = threading.Thread(target = play,args = target_args)
                    player.start()
                    
                    play_button.may_be_clicked = False
                    stop_button.may_be_clicked = True
                    
                if (stop_button.rect.collidepoint(mouse)
                    and stop_button.may_be_clicked
                    and len(clickable_list) > 2):
                    
                    #stop playing metronome
                    Constants.STOP_FLAG = True
                    play_button.may_be_clicked = True
                    stop_button.may_be_clicked = False
                
                    
                    
            #end if mouse button down
            

                        
                            
        
        #end main for loop event checker        
        screen.blit(background,(0,0))
        allsprites.draw(screen)
        pygame.display.update(dirty_rects)
                
    #end While go
    pygame.quit()
                
if __name__=='__main__':
    main()
