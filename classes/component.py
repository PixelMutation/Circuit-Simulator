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

    def __init__(self,component_dict):
        # error checking:
        if len(component_dict)>3:
            raise SyntaxError(f"Line {component_dict} has incorrect number of key:value pairs")
        for key in ["n1","n2"]:
            if not key in component_dict:
                raise SyntaxError(f"Line {component_dict} is missing {key}")
        # Set first node
        n1=int(component_dict["n1"])
        n2=int(component_dict["n2"])
        self.node=n1
        # Shunt if n2==0
        self.shunt=not bool(n2)
        # Find component type
        self.Type=None
        for t in ["R","L","C","G"]:
            # Check it is valid
            #// TODO add response if invalid 
            if t in component_dict:
                self.Type=t
                value=component_dict[t]
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
        for prefix in prefixes:
            if prefix in component_dict:
                # G prefix can conflict with G component, so check value is None
                if component_dict[prefix] is None:
                    self.value*=prefixes[prefix]
        self.Z=Z_expr[self.Type].subs(Val,self.value)
    def calc_impedances(self,freqs):
        # print(self.Z)
        # R and G are not frequency dependent
        # if self.Type=="R":
        #     self.Z_values=np.full(len(freqs),self.value)
        # elif self.Type=="G":
        #     self.Z_values=np.full(len(freqs),1/self.value)
        # L and C are frequency dependent so use a lambda to evaluate at each frequency
        # else:
            # self.Z_values=np.asarray(lambdify(w,self.Z)(2*np.pi*freqs))
        vals=np.full(len(freqs),self.value)
        self.Z_values=np.asarray(Z_lambdas[self.Type](vals,2*np.pi*freqs),dtype=np.longcomplex)
        # print(self.Z_values)
        
        # print(self.Z_values)
    def calc_matrices(self):
        self.ABCDs=np.full((len(self.Z_values),2,2),np.identity(2,dtype=np.longcomplex))
        # print(np.shape(self.ABCDs))
        #? Had issues here with slice notation replacing all Cs and Bs at all freqs
        #? In the end, was solved by using a numpy array instead of a list of matrices
        if self.shunt:
            # Set C to the admittance
            # print(np.shape(self.ABCDs[:,0,1]))
            self.ABCDs[:,1,0]=1/self.Z_values
        else:
            # Set B to the impedance
            # print(np.shape(self.ABCDs[:,1,0]))
            self.ABCDs[:,0,1]=self.Z_values
        # print(self.ABCDs[0])
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