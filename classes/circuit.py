import numpy as np
import sys
import math
from collections import deque
from sympy import * #I,Matrix,symbols,subs,nan
from multiprocessing import Pool

from classes.prefixes import prefixes
from classes.terms import Terms
from classes.variables import *

A,B,C,D,ZS,ZL,w,f=symbols("A,B,C,D,ZS,ZL,w,f")

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
        if self.shunt:
            Y=lambdify(w,(1/self.Z))
            for f in freqs:
                mat=np.mat([
                    [1           ,0],
                    [Y(2*np.pi*f),1]]
                )
                self.ABCDs.append(mat)
        else:
            Z=lambdify(w,self.Z)
            for f in freqs:
                mat=np.mat([
                    [1,Z(2*np.pi*f)],
                    [0,           1]]
                )
                self.ABCDs.append(mat)
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

# Stores the Sympy equations for each variable
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
}

# Stores the dependencies of each variable
dependencies={
    Vin  : [],
    Vout : [],
    Iin  : [],
    Iout : [],
    Zin  : [],
    Zout : [],
    Pin  : [],
    Pout : [],
    Av   : [],
    Ai   : [],
    Ap   : [Av,Ai_conj],
    Ai_conj:[Ai],
}

class Circuit:
    num_components=0 # Size of the circuit
    components=None # stores Component objects
    terms=None # stores Terms object
    ABCDs=[] # Overall ABCDs evaluated at each frequency
    calculated_vars={} # Stores raw calculated variables

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

    # Combines a list of matrices
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
        self.ABCDs=list(map(self.combine_matrices,matrices))
        print(self.ABCDs[0])

    # Calculate the ABCDs of each component for each frequency
    def calc_ABCDs(self):
        idx=0
        # Calculate individual ABCD matrices
        for i,node in enumerate(self.components):
            for j,component in enumerate(node):
                idx+=1
                print(f"n{i} {idx}/{self.num_components}",end="\r")
                component.calc_impedance()
                component.calc_matrix()
                # if first component, set overall ABCD to component ABCD
                if i==0 and j==0:
                    self.ABCD=component.ABCD
                # otherwise, multiply overall ABCD by component ABCD
                else:
                    self.ABCD=self.ABCD*component.ABCD

    # Calculates the chosen variable and any dependencies
    def calc_output(self,var):
        # Check variable hasn't been calculated already
        if not var in self.calculated_vars:
            print(f"Calc {var}")
            # Substitute the input conditions
            expr = equations[var]
            expr = expr.subs(ZS,self.terms.ZS)
            expr = expr.subs(ZL,self.terms.ZL)
            # Check if Ai*, in which case find complex conjugate  
            if var == Ai_conj:
                # Ensure Ai has been calculated
                self.calc_output(Ai)
                self.calculated_vars[var]=np.conjugate(self.calculated_vars[Ai])
            else:
                self.calculated_vars[var]=[expr for i in range(len(self.terms.freqs))]
                # Check for dependencies (e.g. Av, Ai* for Ap) 
                for d in dependencies[var]:
                    # Calculate the values of that dependency (if not already done)
                    self.calc_output(d)
                # For each
                for idx,val in enumerate(self.calculated_vars[var]): # TODO replace this loop with pool.map
                    # Substitue all dependencies
                    for d in dependencies[var]:
                        val=val.subs(d,self.calculated_vars[d][idx])
                    # Substitute overall ABCD values for each frequency
                    self.calculated_vars[var][idx]=self.sub_ABCD(val,self.ABCDs[idx])
    # Substitues the values of
    def sub_ABCD(self,expr,ABCD,dependencies):
        expr = expr.subs(A,ABCD[0])
        expr = expr.subs(B,ABCD[1])
        expr = expr.subs(C,ABCD[2])
        expr = expr.subs(D,ABCD[3])
        return expr
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