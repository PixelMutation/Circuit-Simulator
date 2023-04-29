import numpy as np
import sys
import math
from collections import deque
from sympy import * #I,Matrix,symbols,subs,nan
from multiprocessing import Pool

from classes.prefixes import prefixes
from classes.terms import Terms
from classes.variables import *



# Component value
Val=Symbol("Val")
w=Symbol("w")
class Component:
    node=None
    shunt=None
    Type=None
    value=None
    Z=None
    ABCD=None
    ABCDs=[]
    Z_expr={
        "R":  Val,
        "L":  I*w*Val,
        "C":-(I/(w*Val)),
        "G":  1/Val
    }
    def __init__(self,component_dict):
        # error checking:
        #TODO implement error checking
        # Set first node
        self.node=int(component_dict["n1"])
        # Shunt if n2==0
        self.shunt=not bool(int(component_dict["n2"]))
        # Find component type
        for t in ["R","L","C","G"]:
            if t in component_dict:
                self.Type=t
                value=component_dict[t]
                self.value=float(value)
                break
        for prefix in prefixes:
            if prefix in component_dict:
                self.value*=prefixes[prefix]
        # Set expression for impedance using expression for given component type
        self.Z=self.Z_expr[self.Type].subs(Val,self.value)
    def calc_impedances(self,freqs):
        # print(self.Z)
        # R and G are not frequency dependent
        if self.Type=="R":
            self.Z_values=np.full(len(freqs),self.value)
        elif self.Type=="G":
            self.Z_values=np.full(len(freqs),1/self.value)
        # L and C are frequency dependent so use a lambda to evaluate at each frequency
        else:
            self.Z_values=np.asarray(lambdify(w,self.Z)(2*np.pi*freqs))
        # print(self.Z_values)
        
        # print(self.Z_values)
    def calc_matrices(self):
        self.ABCDs=np.full((len(self.Z_values),2,2),np.identity(2,dtype=complex))
        # print(np.shape(self.ABCDs))
        #? Had issues here with slice notation replacing all Cs and Bs at all freqs
        #? In the end, was solved by using a numpy array instead of a list of matrices
        if self.shunt:
            # Set C to the admittance
            # print(np.shape(self.ABCDs[:,0,1]))
            self.ABCDs[:,0,1]=1/self.Z_values
        else:
            # Set B to the impedance
            # print(np.shape(self.ABCDs[:,1,0]))
            self.ABCDs[:,1,0]=self.Z_values
        # print(self.ABCDs[0])
    def __str__(self):
        string=[
            f"\nNode: {self.node}",
            f"    Shunt: {self.shunt}",
            f"    Type: {self.Type}",
            f"    Value: {self.value}",
            f"    Impedance: {self.Z}",
            # f"    ABCD: {self.ABCD}",
        ]
        return '\n'.join(string)

A,B,C,D,VT,ZS,ZL=symbols("A,B,C,D,VT,ZS,ZL")
inv_A,inv_B,inv_C,inv_D=symbols("inv_A,inv_B,inv_C,inv_D")
# complex conjugates
# conj_Ai,conj_Iin,conj_Iout = symbols("Ai*,Iin*,Iout*") 

class Circuit:
    # Sympy equations for each variable, to be converted to lambdas
    # This allows any new variable to easily be defined
    equations={
        Vin  :   Iin*Zin,
        Vout :   Vin*inv_A+Iin*inv_B,
        Iin  :   VT/(ZS+Zin),
        Iout :   Vin*inv_C+Iin*inv_D,
        Zin  :   (A*ZL+B)/(C*ZL+D),
        Zout :   (D*ZS+B)/(C*ZS+A),
        Pin  :   Vin*conjugate(Iin),
        Pout :   Vout*conjugate(Iin),
        Av   :   ZL/(A*ZL+B),
        Ai   :   1 /(C*ZL+D),
        Ap   :   Av*conjugate(Ai),
    }

    # Stores the dependencies of each variable that must be calculated first
    dependencies={
        Vin     : [Iin,Zin],
        Vout    : [Vin,Iin,inv_A,inv_B],
        Iin     : [VT,ZS,Zin],
        Iout    : [Vin,inv_C,Iin,inv_D],
        Zin     : [A,B,C,D,ZL],
        Zout    : [A,B,C,D,ZS],
        Pin     : [Vin,Iin],
        Pout    : [Vout,Iin],
        Av      : [A,B,C,ZL],
        Ai      : [B,C,D,ZL],
        Ap      : [Av,Ai],
    }

    num_components=0 # Size of the circuit
    components=None # stores Component objects
    terms=None # stores Terms object
    # ABCDs=[] # Overall ABCDs evaluated at each frequency
    variables={} # Stores raw calculated variables
    # Constructor
    def __init__(self,circuit_list,terms):
        self.terms = terms
        # Create empty circuit, assuming each component is series
        self.components=[deque() for i in range(len(circuit_list))]
        num_nodes=0
        self.num_components=len(circuit_list)
        # For each dictionary from CIRCUIT in .net file
        for component_dict in circuit_list:
            # Create component from dictionary
            component = Component(component_dict)
            if component.node>num_nodes:
                num_nodes=component.node
            # print(component.node)
            # Place component in shunt or series based on n2
            if component.shunt:
                self.components[component.node-1].appendleft(component)
            else:
                self.components[component.node-1].append(component)
        # Remove extra nodes
        self.components=self.components[:num_nodes]
        # Store terms in variables dict for easy access
        self.variables[VT]=np.full(len(terms.freqs),terms.VT)
        self.variables[ZS]=np.full(len(terms.freqs),terms.ZS)
        self.variables[ZL]=np.full(len(terms.freqs),terms.ZL)

    # Combines a list of matrices via matrix multiplication
    def combine_matrices(self,matrices):
        ABCD=matrices[0]
        for mat in matrices[1:]:
            # print(mat)
            ABCD=np.matmul(ABCD,mat)
        # print(ABCD)
        return ABCD

    # Combine ABCDs to get overall ABCD at each frequency
    def calc_overall_ABCDs(self):
        matrices=np.empty((len(self.terms.freqs),self.num_components,2,2),dtype=complex)
        # print(np.shape(matrices))
        idx=0
        for node in self.components:
            for component in node:
                print(np.shape(component.ABCDs))
                matrices[:,idx]=component.ABCDs
                idx+=1
        # For each frequency, combine the matrices
        ABCDs=np.asarray(list(map(self.combine_matrices,matrices)))
        # TODO upgrade to use Pool
        # with Pool(processes=8) as pool:
        #     ABCDs=pool.map(self.combine_matrices,matrices)
        # print(ABCDs[0])
        # print(np.shape(ABCDs))
        # Split results into variables dict for easy access
        self.variables[A]=ABCDs[:,0,0]
        self.variables[B]=ABCDs[:,0,1]
        self.variables[C]=ABCDs[:,1,0]
        self.variables[D]=ABCDs[:,0,1]
        #? Had issues here with indexing, incorrectly accessed as single index 0-3 like sympy matrices
        #? also tried to extract as ABCDs[0][0] which doesnt work as need to extract all items of first dimension using :

        # Invert
        inv_ABCDs=np.linalg.inv(ABCDs)
        self.variables[inv_A]=inv_ABCDs[:,0,0]
        self.variables[inv_B]=inv_ABCDs[:,0,1]
        self.variables[inv_C]=inv_ABCDs[:,1,0]
        self.variables[inv_D]=inv_ABCDs[:,0,1]

    # Calculate the ABCDs of each component for each frequency
    def calc_component_ABCDs(self):
        idx=0
        # Calculate individual ABCD matrices
        for i,node in enumerate(self.components):
            for j,component in enumerate(node):
                idx+=1
                # print(f"n{i} {idx}/{self.num_components}",end="\r")
                component.calc_impedances(self.terms.freqs)
                component.calc_matrices()

    # Calculates the chosen variable and any dependencies
    def calc_output(self,var,dep_lvl=0):
        # Check variable can be calculated
        if var in self.equations:
            # Check variable hasn't been calculated already
            if not var in self.variables:
                # Print variable and equation to console, indented to reflect dependency tree
                print("    "*dep_lvl+f"{var}={self.equations[var]}")
                # Fetch dependencies of the equation.
                # Store in a 2d array, where first dimension is the variable and second is the frequency
                deps=np.empty((len(self.dependencies[var]),len(self.terms.freqs)),dtype=complex)
                for idx,d in enumerate(self.dependencies[var]):
                    # Calculate the values of that dependency (if not already done)
                    if not d in self.variables:
                        self.calc_output(d,dep_lvl+1)
                    # Add to table
                    deps[idx]=self.variables[d]
                print(np.shape(deps))
                # deps=np.rot90(deps)
                # print(np.shape(deps))
                # Create lambda function from equation to quickly evaluate at all frequencies
                print(self.dependencies[var])
                l=lambdify(self.dependencies[var],self.equations[var])
                # apply the equation with given dependencies, using a lambda to quickly evaluate all freqs
                self.variables[var]=l(*deps) # have to unpack the dependencies
                # print(self.variables[var])
        else:
            print(f"Variable {var} has no equation")

    def __str__(self):
        components_string=""
        for node in self.components:
            for component in node:
                # components_string+="\n        "+var+"\n   "
                col_strings=str(component).splitlines(keepends=True)
                components_string+='        '.join(col_strings)
        string=[
            "Circuit object:",
            # f"    ABCD: {self.ABCD}",
            f"    Components: {components_string}",
            
        ]
        return '\n'.join(string)