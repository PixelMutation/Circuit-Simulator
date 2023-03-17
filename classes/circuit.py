import numpy as np
from collections import deque

c_types=[
    "R",
    "L",
    "C",
    "G"
]

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
        for t in c_types:
            if t in component_dict:
                self.Type=t
                self.value=float(component_dict[t])
        # Convert conductance to resistance 
        if self.Type=="G":
            self.Type="R"
            self.value=1/self.value
    def calc_impedance(self):
        #TODO calculate impedance
        print("calc impedance")
    def calc_matrix(self):
        #TODO calculate matrix
        print("calc single ABCD")
    

# class Node:
#     series=None
#     shunt=[]


class Circuit:
    components=[]
    terms=None
    ABCD=None
    def __init__(self,circuit_list,terms):
        self.terms = terms
        # Create empty circuit, assuming each component is series
        self.components=deque()*len(circuit_list)
        num_nodes=0
        # For each dictionary from CIRCUIT in .net file
        for component_dict in circuit_list:
            # Create component from dictionary
            component = Component(component_dict)
            if component.node>num_nodes:
                num_nodes=component.node
            # Place component in shunt or series based on n2
            if component.shunt:
                self.components[component.node].appendleft(component)
            else:
                self.components[component.node].append(component)
        # Remove extra nodes
        self.components=self.components[:num_nodes]
    def calc_matrix(self):
        # Calculate individual ABCD matrices
        for i,node in enumerate(self.components):
            for j,component in enumerate(node):
                component.calc_impedance()
                component.calc_matrix()
                # if first component, set overall ABCD to component ABCD
                if i==0 and j==0:
                    self.ABCD=component.ABCD
                # otherwise, multiply overall ABCD by component ABCD
                else:
                    self.ABCD=self.ABCD*component.ABCD
    def evaluate(expression,freqs):
        