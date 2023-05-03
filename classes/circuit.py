import numpy as np
import sys
import math
from collections import deque
from sympy import * #I,Matrix,symbols,subs,nan
from multiprocessing import Pool
from matplotlib import ticker

from classes.component import Component
from classes.terms import Terms
from classes.variables import *
from classes.icons import icons

class Circuit:
    num_components=0 # Size of the circuit
    components=None # stores Component objects
    terms=None # stores Terms object
    # ABCDs=[] # Overall ABCDs evaluated at each frequency
    variables={} # Stores raw calculated variables
    f_idx=0 # used to print progress when combining ABCDs
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
        # Check for missing components
        for idx,node in enumerate(self.components):
            if len(node)==0:
                raise Exception(f"Missing component at node {idx+1}")
        # copy terms to variables dict for easy access
        self.variables[VS]=np.full(len(terms.freqs),terms.VS)
        self.variables[ZS]=np.full(len(terms.freqs),terms.ZS)
        self.variables[ZL]=np.full(len(terms.freqs),terms.ZL)

    # Combines a list of matrices via matrix multiplication
    def combine_matrices(self,matrices):
        self.f_idx+=1
        print(f"Freq {self.f_idx}/{len(self.terms.freqs)}",end="\r")
        ABCD=matrices[0]
        for mat in matrices[1:]:
            # print(mat)
            ABCD=np.matmul(ABCD,mat)
        # print(ABCD)
        return ABCD

    # Combine ABCDs to get overall ABCD at each frequency
    def calc_overall_ABCDs(self):
        matrices=np.empty((len(self.terms.freqs),self.num_components,2,2),dtype=np.longcomplex)
        idx=0
        for node in self.components:
            for component in node:
                # print(np.shape(component.ABCDs))
                matrices[:,idx]=component.ABCDs
                idx+=1
        # For each frequency, combine the matrices
        ABCDs=np.asarray(list(map(self.combine_matrices,matrices)))
        print("\n",end="")
        # TODO upgrade to use Pool
        # with Pool(processes=8) as pool:
        #     ABCDs=pool.map(self.combine_matrices,matrices)

        # Split results into variables dict for easy access in calculations
        self.variables[A]=ABCDs[:,0,0]
        self.variables[B]=ABCDs[:,0,1]
        self.variables[C]=ABCDs[:,1,0]
        self.variables[D]=ABCDs[:,1,1]
        # print(ABCDs[0])
        #? Had issues here with indexing, incorrectly accessed as single index 0-3 like sympy matrices
        #? also tried to extract as ABCDs[0][0] which doesnt work as need to extract all items of first dimension using :

    # Calculate the ABCDs of each component for each frequency
    def calc_component_ABCDs(self):
        idx=0
        # Calculate individual ABCD matrices
        for i,node in enumerate(self.components):
            for j,component in enumerate(node):
                idx+=1
                print(f"n{i} {idx}/{self.num_components}",end="\r")
                component.calc_impedances(self.terms.freqs)
                component.calc_matrices()
        print("\n",end="")

    # Calculates the chosen variable and any dependencies recursively
    def calc_output(self,var,dep_lvl=0):
        # Check variable can be calculated
        if var in equations:
            # Check variable hasn't been calculated already
            if not var in self.variables:
                # Print variable and equation to console, indented to reflect dependency tree
                print("    "*dep_lvl+f"{var} = {equations[var]}")
                # Fetch dependencies of the equation.
                # Store in a 2d array, where first dimension is the variable and second is the frequency
                deps=np.empty((len(dependencies[var]),len(self.terms.freqs)),dtype=np.longcomplex)
                for idx,d in enumerate(dependencies[var]):
                    # Calculate the values of that dependency (if not already done)
                    if not d in self.variables:
                        self.calc_output(d,dep_lvl+1)
                    # Add to table
                    deps[idx]=self.variables[d]
                # Create lambda function from equation to quickly evaluate at all frequencies
                l=lambdify(dependencies[var],equations[var],modules="numpy")
                # apply the equation with given dependencies, using a lambda to quickly evaluate all freqs
                self.variables[var]=l(*deps) # have to unpack the dependencies list
        else:
            print(f"Variable {var} has no equation")
    # convert circuit to ascii art
    def get_ascii_art(self,max=10):
        formatter=ticker.EngFormatter(places=2,sep="")
        s=["" for i in range(7)]
        s[0]=" "*12
        s[6]=" "*12
        if self.terms.thevenin:
            for idx,line in enumerate(icons["thevenin"]):
                s[idx+1]+=line
        else:
            for idx,line in enumerate(icons["norton"]):
                s[idx+1]+=line
        count=0
        for node in self.components:
            for idx,component in enumerate(node):
                count+=1
                t=component.Type
                if t=="G":
                    t="R"
                width=len(icons[t][component.shunt][0])

                n=component.node
                if component.shunt:
                    s[0]+=f"{n}".center(width)
                else:
                    s[0]+=f"{n}".ljust(width)
                s[6]+=formatter(component.value).center(width)

                for idx,line in enumerate(icons[t][component.shunt]):
                    s[idx+1]+=line
                if count==max:
                    break
            if count==max:
                break
        if count==max:
            for idx,line in enumerate(icons["elipsis"]):
                s[idx+1]+=line
        for idx,line in enumerate(icons["load"]):
            s[idx+1]+=line
        
        return "\n".join(s)
    # string representing the circuit object
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
            f"    First components (up to {depth}): {components_string}",
            f"    First combined ABCD:",
            f"        [{self.variables[A][0]} {self.variables[B][0]}]",
            f"        [{self.variables[C][0]} {self.variables[D][0]}]",
            
        ]
        return '\n'.join(string)