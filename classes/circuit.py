import numpy as np
import sys
import math
from collections import deque
from sympy import * #I,Matrix,symbols,subs,nan
from classes.prefixes import prefixes
from classes.terms import Terms
from multiprocessing import Pool


A,B,C,D,ZS,ZL,w,f=symbols("A,B,C,D,ZS,ZL,w,f")
# j=Symbol("j",real=True)

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
    def calc_matrix2(self,freqs):
        if self.shunt:
            for Z in freqs:
                Y=(1/self.Z).subs(w,2*pi*f)
                self.ABCD_arr.append(np.matrix([
                    [1,0],
                    [Y,1]
                ]))
        else:
            for f in freqs:
                Z=self.Z.subs(w,2*pi*f)
                self.ABCD_arr.append(np.matrix([
                    [1,Z],
                    [0,1]
                ]))
    def calc_matrices(self,freqs):
        if self.shunt:
            Y=lambdify(w,(1/self.Z))
            for f in freqs:
                mat=np.mat([
                    [1           ,0],
                    [Y(2*np.pi*f),1]]
                )
                self.ABCDs.append(mat)
            # Y=(1/self.Z).subs(w,2*np.pi*f)
            # func=lambdify(f,[
            #         [1,0],
            #         [Y,1]])
            # self.ABCDs=Pool(processes=4).map(func,freqs)
        else:
            Z=lambdify(w,self.Z)
            for f in freqs:
                mat=np.mat([
                    [1,Z(2*np.pi*f)],
                    [0,           1]]
                )
                self.ABCDs.append(mat)
            # Z=self.Z.subs(w,2*np.pi*f)
            # func=lambdify(f,[
            #         [1,Z],
            #         [0,1]])
            # self.ABCDs=Pool(processes=4).map(func,freqs)
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
    "Ap":nan
}

class Circuit:
    num_components=0
    components=None
    terms=None
    ABCD=None
    ABCDs=[]
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
            else:1
                self.components[component.node-1].append(component)
        # Remove extra nodes
        self.components=self.components[:num_nodes]
    def combine_matrices(self,matrices):
        ABCD=matrices[0]
        for mat in matrices[1:]:
            print(mat)
            ABCD=np.matmul(ABCD,mat)
        print(ABCD)

    def calc_matrices(self):
        # Calculate individual ABCD matrices
        matrices=[]
        for node in self.components:
            for component in node:
                component.calc_impedance()
                component.calc_matrices(self.terms.freqs)
                matrices.append(component.ABCDs)
        matrices=np.asarray(matrices)
        matrices=np.swapaxes(matrices,0,1)
        print(np.shape(matrices))
        # For each frequency, combine the matrices
        # self.ABCDs=Pool(processes=8).map(self.combine_matrices,matrices.tolist())
        self.ABCDs=list(map(self.combine_matrices,matrices))
        print(self.ABCDs[0])
        
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
        for idx,f in enumerate(freqs):
            print(f"{idx}/{len(freqs)}",end="\r")
            result=expression.subs(w,2*np.pi*f)
            # result=result.subs(j,I)
            results.append(result)
        return results
    def evaluate2(self,expression,freqs):
        if expression == nan:
            results=[np.nan for i in range(len(freqs))]
        else:
            freq_array=np.array(freqs)
            func=lambdify(w,expression,'numpy')
            results=func(freq_array)
        return results
    def calc_output(self,var):
        print(f"Calc {var}")
        if var in equations:
            expr = equations[var]
            expr = expr.subs(A,self.ABCD[0])
            expr = expr.subs(B,self.ABCD[1])
            expr = expr.subs(C,self.ABCD[2])
            expr = expr.subs(D,self.ABCD[3])
            expr = expr.subs(ZS,self.terms.ZS)
            expr = expr.subs(ZL,self.terms.ZL)
            return self.evaluate2(expr,self.terms.freqs)
        return []
    def evaluate3(self,expr,ABCD):
        expr = expr.subs(A,ABCD[0])
        expr = expr.subs(B,ABCD[1])
        expr = expr.subs(C,ABCD[2])
        expr = expr.subs(D,ABCD[3])
        expr = expr.subs(ZS,self.terms.ZS)
        expr = expr.subs(ZL,self.terms.ZL)
        return expr
    def calc_output3(self,var):
        print(f"Calc {var}")
        if var in equations:
            res=[]
            for ABCD in self.ABCDs:
                expr = equations[var]
                res.append(self.evaluate3(expr,ABCD))
            return res
        return []
    def calc_output2(self,var):
        print(f"Calc {var}")
        if var in equations:
            expr = equations[var]
            expr = expr.subs(A,self.ABCD[0])
            expr = expr.subs(B,self.ABCD[1])
            expr = expr.subs(C,self.ABCD[2])
            expr = expr.subs(D,self.ABCD[3])
            expr = expr.subs(ZS,self.terms.ZS)
            expr = expr.subs(ZL,self.terms.ZL)
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
            # f"    ABCD: {self.ABCD}",
            f"    Components: {components_string}",
            
        ]
        return '\n'.join(string)