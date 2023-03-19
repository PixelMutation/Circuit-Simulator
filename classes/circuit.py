import numpy as np
import sys
import math
from collections import deque
from sympy import *

from classes.terms import Terms


A,B,C,D,ZS,ZL,w=symbols("A,B,C,D,ZS,ZL,w")
j=Symbol("j",real=False)

class Component:
    node=None
    shunt=None
    Type=None
    value=None
    Z=None
    ABCD=None
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
                self.value=float(component_dict[t])
                break
        # Convert conductance to resistance 
        if self.Type=="G":
            self.Type="R"
            self.value=1/self.value
    def calc_impedance(self):
        if self.Type=="R":
            self.Z=self.value
        elif self.Type=="L":
            self.Z=j*w*self.value
        else:
            self.Z=-(j/(w*self.value))
    def calc_matrix(self):
        if self.shunt:
            Y=1/self.Z
            self.ABCD=Matrix([
                [1,0],
                [Y,1]
            ])
        else:
            Z=self.Z
            self.ABCD=Matrix([
                [1,Z],
                [0,1]
            ])
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

equations={
    "Vin":nan,
    "Vout":nan,
    "Iin":nan,
    "Iout":nan,
    "Zin":(A*ZL+B)/(C*ZL+D),
    "Zout":(D*ZS+B)/(C*ZS+A),
    "Pin":nan,
    "Pout":nan,
    "Av":ZL/(A*ZL+B),
    "Ai":1/(C*ZL+D),
}

class Circuit:
    num_components=0
    components=None
    terms=None
    ABCD=None
    def __init__(self,circuit_list,terms):
        self.terms = terms
        # Create empty circuit, assuming each component is series
        self.components=[deque() for i in range(len(circuit_list))]
        # print(self.components)
        # print(len(self.components))
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
    def calc_matrix(self):
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
    def evaluate(self,expression,freqs):
        results=[]
        for f in enumerate(freqs):
            results.append(expression.subs(w,f))
        return results

    def calc_output(self,var):
        print(f"Calc {var}")
        print(self.ABCD)
        if var in equations:
            print(equations[var])
            expr = equations[var]
            expr = expr.subs(A,self.ABCD[0])
            expr = expr.subs(B,self.ABCD[1])
            expr = expr.subs(C,self.ABCD[2])
            expr = expr.subs(D,self.ABCD[3])
            expr = expr.subs(ZS,self.terms.ZS)
            expr = expr.subs(ZL,self.terms.ZL)
            print(expr)
            return self.evaluate(expr,self.terms.freqs)

        return []
    def __str__(self):
        components_string=""
        for node in self.components:
            for component in node:
                # components_string+="\n        "+var+"\n   "
                col_strings=str(component).splitlines(keepends=True)
                components_string+='        '.join(col_strings)
        string=[
            "Circuit object:",
            f"    ABCD: {self.ABCD}",
            f"    Components: {components_string}",
            
        ]
        return '\n'.join(string)