import numpy as np
import sys
import math
from collections import deque
from sympy import * #I,Matrix,symbols,subs,nan
from multiprocessing import Pool


from classes.component import Component
from classes.terms import Terms
from classes.variables import *

class Circuit:
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
        idx=0
        for node in self.components:
            for component in node:
                # print(np.shape(component.ABCDs))
                matrices[:,idx]=component.ABCDs
                idx+=1
        # For each frequency, combine the matrices
        ABCDs=np.asarray(list(map(self.combine_matrices,matrices)))
        # TODO upgrade to use Pool
        # with Pool(processes=8) as pool:
        #     ABCDs=pool.map(self.combine_matrices,matrices)

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
        if var in equations:
            # Check variable hasn't been calculated already
            if not var in self.variables:
                # Print variable and equation to console, indented to reflect dependency tree
                print("    "*dep_lvl+f"{var} = {equations[var]}")
                # Fetch dependencies of the equation.
                # Store in a 2d array, where first dimension is the variable and second is the frequency
                deps=np.empty((len(dependencies[var]),len(self.terms.freqs)),dtype=complex)
                for idx,d in enumerate(dependencies[var]):
                    # Calculate the values of that dependency (if not already done)
                    if not d in self.variables:
                        self.calc_output(d,dep_lvl+1)
                    # Add to table
                    deps[idx]=self.variables[d]
                # Create lambda function from equation to quickly evaluate at all frequencies
                l=lambdify(dependencies[var],equations[var])
                # apply the equation with given dependencies, using a lambda to quickly evaluate all freqs
                self.variables[var]=l(*deps) # have to unpack the dependencies
        else:
            print(f"Variable {var} has no equation")

    def __str__(self):
        components_string=""
        idx=0
        depth=3
        for node in self.components:
            for component in node:
                # components_string+="\n        "+var+"\n   "
                col_strings=str(component).splitlines(keepends=True)
                components_string+='        '.join(col_strings)
                idx+=1
                if idx==depth:
                    break
            if idx==depth:
                    break
        string=[
            "Circuit object:",
            f"    {self.num_components} components",
            f"    {len(self.components)} nodes",
            f"    First components (up to 3): {components_string}",
            
        ]
        return '\n'.join(string)