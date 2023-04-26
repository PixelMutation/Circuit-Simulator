import numpy as np
import sys
import math
from collections import deque
from sympy import * #I,Matrix,symbols,subs,nan
from multiprocessing import Pool

from classes.prefixes import prefixes
from classes.terms import Terms
from classes.variables import *

A,B,C,D,VT,ZS,ZL,w,f=symbols("A,B,C,D,VT,ZS,ZL,w,f")
Z=Symbol("Z")
class Component:
    node=None
    shunt=None
    Type=None
    value=None
    Z=None
    ABCD=None
    ABCDs=[]
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
        # Convert conductance to resistance 
        if self.Type=="G":
            self.Type="R"
            self.value=1/self.value
    def calc_impedance(self):
        if self.Type=="R":
            self.Z=self.value
        elif self.Type=="L":
            self.Z=I*w*self.value
        else:
            self.Z=-(I/(w*self.value))
    def calc_matrices(self,freqs):
        # Set ABCD expression based on whether component is shunt or series
        if self.shunt:
            self.ABCD=([
                [1,      0],
                [1/Z,    1]])
        else:
            self.ABCD=([
                [1,      Z],
                [0,      1]])
        # Substitute Z expression of component type into ABCD
        self.ABCD=self.ABCD.subs(Z,self.Z)
        # Then convert to lambda for fast evaluation
        calcABCD=lambdify(w,self.ABCD)
        # Evaluate for all chosen frequencies
        self.ABCDs=calcABCD(2*np.pi*freqs)
    def __str__(self):
        string=[
            f"\nNode: {self.node}",
            f"    Shunt: {self.shunt}",
            f"    Type: {self.Type}",
            f"    Value: {self.value}",
            f"    Impedance: {self.Z}",
            f"    ABCD: {self.ABCD}",
        ]
        return '\n'.join(string)

# complex conjugate of Ai, not an output variable. requires special logic
Ai_conj = symbols("Ai*") 

class Circuit:
    # Sympy equations for each variable, to be converted to lambdas
    # This allows any new variable to easily be defined
    equations={
        Vin  :   nan,
        Vout :   nan,
        Iin  :   nan,
        Iout :   nan,
        Zin  :   (A*ZL+B)/(C*ZL+D),
        Zout :   (D*ZS+B)/(C*ZS+A),
        Pin  :   nan,
        Pout :   nan,
        Av   :   ZL/(A*ZL+B),
        Ai   :   1 /(C*ZL+D),
        Ap   :   nan,
        Ai_conj :nan, # Requires special logic
    }
    # Stores the dependencies of each variable that must be calculated first
    dependencies={
        Vin     : [],
        Vout    : [],
        Iin     : [],
        Iout    : [],
        Zin     : [A,B,C,D,ZL],
        Zout    : [A,B,C,D,ZS],
        Pin     : [],
        Pout    : [],
        Av      : [A,B,C,ZL],
        Ai      : [B,C,D,ZL],
        Ap      : [Av,Ai_conj],
        Ai_conj : [Ai],
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
        self.variables[VT]=[terms.VT]*len(terms.freqs)
        self.variables[ZS]=[terms.ZS]*len(terms.freqs)
        self.variables[ZL]=[terms.ZL]*len(terms.freqs)

    # Combines a list of matrices via matrix multiplication
    def combine_matrices(self,matrices):
        ABCD=matrices[0]
        for mat in matrices[1:]:
            print(mat)
            ABCD=np.matmul(ABCD,mat)
        print(ABCD)

    # Combine ABCDs to get overall ABCD at each frequency
    def calc_overall_ABCDs(self):
        matrices=[]
        for node in self.components:
            for component in node:
                # First find the impedance
                component.calc_impedance()
                # Then evaluate the ABCD at each frequency
                component.calc_matrices(self.terms.freqs)
                matrices.append(component.ABCDs)
        matrices=np.asarray(matrices)
        matrices=np.swapaxes(matrices,0,1)
        print(np.shape(matrices))
        # For each frequency, combine the matrices
        # TODO upgrade to use Pool
        # self.ABCDs=Pool(processes=8).map(self.combine_matrices,matrices.tolist())
        ABCDs=list(map(self.combine_matrices,matrices))
        print(ABCDs[0])
        # Split results into variables dict for easy access
        self.variables[A]=ABCDs[0]
        self.variables[B]=ABCDs[1]
        self.variables[C]=ABCDs[2]
        self.variables[D]=ABCDs[3]

    # Calculate the ABCDs of each component for each frequency
    def calc_component_ABCDs(self):
        idx=0
        # Calculate individual ABCD matrices
        for i,node in enumerate(self.components):
            for j,component in enumerate(node):
                idx+=1
                print(f"n{i} {idx}/{self.num_components}",end="\r")
                component.calc_impedance()
                component.calc_matrix()

    # Calculates the chosen variable and any dependencies
    def calc_output(self,var):
        # Check variable can be calculated
        if var in self.equations:
            # Check variable hasn't been calculated already
            if not var in self.variables:
                print(f"Calc {var}")
                # Check if Ai*, in which case find complex conjugate  
                if var == Ai_conj:
                    # Ensure Ai has been calculated
                    self.calc_output(Ai)
                    self.variables[var]=np.conjugate(self.variables[Ai])
                else:
                    # Check for dependencies (e.g. Av, Ai* for Ap) 
                    deps=[]
                    for d in self.dependencies[var]:
                        # Calculate the values of that dependency (if not already done)
                        if not d in self.variables:
                            self.calc_output(d)
                        # Add to table
                        deps.append(self.variables[d])
                    # Convert table to np matrix so we can iterate over each row
                    deps=np.hstack(deps)
                    # Create lambda function from equation to quickly calculate the value
                    l=lambdify(self.dependencies[var],self.equations[var])
                    # For each frequency, apply the equation given the parameters
                    self.variables[var]=l(deps)
                    # # TODO upgrade to use Pool
                    # self.variables[var]=list(map(l,deps))
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