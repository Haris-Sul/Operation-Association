# ------------------------  USER SETTINGS ----------------------- 

# these values are safe for users to make reasonable adjustments to for reducing or increasing difficulty
SWITCH_LENGTH = 5 # time in seconds for switching phase
# all these have a default value of 1

# increase this to increase time given for turns
TIME_MULTIPLIER = 1 # recommended range [0.7, 2.5]

# reduce this to make weaker connections be accepted 
REQUIRED_ASSOCIATION_MULTIPLIER = 1.00 # recommended range[0.8, 1.35]

# decrease this to reduce the score loss from penalties, set to 0 for no penalty
PENALTY_MULTIPLIER = 1 # recommended range [0, 1,5]


# --------------------- importing libraries ------------------------

# as import * was not used, the tkinter module using tk.root() instead of just root()
# and customtkinter's methods use ctk.root + classes use ctk.CTk<classname> to differ from tkinter classes
import tkinter as tk
import customtkinter as ctk 
from PIL import ImageTk
import os
import random
import enchant
import spacy
from math import ceil
from nltk.corpus import wordnet

# override default windows theme to the game's theme
ctk.set_appearance_mode("dark")


# --------------------- defining colours -------------------------

black = '#000000'
dark_grey = '#2B2B2B'
grey = '#3D3E3E'
light_grey = '#868686'
white = '#F2F2F2'
purple = '#3F22FF'
green = '#00FF00'
dark_green = '#00B000'
light_blue = '#00FFFF'
blue = '#00AAFF'
dark_blue = '#0000FF'
turqoise = '#00FFBB'
red = '#FF1100'
rose = '#FF666F'
orange = '#FA7A0A'
yellow = '#FFF000'
    
# inheriting tk.Tk makes App a child class of tk.Tk so it can inherits all its methods
class App(tk.Tk):
    def __init__(self):
        # runs the parents constructor to gain access to them
        super().__init__()
        self.title('Operation Association')
        self.nlp = spacy.load('en_core_web_lg', exclude=["parser",'ner'])

        #here self is effectively what would normally be root in a program without classes
         
        self.width = 1280
        self.height = 720 - 23

        # simply: self.geometry("1280x697")
        self.geometry(f"{self.width}x{self.height}") 

        # this disables the menu bar button to toggle fullscreen mode as the game only needs to be fullscreen or minimised
        self.resizable(0,0) 

        if self.winfo_screenwidth() == 1280:
            self.state('zoomed')

        self.name1 = ''
        self.name2 = ''
        
        # define style for the most common button used on all sub pages
        self.standard_btn_style = {
            'font':('Arial', 28,'bold'),
            'fg_color': light_blue,
            'text_color': dark_blue,
            'border_color':light_blue,
            'border_width':2,
            'hover_color':orange,
            'corner_radius':10,
        }        

        # Create the main container
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        
        os.chdir("data") #changes to data directory
        # check if the file created the first time the game is run exists yet
        file_exists = os.path.exists('name.txt')
    
        # go to page to add the users name
        if not file_exists:
            self.current_page = Choose_name_page(self.container, self)
            self.current_page.pack(side="top", fill="both", expand=True)

        else:
            # an instance of the home page is created here
            self.current_page = Home_page(self.container, self)
            self.current_page.pack(side="top", fill="both", expand=True)

    def new_page(self, new_page_class): 
        # Show the selected page and hide the others
        self.current_page.destroy()
        self.current_page = new_page_class(self.container, self)
        self.current_page.pack(side="top", fill="both", expand=True)

        # Call the tkraise method on the instance to bring it to the front
        self.current_page.tkraise() 

    # method to check the text being entered into the name page's entry boxes
    def check_entry(self, new_text):
        if len(new_text) > 10:
            allowed = False
        else:
            allowed = True
            for char in new_text:
                # range of characters with ascii values from a to z or A to Z
                if not ((96 < ord(char) < 123) or (64 < ord(char) < 91)):
                    # check if its not a number as well
                    if char not in '1234567890':
                        allowed = False
                    else:
                        if char == new_text[0]:
                            allowed = False
        return allowed

# page to set the main user's saved name
class Choose_name_page(ctk.CTkFrame):
    def __init__(self, parent, ctrl): 
        
        super().__init__(parent)
        self.ctrl = ctrl

        self.background_img=ImageTk.PhotoImage(file="logopage_img.png")
        bgd_img_label = tk.Label(self, image=self.background_img)
        bgd_img_label.place(x=0,y=0)

        self.name1_label = ctk.CTkLabel(self, text="Please enter the Main user's name here so it can be used later in games.", text_color=light_blue, font=('Arial', 34,'bold'))
        self.name1_label.place(x=ctrl.width/2, y=250, anchor='center')

        self.entry = ctk.CTkEntry(master=self, font=('Arial', 34,'bold'), width=250, text_color=light_blue, border_color=light_blue, corner_radius=0)
        self.entry.place(x=750, y=20, anchor='center')

        # wrapper function as shown in tkinter docs
        validation_wrapper = (self.register(ctrl.check_entry), '%P')
        # set wrapper function to the command parameter
        self.entry.configure(validate ="key", validatecommand=(validation_wrapper))

        self.msg_label = ctk.CTkLabel(self, text="Name can only contain letters and numbers", text_color=green, font=('Arial', 28,'bold'))
        self.msg_label.place(x=ctrl.width/2, y=450, anchor='center')

        self.submit_btn = ctk.CTkButton(self, text="Continue", **ctrl.standard_btn_style, command=self.submit)
        self.submit_btn.place(x=ctrl.width/2,y=550, anchor='center')
    
    # method called when submit name button is pressed to save name and take to home page
    def submit(self):
        # get the text in the entry box
        name = self.entry.get()
        
        if len(name) > 1: #if name is at least 2 characters
            #save to file
            with open('name.txt', 'w+') as f:
                f.write(name)

            # change to home page
            self.ctrl.new_page(Home_page)

        else:
            # change message if they tried to enter too short of a name
            self.msg_label.configure(text_color=rose, text='Name must be at least 2 characters')

# page for the entry of names before starting the main game (2-player mode)
class Main_name_page(ctk.CTkFrame):
    def __init__(self, parent, ctrl): 
        
        super().__init__(parent)
        self.ctrl = ctrl

        self.background_img=ImageTk.PhotoImage(file="logopage_img.png")
        bgd_img_label = tk.Label(self, image=self.background_img)
        bgd_img_label.place(x=0,y=0)

        self.back_btn = ctk.CTkButton(self, text="❮=", **ctrl.standard_btn_style, width=55, height=40, command=lambda: ctrl.new_page(Home_page))
        self.back_btn.place(x=5,y=5, anchor='nw')

        # read the name saved in the file and set it to list's first item 
        with open('name.txt', 'r') as f:
            name = f.read()
            ctrl.name1 = name

        # ------------------- setting up page interface ---------------------

        self.name1_label = ctk.CTkLabel(self, text="Main user's name:", text_color=light_blue, font=('Arial', 34,'bold'))
        self.name1_label.place(x=ctrl.width*.25, y=250, anchor='center')

        self.entry = ctk.CTkEntry(master=self, font=('Arial', 34,'bold'), placeholder_text=ctrl.name1, width=250, text_color=light_blue, border_color=light_blue, corner_radius=0)
        self.entry.place(x=ctrl.width*.25, y=320, anchor='center')

        validation_wrapper = (self.register(ctrl.check_entry), '%P')
        self.entry.configure(validate ="key", validatecommand=(validation_wrapper))

        self.name1_label = ctk.CTkLabel(self, text="Challenger's name:", text_color=light_blue, font=('Arial', 34,'bold'))
        self.name1_label.place(x=ctrl.width*.75, y=250, anchor='center')

        self.entry2 = ctk.CTkEntry(master=self, font=('Arial', 34,'bold'), placeholder_text='Challenger', width=250, text_color=light_blue, border_color=light_blue, corner_radius=0)
        self.entry2.place(x=ctrl.width*.75, y=320, anchor='center')

        validation_wrapper = (self.register(ctrl.check_entry), '%P')
        self.entry2.configure(validate ="key", validatecommand=(validation_wrapper))

        self.msg_label = ctk.CTkLabel(self, text="Name must start with a letter then can contain numbers too", text_color=green, font=('Arial', 28,'bold'))
        self.msg_label.place(x=ctrl.width/2, y=450, anchor='center')

        self.start_btn = ctk.CTkButton(self, text="Continue", **ctrl.standard_btn_style, command=self.start)
        self.start_btn.place(x=ctrl.width/2,y=550, anchor='center')
    
    # method called when button to start game is pressed
    def start(self):
        # get the text in the entry box
        name1 = self.entry.get()
        name2 = self.entry2.get()

        # if the names are blank this means they left the placeholder values as they were
        # or they just cleared the values and clicked start
        # in either case their names can just become the placeholder values
        if name1 == '':
            name1 = self.ctrl.name1
        
        if name2 == '':
            name2 = 'Challenger'

        if len(name1) > 1 and len(name2) > 1: #names must be at least 2 characters
            if name1.lower() != name2.lower(): # names cant be the same
                if name1.lower() != 'challenger': # name challenger is reserved for guest
                    if name2.lower() != self.ctrl.name1.lower(): # guest cant use main users reserved name
                        # save names to App class variables 
                        self.ctrl.name1 = name1
                        self.ctrl.name2 = name2

                        # change to home page
                        self.ctrl.new_page(Game_page)

                    else:
                        self.msg_label.configure(text_color=rose, text="guest cant use main user's reserved name")
                else:
                    self.msg_label.configure(text_color=rose, text="Name 'challenger' is reserved for guest")
            else:
                self.msg_label.configure(text_color=rose, text="Names must be different")
        else:
            self.msg_label.configure(text_color=rose, text='Name must be at least 2 characters')

# page to navigate to the various other pages in the game
class Home_page(tk.Frame):
    # the parent is a container (main frame that contains the other frames) 
    # the controller (ctrl) is the main class (to communicate + access each others attributes/ funcs)

    def __init__(self, parent, ctrl):
        super().__init__(parent)
        self.ctrl = ctrl
        self.configure(background=dark_grey)

        # define style buttons on this page will use
        menu_style = {
            'master': self,
            'font':('Arial', 26,'bold'),
            'fg_color': light_blue,
            'text_color': dark_blue,
            'border_color':purple,
            'border_width':5,
            'hover_color':rose,
            'corner_radius':10,
            'height':47
        }        
        # define image (it is stored in 'data' folder )

        self.background_img=ImageTk.PhotoImage(file="homepage.png")
        bgd_img_label = tk.Label(self, image = self.background_img)
        bgd_img_label.place(x=0,y=0)

        # ------------ navigation menu buttons -------------

        self.button = ctk.CTkButton(text='How To Play', **menu_style, command=lambda: ctrl.new_page(Instructions_page))
        self.button.place(x=385, y=180, anchor=tk.CENTER)

        self.button = ctk.CTkButton(text='Start Game', **menu_style, command=lambda: ctrl.new_page(Main_name_page))
        self.button.place(x=590, y=122, anchor=tk.CENTER)
        

# page for the main game to take place on
class Game_page(ctk.CTkFrame):
    def __init__(self, parent, ctrl): 

        super().__init__(parent)
        self.ctrl = ctrl

        # main space meter/ bars style
        bar_style = {
            'fg_color':purple,
            'progress_color':red,
            'border_color':light_blue,
            'border_width':4,
            'height':40,
            'width':500,
            'corner_radius':14,
        }

        # define style for players timer progress bars- initially player 1's colours
        p1_timer_style = {
            'orientation':'vertical',
            'fg_color':black,
            'progress_color':light_blue,
            'border_color':blue,
            'border_width':4,
            'height':210,
            'width':35,
            'corner_radius':4
        }

        # ----------------------------- main interface setup -----------------------------------

        self.word_height = 40

        self.canvas_frame = ctk.CTkFrame(master=self,width=1140,height=540)
        # anchor here decides part of canvas to place it by, here the width
        self.canvas_frame.place(x=0, y=100, anchor='nw')

        self.canvas = ctk.CTkCanvas(master=self.canvas_frame, width=1140, height=540, bg=grey, highlightbackground=grey, bd=3)
        self.canvas.place(x=0,y=0,anchor=tk.NW)

        self.entry_label = ctk.CTkLabel(self, text="Switching...", text_color=light_grey, font=('Arial', 18,'bold'))

        self.entry = ctk.CTkEntry(self, font=('Arial', 22,'bold'), width=160, text_color=light_blue, border_color=light_blue, border_width=2, corner_radius=0)
        self.entry.place(x=770, y=70, anchor='center')

        self.entry_label = ctk.CTkLabel(self, text="Switching...", text_color=light_grey, font=('Arial', 18,'bold'))

        self.validation_wrapper = (self.register(self.check_entry), '%P')
        self.entry.configure(validate="key", validatecommand=(self.validation_wrapper))

        
        # readonly as only for visual reminder, not used as a button
        self.word_btns = []
        # self.prev_word_btn = ctk.CTkButton(self, text="", state='readonly', text_color=light_blue, fg_color=dark_blue, border_color=light_blue, border_width=3, corner_radius=0, font=('Arial', 28,'bold'))

        # define variable to keep custom padding value consistent
        my_pad = 5
        
        # same command as return home button on other pages takes you back to homepage
        # like all other sub page buttons, uses standard button styles for some formatting
        self.back_btn = ctk.CTkButton(self, text="❮=", **ctrl.standard_btn_style, width=55, height=40, command=lambda: ctrl.new_page(Home_page))
        self.back_btn.place(x=my_pad,y=my_pad, anchor='nw')

        self.pause_btn = ctk.CTkButton(self, text="⏸", **ctrl.standard_btn_style, width=55, height=40, command=self.pause_play)
        self.pause_btn.place(x=65,y=5, anchor='nw')

        # named to not sound like the space bar key
        self.space_meter = ctk.CTkProgressBar(self, **bar_style)
        self.space_meter.place(x=120, y=50, anchor='nw')
        self.space_meter.set(0)

        self.space_text_label = ctk.CTkLabel(self, text="Space Taken:", text_color=yellow, font=('Arial', 24,'bold'))
        self.space_text_label.place(x=350,y=25, anchor='center')

        self.entry_text_label = ctk.CTkLabel(self, text="Enter a Word:", text_color=yellow, font=('Arial', 24,'bold'))
        self.entry_text_label.place(x=770,y=25, anchor='center')

        self.space_value_label = ctk.CTkLabel(self, text="0%", text_color=yellow, font=('Arial', 27,'bold'), bg_color=red, corner_radius=5)
        self.space_value_label.place(x=130,y=54, anchor='nw')
        
        # the labels just use manual formatting as have less parameters
        self.msg_label = ctk.CTkLabel(self, text="Player 1: Type a word and hit Enter to start!", text_color=orange, font=('Arial', 28,'bold'))
        # as this one is positioned from centre must move up from bottom of screen too
        self.msg_label.place(x=(ctrl.width-400)/2,y=ctrl.height-30, anchor='center')

        # randomly set who starts to player 1 or 2's (0 or 1)
        self.starts = random.randint(0,1)
        self.names = [self.ctrl.name1, self.ctrl.name2]

        # turn is used to initially choose the name for each label from the list
        self.name1_label = ctk.CTkLabel(self, text=('Player 1: ' +self.names[self.starts]), text_color=light_blue, font=('courier', 32,'bold'))
        self.name1_label.place(x=ctrl.width-my_pad,y=my_pad, anchor='ne')
    
        # score label saying just 'score' needed so score can have room to expand
        self.score1_text_label = ctk.CTkLabel(self, text="Score:", text_color=light_blue, font=('courier', 28,'bold'))
        self.score1_text_label.place(x=ctrl.width-20,y=55, anchor='ne')

        score1_label = ctk.CTkLabel(self, text="0", text_color=light_blue, font=('courier', 28,'bold'))
        score1_label.place(x=ctrl.width-70,y=105, anchor='center')

        score1_inc_label = ctk.CTkLabel(self, text="", text_color=light_blue, font=('courier', 26,'bold'))
        score1_inc_label.place(x=ctrl.width-70,y=140, anchor='center')

        # reduce size of button by copying and editing font value of dictionary
        # this button is given no horizontal padding to reduce the width it takes up 
        small_btn = ctrl.standard_btn_style.copy()
        small_btn['font'] = ('Arial', 24,'bold') 

        #self.current_colour
        self.timer_text_label = ctk.CTkLabel(self, text="Time(s)", text_color=light_blue, font=('courier', 28,'bold'))
        self.timer_text_label.place(x=ctrl.width-70,y=275, anchor='center')

        self.timer_bar = ctk.CTkProgressBar(self, **p1_timer_style)
        self.timer_bar.place(x=ctrl.width-80, y=300, anchor='nw')
        self.timer_bar.set(1)

        self.timer_val_label = ctk.CTkLabel(self, text="7", text_color=light_blue, font=('courier', 28,'bold'), bg_color=black)
        self.timer_val_label.place(x=ctrl.width-63,y=405, anchor='center')

        self.score2_text_label = ctk.CTkLabel(self, text="Score:", text_color=green, font=('courier', 28,'bold'))
        self.score2_text_label.place(x=ctrl.width-20,y=ctrl.height-120, anchor='se')

        score2_label = ctk.CTkLabel(self, text="0", text_color=green, font=('courier', 28,'bold'))
        score2_label.place(x=ctrl.width-70,y=ctrl.height-100, anchor='center')

        score2_inc_label = ctk.CTkLabel(self, text="", text_color=green, font=('courier', 26,'bold'))
        score2_inc_label.place(x=ctrl.width-70,y=ctrl.height-65, anchor='center')

        self.name2_label = ctk.CTkLabel(self, text=('Player 2: ' + self.names[not self.starts]), text_color=green, font=('courier', 32,'bold'))
        self.name2_label.place(x=ctrl.width-my_pad,y=ctrl.height-my_pad, anchor='se')


        # ------------------------ keybindings --------------------------
        
        # pressing enter submits word to method chain
        self.entry.bind('<Return>', self.check_allowed)
        # pressing 0 is a quick keybind to clear the text
        self.entry.bind('<0>',  lambda e: self.entry.delete(0, tk.END))
        # pressing 3 allows you to pause the game quickly
        self.entry.bind('<KeyPress-1>', lambda e: self.pause_play())

        #-------------------------- key attributes setup -------------------------- 

        self.valid_words = []

        # value for which players turn it is now
        self.turn = 0
        # number of turns taken to get a valid word
        self.turns_taken = 0
        # when starting new turn, used to check if turns taken needs incrementing
        self.word_played = False
        self.turn_phase = True
        self.paused = False
        self.time_taken = 0

        #  initialising score data 
        self.scores = [0,0]
        self.score_labels = [score1_label,score2_label]
        self.score_inc_labels = [score1_inc_label,score2_inc_label]
        self.score_increase = 0
        self.mistakes = 0

        # list of value that similarity must be above for the turns taken to be accepted

        req_values = [0.272, 0.272, 0.263, 0.25, 0.22]
        # limit this to a minimum of 0.75 or completely unrelated words will start being accepted
        req_val_mult = REQUIRED_ASSOCIATION_MULTIPLIER
        if req_val_mult < 0.75:
            req_val_mult = 0.75
        self.req_values = [round(value * req_val_mult, 3) for value in req_values]

        # mutipliers that reduces score gained as turns taken increases
        self.turns_taken_limiter = [1.0, 0.85, 0.6, 0.4, 0.25]

        # turn duration, each one is for each consecutive turn where the previous word does not change 
        turn_times = [6, 6, 7, 8, 8]
        self.turn_times = [round(time * TIME_MULTIPLIER) for time in turn_times]
        self.switch_length = round(SWITCH_LENGTH)
        self.penalty_mult = PENALTY_MULTIPLIER

        # make sure the penalties wouldn't cause errors if the user ended up making the multiplier negative
        if self.penalty_mult < 0:
            self.penalty_mult = 0

        # set placeholder task name so if task is cancelled before one ocurrs there isnt an error
        self.msg_task = 'after#0'

        # define specific widget's styles in list for variable attributes so can switch for new player
        self.button_styles = [{'fg_color': light_blue,'text_color': dark_blue,'border_color':light_blue},
                              {'fg_color': yellow,'text_color': black,'border_color':green}]

        self.timer_styles = [{'progress_color':light_blue,'border_color':blue},
                             {'progress_color':green,'border_color':yellow}]
        
        self.word_styles = [{'text_color':light_blue, 'fg_color': dark_blue, 'border_color': light_blue},
                                 {'text_color':dark_green, 'fg_color': yellow, 'border_color': green}]

        self.time_left = 0
        self.timer_length = 0
        
        self.game_started = False
        self.game_over = False
        # time between timer updates in seconds
        self.update_interval = 0.05

        # testing end phase
        # self.valid_words = ["camel","desert","dry","warming","global","environmental","catastrophe","calamity","warning","messenger","prophecy","foretell","read","believe","inspire","engage","activate","energy","fuel","petrol","fossil","ancient","mysterious","curious","investigate","detect","evidence","proof","truth","falsehood","failure","succeed","accomplish","certificate","leader","greatness","responsibility","respect","ignore","annoying","bothersome","irritate","persist","undying","pure","holiness","ritual","magic","danger","alert","scare","trigger","gun"]
        # for word in self.valid_words:
        #     new_word_btn = ctk.CTkButton(master=self.canvas_frame, width=0,text="", state='readonly', text_color=light_blue, fg_color=dark_blue, border_color=light_blue, border_width=3, corner_radius=0, font=('Arial', 26,'bold'))
        #     rand = random.randint(0,1)
        #     new_word_btn.configure(text=word, **self.word_styles[rand])
        #     self.word_btns.append(new_word_btn)


        # start of new game terminal log
        print(f'\n<<<============= {self.names[self.starts]} VS {self.names[not self.starts]} =============>>>')
        print("\n----------- Player 1's Turn ----------")


# -------------------- game page methods ---------------------

    # method to pause or play the game when the pause button is pressed during the main game
    def pause_play(self):
        if not self.game_started or self.game_over:
            return

        # switching state of pause cancels any tasks from continuing themselves
        self.paused = not self.paused

        # when they pause the game
        if self.paused: 
            # change symbol on pause button
            self.pause_btn.configure(text='⏵')
            # disable widgets while paused
            self.entry.configure(state='readonly')
        
        # when they click play again
        else:
            # change symbol on pause button
            self.pause_btn.configure(text='⏸')

            # re-enable widgets now the game is played if it is the turn phase
            if self.turn_phase:
                self.entry.configure(state='normal')

            # continues the correct timer from where it was, the timing values are saved from when it was cancelled
            # but depending on the current phase, we need to use the correct command and turn timer value
            if self.turn_phase:
                self.after(round(self.update_interval*1000), lambda: self.start_timer(self.start_switch, turn_timer=True))
            else:
                self.after(round(self.update_interval*1000), lambda: self.start_timer(self.start_turn, turn_timer=False))


    # method to restrict the text being entered into the main entry box
    def check_entry(self, new_text):
        for char in new_text:
            # range of characters with ascii values from a to z or A to Z
            if not ((96 < ord(char) < 123) or (64 < ord(char) < 91)):
                return False
            
        return True

    # first method to deal with words entered and catch some invalid forms or call the correct next check
    def check_allowed(self, e):

        self.current_word = self.entry.get()
        print(self.current_word, end='')

        if self.current_word == '':
            return
        
        if len(self.current_word) < 3:
            # no mistakes given for this error as they may not have known this
            self.update_msg('Word too short! [minimum 3 letters]', rose, 1500)
            return
        
        score_penalty = self.check_used()
        if score_penalty:
            self.update_msg('Base word already used! Try again', rose, 1500)
            
            # update score value and display in its label
            if self.scores[self.turn] - score_penalty < 0:
                # if score would have been reduced to less than 0, set score penalty to score so it becomes 0
                score_penalty = self.scores[self.turn]
            
            # reduce score by penalty decided
            self.scores[self.turn] -= score_penalty                

            self.score_labels[self.turn].configure(text=self.scores[self.turn])

            # this text is not cleared on a timer so it doesnt interfere with the score gain text
            self.score_inc_labels[self.turn].configure(text=f"-{score_penalty}")
            print(f' ==> -{score_penalty}')
            print('Base word already used!')
            return

        allowed = False
        #if the word was in the dictionary
        if self.check_enchant(self.current_word): 
            # if the word has a vector in the spacy database
            if self.check_spacy_vector(self.current_word):
                allowed = True
                # and the word is not the first valid word entered
                if len(self.valid_words) > 0: 
                    self.check_val() #check its spacy association value

                # if first word, it is real and has a spacy vector so can be added already
                else:
                    self.add2web()

        if not allowed:
            # if input invalid due to enchant or spacy check still warns them
            self.update_msg('Invalid word, try again', rose, 2000)
            print(': Invalid word!')
            if len(self.valid_words) > 0:
                self.mistakes += 1

    # method to run enchant checks with different cases
    def check_enchant(self, word):
        real_words =  enchant.Dict("en_GB")

        #check if lower/uppercase is real
        if real_words.check(word.lower()):
            return True
        if real_words.check(word.upper()):
            return True
        # check if real with just first letter uppercase
        if real_words.check(word[0].upper() + word[1:].lower()):
            return True

        # if the method was not left by now the word is not real
        return False
    
    # method to run enchant checks with different cases
    # after this stage, only the case used for spacy matters, but doesnt need saving as fast enough to try all combos
    # then original input can still be the form displayed 
    def check_spacy_vector(self, word, get_forms=False):
        valid_forms = []

        #check if lower/uppercase is defined in spacy
        if self.ctrl.nlp(word.lower()).has_vector:
            valid_forms.append(word.lower())

        # check with jsut first letter uppercase
        if self.ctrl.nlp(word[0].upper() + word[1:].lower()).has_vector:
            valid_forms.append(word[0].upper() + word[1:].lower())
        
        if get_forms:
            return valid_forms

        else:
            # if number of valid forms is 0 this equates to false
            return len(valid_forms)
    
    # method to change the message label's text, cancel any other update_msgs set to run,
    # and set the message to change back to normal after the time passed in
    # if no max time is passed in, it will not change back
    def update_msg(self, new_text, new_colour, max_time=False):
        self.msg_label.configure(text=new_text, text_color=new_colour)
        #
        self.after_cancel(self.msg_task)

        if max_time:
            self.msg_task = self.after(max_time, lambda: self.msg_label.configure(text=f"Player {self.turn+1}'s turn", text_color=orange))

    # method called by check_allowed to check for the base word being used before
    def check_used(self):
        new_word = self.current_word.lower()

        # using list comprehension to create list of lowercase words previously played
        # to check new word is an exact match to any words played before
        if new_word in [word.lower() for word in self.valid_words]:
            return round(random.randint(400, 570) * self.penalty_mult)

        # nlp(w1)[0].lemma_ gets a words lemma - checking the lemmas arent the same 
        # using list comprehension to create list of root words previously played and check new word root is it
        if self.ctrl.nlp(new_word)[0].lemma_ in [self.ctrl.nlp(word.lower())[0].lemma_ for word in self.valid_words]:
            return round(random.randint(250,400) * self.penalty_mult)
        
        # if the word is only 3 characters this check will not be taken
        # check if new word is a sub word of words played or if they are a sub word of the new word
        if len(new_word) > 3:
            # make list of lowercases of all previous words longer than 3 characters
            lowered = [word.lower() for word in self.valid_words if len(word) > 3]

            # check if one of the words is a partial word of the other
            for word in lowered:
                if new_word in word or word in new_word:
                    return round(random.randint(100,250) * self.penalty_mult)


    # method to get the spacy similarity value
    def check_val(self):
        # from the check allowed method we know both the words are defined in the spacy model
        # valid all lowercase, all uppercase, and only 1st uppercase will be checked to see highest

        # get list of all valid forms of both words being compared
        prev_words = self.check_spacy_vector(self.valid_words[-1], get_forms=True)
        current_words = self.check_spacy_vector(self.current_word, get_forms=True)

        # compare all potential combinations of words and add their scores to a list
        values = []
        for word1 in prev_words:
            for word2 in current_words:
                values.append((self.ctrl.nlp(word1)).similarity(self.ctrl.nlp(word2)))

        value = max(values)
        # if the highest value meets the current required value
        if value >= self.req_values[self.turns_taken]:
            self.calculate_score(value)

        else:
            self.entry.delete(0, tk.END)
            self.update_msg('Association too weak! Try again.', rose, 1500)
            print(': Association too weak!')
            self.mistakes += 1

    # method to find the score and call the next stage
    def calculate_score(self, value):

        self.time_taken = self.timer_length- self.time_left

        # score calculated using a combination of API association value, time taken and number of invalid entries
        # simply (850x(value - mistakes) + 300x(remaining/max time)) x turns taken limiter
        
        # as mistakes increases score decreases
        main_score = 850*(value - self.mistakes*0.03)
        time_score = 300 * ( (max(self.turn_times)-self.time_taken) /max(self.turn_times))

        score = (main_score + time_score) * self.turns_taken_limiter[self.turns_taken]
        score = round(score)

        # set score to maximum score if needed
        if score > 1000:
            score = 1000
        # set score to minimum score if needed
        if score < 100:
            score = 100
        self.score_increase = score

        self.add2web()

    # method to run initial processing of game state once successful word has been confirmed
    def add2web(self):

        # in the full link back version this would only run once the word was successfuly added:

        # clear entry since word was successfully submitted
        self.entry.delete(0, tk.END)

        # update score value and display in its label
        print(f' ==> +{self.score_increase}')
        self.scores[self.turn] += self.score_increase
        self.score_labels[self.turn].configure(text=self.scores[self.turn])
        
        if len(self.valid_words) > 0:
            # show score INCREASE in dedicated label and make it disappear after 1 second
            self.score_inc_labels[self.turn].configure(text=f"+{self.score_increase}")

            # set temporary variable to value of self.turn so when passed by reference, its not updated by changes to self.turn
            saved_turn_value = self.turn
            self.after(2000, lambda: self.score_inc_labels[saved_turn_value].configure(text=""))

        else:
            self.game_started = True

        self.valid_words.append(self.current_word)
        self.word_played = True


        new_word_btn = ctk.CTkButton(master=self.canvas_frame, width=0,text="", state='readonly', text_color=light_blue, fg_color=dark_blue, border_color=light_blue, border_width=3, corner_radius=0, font=('Arial', 26,'bold'))
        new_word_btn.configure(text=self.valid_words[-1], **self.word_styles[not self.turn])
        self.word_btns.append(new_word_btn)

        # word placement system
        row = 0
        x_value = 10
        for word_btn in self.word_btns:
            word_btn.update_idletasks()

            right_side = x_value + word_btn.winfo_reqwidth()
            next_x_value = right_side + 25

            if right_side > 1130:
                # old_x_value = 10
                x_value = 10
                next_x_value = x_value + word_btn.winfo_reqwidth() + 25
                row += 2

                if row >= 14:
                    if self.scores[0]>self.scores[1]:
                        winner = self.names[0]
                    elif self.scores[0]<self.scores[1]:
                        winner = self.names[0]
                    else:
                        winner = "everybody"

                    self.entry.configure(state='readonly')
                    self.entry.place_forget()

                    self.entry_text_label.configure(text="Game Over:")
                    self.winner_label = ctk.CTkLabel(self, text=f"The winner was {winner}!", text_color=rose, font=('Arial', 28,'bold'))
                    self.winner_label.place(x=780,y=70, anchor='center')

                    self.msg_label.configure(text=f"Click a word to show its definition", text_color=orange)
                    # self.msg_label.place(x=1140/2, y=450, anchor='center')
                    print("\nWeb of words full, game ended.")

                    for btn in self.word_btns:
                        btn.configure(state='normal', command=lambda b=btn: self.show_definition(b._text))

                    self.game_over = True
                    
            
            if not self.game_over:
                word_btn.place(x=x_value, y=10+row*self.word_height, anchor='nw')
                x_value = next_x_value

        space_taken = (1/7) * (row/2) + (1/7)*(next_x_value/1120)
        self.space_meter.set(round(space_taken,2))
        self.space_value_label.configure(text=f"{min(100,round(100*space_taken))}%")

        self.start_switch()

    def show_definition(self, word2define):
        synsets = wordnet.synsets(word2define)
        
        defs = []
        for set in synsets:
            for word in set.lemma_names():
                if word == word2define:
                    defs.append(set.definition())

        if len(defs) == 0:
            defs.append(synsets[0].definition())

        text = defs[0]
        font_size = 28
        if len(text) > 35:
            font_size = max(14, int(font_size-((len(text)-35)/5)))
        self.msg_label.configure(text=f"{word}: {defs[0]}", text_color=orange, font=('Arial', font_size,'bold'))

# method to initiate the switching phase
    def start_switch(self):
        if self.game_over:
            return
        # ------- reset flags and counters ---------

        if not self.word_played:
            # if a word wasnt played then another turn in the same run was used
            self.turns_taken += 1
            # clear any score penalty text if it wasn't cleared by a successful word's score increase
            self.score_inc_labels[self.turn].configure(text="")
        else:
            self.turns_taken = 0

        self.turn = not self.turn
        self.turn_phase = not self.turn_phase
        self.mistakes = 0
        self.time_taken = 0
        self.score_increase = 0

        # ------------ change colours to new player's ------------

        colours = [light_blue, green]

        self.timer_bar.configure(**self.timer_styles[self.turn])

        self.timer_text_label.configure(text_color=colours[self.turn])
        self.timer_val_label.configure(text_color = colours[self.turn])
        self.entry.configure(border_color = colours[self.turn], text_color = colours[self.turn])

        # ------------------ initiating switch phase ------------------ #
        self.entry.delete(0, tk.END)

        self.entry.configure(state='readonly')
        self.entry_label.place(x=770, y=70, anchor='center')
        
        # change message from turn msg to switching msg
        self.msg_label.configure(text=f"Switch! Get ready player {self.turn+1}.", text_color=orange)
        
        if self.turns_taken < 5:
            # this is the timer until switching is completed so turn_timer is false
            self.start_timer(self.start_turn, duration=self.switch_length, turn_timer=False)

        else:
            self.game_over = True
            self.entry.configure(state='readonly')
            self.entry.place_forget()
            self.msg_label.configure(text=f"Too many turns taken, game ended.", text_color=rose)
            print("\nToo many turns taken, game ended.")


# method to re-enable widgets and reset things for start of turn 
    def start_turn(self):
        self.entry.configure(state='normal')

        # change message from switching msg to turn msg
        self.msg_label.configure(text=f"Player {self.turn+1}'s turn", text_color=orange)
        self.entry_label.place_forget()

        print(f"\n----------- Player {self.turn+1}'s turn ----------")
        

        self.turn_phase = not self.turn_phase

        # only reset this flag after next turn starts so that if word was played,
        # the turn timer will have some time to cancel itself while this flag is True
        self.word_played = False

        # this is the timer until the turn ends (when the switching phase starts) so it is a 'turn timer'
        # this can be cancelled
        # self.start_timer(self.start_switch, duration=self.switch_length, turn_timer=True)
        self.start_timer(self.start_switch, duration=self.turn_times[self.turns_taken], turn_timer=True)


    # function to keep updating timer text (+ bar?) until timer up, then calls the action function
    # action is the method to call at the end of the timer
    # duration is passed in on first call, on other calls is not passed in
    def start_timer(self, action, duration=None, turn_timer=False):

        # if it is the first call set initial value of time_left attribute
        if duration:
            self.time_left = duration
            self.timer_length = duration

        else: # only decrement time if not the first call as then 1s hasnt passed yet
            self.time_left -= self.update_interval #decrease time left by time between updates
        
        # perform periodic update of timing widgets
        self.timer_val_label.configure(text= str(ceil(self.time_left)))
        self.timer_bar.set(self.time_left/self.timer_length)
        
        # call this method again after delay, if time not up and game is not paused
        if self.time_left > 0:
            if not self.game_over and not self.paused:
                
                # if it is a turn timer, it needs to stop calling itself once word_played is true
                cancel = False
                if turn_timer:
                    if self.word_played:
                        cancel = True
                        
                if not cancel:
                    #convert update rate to milleseconds as time until it is called,
                    # use lambda to allow parameters to be passed in
                    self.after(round(self.update_interval*1000), lambda: self.start_timer(action, turn_timer=turn_timer))

        else:
            action()

#---------------------------- other pages ------------------------

class Instructions_page(ctk.CTkFrame):

    def __init__(self, parent, ctrl): 
        super().__init__(parent)
        self.ctrl = ctrl

        self.background_img=ImageTk.PhotoImage(file="instructions.png")
        bgd_img_label = tk.Label(self, image = self.background_img)
        bgd_img_label.place(x=0,y=0)

        self.back_btn = ctk.CTkButton(self, text="❮=", **ctrl.standard_btn_style, width=55, height=40, command=lambda: ctrl.new_page(Home_page))
        self.back_btn.place(x=5,y=5, anchor='nw')


app = App()
app.mainloop()

