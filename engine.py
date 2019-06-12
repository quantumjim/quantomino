from ipywidgets import widgets  
from IPython.display import display

from qiskit import *
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import CommutativeCancellation

import random

import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def run_game(game):
    '''
    Runs the given game.
    
    This game engine supports turn based play.
    In each turn, the player chooses first chooses an option for an input
    named `a`, and then chooses an option for `c`. The
    image and the possible options for each input can be altered based on
    the inputs given.
    '''
        
    input_a = widgets.ToggleButtons(options=game.options_a)
    input_c = widgets.ToggleButtons(options=[''])

    boxes = widgets.VBox([input_a,input_c])
    display(boxes)

    def given_a(obs_a):
        if input_a.value not in ['',input_a.options[0]] and (input_a.value in input_a.options):
            game.given_a(input_a.value)
            input_c.options = game.options_c

    def given_c(obs_c):
        if (input_c.value not in ['',input_c.options[0]]) and (input_c.value in input_c.options):
            game.given_c(input_c.value)
            input_a.options = game.options_a
            input_c.options = ['']          

    input_a.observe(given_a)
    input_c.observe(given_c)
    
    
class GameObject():

    def __init__ (self,n=4,limit=7,goal=5):
        
        self.n = n
        self.limit = limit
        self.goal = goal
        self.qc = QuantumCircuit(self.n)
        self.gate = random.choice( ['x','y','z','h'] )
        eval('self.qc.'+self.gate +'('+str(random.randint(0,self.n-1))+')')
        self.qc.draw(output='latex',filename='temp.png')
        self.last_gates = [self.gate,self.gate,self.gate]
        
        # set up the figure and display the initial image
        self.fig = plt.figure()
        self.ax = self.fig.gca()
        self.fig.show()
        plt.axis('off')
        image = mpimg.imread("temp.png")
        plt.imshow(image, interpolation='None')
        self.fig.canvas.draw()
        
        # define initial values and choices for the three inputs
        self.a = ''
        self.c = ''
        
        self.gate = random.choice( ['x','y','z','h','cx','cx'] )
        
        self.options_a = self.gate_options(self.gate)
        self.options_c = ['']
        
        self.reduction = 0
      
    def gate_options(self,gate):
        if gate=='cx':
            gate_list = [ gate +'('+str(j)+','+str(j+1)+')' for j in range(self.n-1) ]
        else:
            gate_list = [ gate +'('+str(j)+')' for j in range(self.n) ]
        return ['Choose a gate']+gate_list
    
    def show_image(self,filename):
        image = mpimg.imread(filename)
        plt.imshow(image, interpolation='None')
        self.fig.canvas.draw()
    
    def given_a(self,a):
        '''
        Stores input a and sets up options for input b.
        '''        
        self.a = a
        self.options_c = ['','Confirm']
        
    def given_c(self,c):
        '''
        Stores input c and sets up a new round, with options for a and none for b and c.
        
        Also displays an image that depends on the output for c.
        '''
        self.c = c
        
        eval('self.qc.'+self.a)
        self.qc.draw(output='latex',filename='temp.png')
        self.show_image("temp.png")
        depth = self.qc.depth()
        
        pm = PassManager(CommutativeCancellation())
        self.qc = pm.run(self.qc)
        self.qc.draw(output='latex',filename='temp.png')
        self.show_image("temp.png")
        
        self.reduction += ( depth - self.qc.depth() )
        
        print('Current gate depth: '+str(self.qc.depth())+'. Limit: '+str(self.limit))
        print('Current circuit reduction: '+str(self.reduction)+'. Goal: '+str(self.goal))
        print('')
        
        if self.qc.depth()<self.limit:
            self.last_gates[2] = self.last_gates[1]
            self.last_gates[1] = self.last_gates[0] 
            self.last_gates[0] = self.gate
            self.gate = random.choice( list(set(['x','y','z','h','cx','cx'])-set(self.last_gates) ) )
            self.options_a = self.gate_options(self.gate)
            self.options_c = ['']
        else:
            plt.close(self.fig)
            self.options_a = ['GAME OVER']
            self.options_c = ['GAME OVER']
        
        if self.reduction>=self.goal:
            plt.close(self.fig)
            self.options_a = ['YOU WON!']
            self.options_c = ['YOU WON!'] 
