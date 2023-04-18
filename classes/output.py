import numpy as np
import csv
from sympy import arg,Abs,im,re,nan
from classes.circuit import Circuit
from classes.terms import Terms
from classes.prefixes import prefixes


CSV_LINE_WIDTH=11

class Column:
    real=None
    unit=None
    prefix=None
    decibel=None
    values=[]
    def __init__(self,real:bool,unit:str,prefix:str,decibel:bool,values:list):
        self.real=real
        self.unit=unit
        self.prefix=prefix
        self.decibel=decibel
        self.values=values
        if decibel:
            if not real:
                self.unit="Rads"
                self.prefix=None
        
    def __str__(self):
        string=[
            f"      Real: {self.real}\n",
            f"      Unit: {self.unit}\n",
            f"      Prefix: {self.prefix}\n",
            f"      Decibel: {self.decibel}\n",
            # f"    Values: {self.values}"
        ]
        return ''.join(string)
    def full_unit(self):
        full=""
        if self.decibel and self.real:
            full+="dB"
        if not self.prefix is None:
            full+=self.prefix
        if not self.unit is None:
            full+=self.unit
        return full




class Output:
    results={}
    circuit=None
    terms=None
    # Constructor
    def __init__(self,output_dict,circuit,terms):
        self.circuit=circuit
        self.terms=terms
        # Store frequency column first
        self.results["Freq"]=[Column(None,"Hz",None,False,terms.freqs)]
        for var,unit in output_dict.items():

            dB=False
            prefix=None
            # check for and remove dB modifier
            if not unit is None:
                # print(unit)
                if not unit is None and "dB" in unit:
                    dB=True
                    unit=unit.replace("dB","")
                if not len(unit)==0:
                    # check for and remove prefixes
                    if unit[0] in prefixes:
                        prefix=unit[0]
                        unit=unit[1:] # remove prefix
                else:
                    unit=None

            self.results[var]=[
                Column(True,unit,prefix,dB,[0 for i in range(len(terms.freqs))]),
                Column(False,unit,prefix,dB,[0 for i in range(len(terms.freqs))])
            ]
            
    # Calculate all output variables and store them
    def calc_variables(self):
        for var,columns in self.results.items():
            if var!="Freq":
                values=self.circuit.calc_output(var)
                for idx,val in enumerate(values):
                    for column in columns:
                        if column.real:
                            if column.decibel:
                                try:
                                    res=10*np.log10(Abs(res))
                                except:
                                    res=nan
                            else:
                                res=re(val)
                                if not (column.prefix is None or res is None):
                                    res/=prefixes[column.prefix]
                        else:
                            if column.decibel:
                                res=arg(res)
                            else:
                                res=im(val)
                                if not (column.prefix is None or res is None):
                                    res/=prefixes[column.prefix]
                        column.values[idx]=res
    def calc_variables2(self):
        for var,columns in self.results.items():
            if var!="Freq":
                values=self.circuit.calc_output3(var)
                for idx,val in enumerate(values):
                    for column in columns:
                        if column.real:
                            if column.decibel:
                                try:
                                    res=10*np.log10(np.abs(val))
                                except:
                                    res=np.nan
                            else:
                                res=np.real(val)
                                if (column.prefix in prefixes):
                                    res/=prefixes[column.prefix]
                        else:
                            if column.decibel:
                                res=np.angle(val)
                            else:
                                res=np.imag(val)
                                if (column.prefix in prefixes):
                                    res/=prefixes[column.prefix]
                        column.values[idx]=res

    def save_csv(self,path):
        with open(path+".csv","w") as f:
            
            writer = csv.writer(f,lineterminator="\n")
            vars=[]
            units=[]
            values=[[] for i in range(len(self.results["Freq"][0].values))]
            for var,columns in self.results.items():
                for column in columns:
                    if column.real is None:
                        vars.append(var.rjust(CSV_LINE_WIDTH))
                    else:
                        if column.real:
                            if column.decibel:
                                vars.append(f"|{var}|".rjust(CSV_LINE_WIDTH))
                            else:
                                vars.append(f"Re({var})".rjust(CSV_LINE_WIDTH))
                        else:
                            if column.decibel:
                                vars.append(f"/_{var}".rjust(CSV_LINE_WIDTH))
                            else:
                                vars.append(f"Im({var})".rjust(CSV_LINE_WIDTH))
                    units.append(column.full_unit().rjust(CSV_LINE_WIDTH))
                    for idx,val in enumerate(column.values):
                        if val is None:
                            values[idx].append("None".rjust(CSV_LINE_WIDTH))
                        else:
                            values[idx].append(('%.3e' % val).rjust(CSV_LINE_WIDTH))
            # print(vars)
            writer.writerow(vars)
            # print(units)
            writer.writerow(units)
            # print(values[0])
            for row in values:
                writer.writerow(row)



                
    def __str__(self):
        results_string=""
        for var,columns in self.results.items():
            for column in columns:
                results_string+="\n        "+var+"\n   "
                col_strings=str(column).splitlines(keepends=True)
                results_string+='   '.join(col_strings)
        string=[
            "Output object:",
            f"    Results:{results_string}",
        ]
        return '\n'.join(string)
