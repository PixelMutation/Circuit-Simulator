from sympy import *
import numpy as np

from classes.prefixes import prefixes

# Component value
Val=Symbol("Val")
w=Symbol("w")

Z_expr={
    "R":  Val,
    "L":  I*w*Val,
    "C":-(I/(w*Val)),
    "G":  1/Val
}
Z_lambdas={}
# generate lambdas to quickly calculate impedances
for t,expression in Z_expr.items():
    Z_lambdas[t]=lambdify((Val,w),expression,modules="numpy")

class Component:
    # node=None # n1
    # shunt=None # whether shunt or series
    # Type=None # R,L,C or G
    # value=None # component value (e.g. in ohms for resistors)
    # Z=None # expression for impedance
    # Z_values=None # impedance at each freq
    # ABCDs=None # ABCD at each freq

    # Constructor
    def __init__(self,component_dict):
        
        # Set first node
        n1=int(component_dict["n1"])
        n2=int(component_dict["n2"])
        self.node=n1
        # Shunt if n2==0
        self.shunt=not bool(n2)
        # Find component type
        self.Type=None
        for t in ["R","L","C","G"]:
            # Check it is a valid type
            #// TODO add response if invalid 
            if t in component_dict:
                self.Type=t
                value=component_dict[t]
                # Attempt to convert component value to float
                try:
                    self.value=float(value)
                    if self.value==0:
                        print(f"WARNING: Component {component_dict} has a value of zero! This may cause errors.")
                except:
                    raise TypeError(f"Could not convert \"{value}\" to float in {component_dict}")
                break
        if self.Type is None:
            raise SyntaxError(f"Line {component_dict} does not contain a component value")
        # Check for SI prefixes
        prefix_found=False
        for prefix in prefixes:
            if prefix in component_dict:
                # G prefix can conflict with G component, so check value is None
                if component_dict[prefix] is None:
                    self.value*=prefixes[prefix]
                    prefix_found=True
                    break
                    
        # check correct number of entries
        if (len(component_dict)>3 and not prefix_found) or len(component_dict)>4:
            raise SyntaxError(f"Line {component_dict} has incorrect number of key:value pairs")
        for key in ["n1","n2"]:
            if not key in component_dict:
                raise SyntaxError(f"Line {component_dict} is missing {key}")
        # substitute the value into the sympy expression for display
        self.Z=Z_expr[self.Type].subs(Val,self.value)
    # Calculate the impedance at each frequency
    def calc_impedances(self,freqs):
        # Create array of the component value for each frequency
        vals=np.full(len(freqs),self.value)
        # Apply lambda function for the component type to calculate the impedance
        self.Z_values=np.asarray(Z_lambdas[self.Type](vals,2*np.pi*freqs),dtype=np.longcomplex)
    # Calculate the ABCD matrix at each frequency
    def calc_matrices(self):
        self.ABCDs=np.full((len(self.Z_values),2,2),np.identity(2,dtype=np.longcomplex))
        #? Had issues here with slice notation replacing all Cs and Bs at all freqs
        #? In the end, was solved by using a numpy array instead of a list of matrices
        if self.shunt:
            # Set C to the admittance
            self.ABCDs[:,1,0]=1/self.Z_values
        else:
            # Set B to the impedance
            self.ABCDs[:,0,1]=self.Z_values
    
    # create string representing object
    def __str__(self):
        string=[
            f"\nNode: {self.node}",
            f"    Shunt: {self.shunt}",
            f"    Type: {self.Type}",
            f"    Value: {self.value}",
            f"    Impedance: {self.Z}",
            f"    First ABCD: [{self.ABCDs[0,0,0]} {self.ABCDs[0,0,1]}]",
            f"                [{self.ABCDs[0,1,0]} {self.ABCDs[0,1,1]}]",
        ]
        return '\n'.join(string)