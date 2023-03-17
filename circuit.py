import numpy as np
import Enum


components=[[component({"n1"=1,"n2"=2,"L"=5})],]

def calc_impedance(type,value):


def c_type(Enum):
    CAPACITOR='C'
    RESISTOR='R'
    INDUDCTOR='L'
    CONDUCTOR='G'

allowed_types={
    "C":impedanceEquation
    "R":impedanceEquation
    "L":impedanceEquation
    "G":impedanceEquation
}

class component:
    n1=None
    n2=None
    impedance=None
    shunt=None
    component_type=None
    component_value=None
    matrix=    impedance=None
None

    def __init__(self,dict):
        self.n1=int(dict["n1"])
        self.n2=int(dict["n2"])
        self.shunt=self.n2==0
        if "C" in dict:
            self.component_type=c_type.CAPACITOR
            self.component_value=float(dict[C])
        elif "R" in dict:


        else:
            #error
            print(f"Couldn't find component type in {dict}")
        

    def multiply(self,inputMatrix):

    def calcImpedance(self)

    def print(self):
        printMatrix(self.matrix)


class series(component):
    def multiply(self,inputMatrix):

class shunt(component):
    def multiply(self,inputMatrix):


# create ordered list of components
# for components:
    # 



# we could use dicts to store each node read directly from the file
# This prevents 
component_dict = [
    "Node_in":None,
    "Node_out":None,
    #"L":None
    #"C":None
    #"R":None
    #"G":None
]

class two_port:
    ABCD=None
    input_node=None
    output_node=None
    def __init__(self,component):
