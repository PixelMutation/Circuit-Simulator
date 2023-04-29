import numpy as np
import csv
import sys
from sympy import arg,Abs,im,re,nan
from classes.circuit import Circuit
from classes.terms import Terms
from classes.prefixes import prefixes
from classes.variables import var_table,Freq


CSV_LINE_WIDTH=11

# Column class stores values and unit information for a variable
class Column:
    index=None  # Index of column in output CSV
    real=None   # Whether the column contains real or imaginary values
    unit=None   # The unit of those values (V,A,W,Ohms...)
    prefix=None # SI prefix of the unit
    decibel=None    # Whether values are in a dB scale
    values=[]       # The actual values in that column

    # Constructor
    def __init__(self,name,index,real:bool,unit:str,prefix:str,decibel:bool):
        self.index=index
        self.name=name
        self.real=real
        self.unit=unit
        self.prefix=prefix
        self.decibel=decibel
        # The imaginary component of a dB value is given in Rads
        if decibel:
            if not real:
                self.unit="Rads"
                self.prefix=None
    
    # Converts the raw values for the settings of that column (apply prefixes, dB, split into Im and Re etc.)
    def convert_raw(self,raw_values):
        # If real is None, then it is the frequency column so don't change anything
        if self.real is None:
            self.values=raw_values
        # Otherwise, convert
        else:
            # If column is real, get real part of value
            if self.real:
                # Convert any dB
                if self.decibel:
                    try:
                        self.values=10*np.log10(np.abs(raw_values))
                    except:
                        self.values=np.nan
                else:
                    self.values=np.real(raw_values)
                    if (self.prefix in prefixes):
                        self.values/=prefixes[self.prefix]
            # If column is imaginary, get imaginary part
            else:
                # Convert any dB
                if self.decibel:
                    self.values=np.angle(raw_values)
                else:
                    self.values=np.imag(raw_values)
                    if (self.prefix in prefixes):
                        self.values/=prefixes[self.prefix]

    # Returns a string of the full unit name for display in the CSV
    def get_full_unit(self):
        full=""
        if self.decibel and self.real:
            full+="dB"
        if not self.prefix is None:
            full+=self.prefix
        if not self.unit is None:
            full+=self.unit
        return full
    
    # Convert name to how it will be displayed in the CSV
    def get_display_name(self):
        if self.real is None:
            return self.name
        else:
            if self.real:
                if self.decibel:
                    return f"|{self.name}|"
                else:
                    return f"Re({self.name})"
            else:
                if self.decibel:
                    return f"/_{self.name}"
                else:
                    return f"Im({self.name})"
    
    # Convert column structure to list of strings
    def get_column_list(self):
        # Create blank rows
        rows=["" for i in range(len(self.values))+2]
        # Add name and unit rows
        rows[0]=self.get_display_name()
        rows[1]=self.get_full_unit()
        # Add value rows
        rows[2:]=str(self.values)
    
    # Returns a string containing the settings of the column
    def __str__(self):
        string=[
            f"      Real: {self.real}\n",
            f"      Unit: {self.unit}\n",
            f"      Prefix: {self.prefix}\n",
            f"      Decibel: {self.decibel}\n",
        ]
        return ''.join(string)

class Output:
    results={}
    circuit=None
    terms=None
    # Constructor
    def __init__(self,output_dict,circuit,terms):
        self.circuit=circuit
        self.terms=terms
        self.output_dict=output_dict
        # Store frequency column
        self.results[Freq]=[Column("Freq",0,None,"Hz",None,False)]
        self.results[Freq][0].values=terms.freqs
        # Now decode other variables and create columns for them
        idx=1
        for var_name,unit in output_dict.items():
            if var_name in var_table:
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
                # Every column after freq has an imaginary and real component thus two columns
                # Use var_table to lookup variable constant using name string
                self.results[var_table[var_name]]=[
                    Column(var_name,idx,True,unit,prefix,dB),
                    Column(var_name,idx+1,False,unit,prefix,dB)
                ]
                idx+=2
            else:
                print(f"Variable {var_name} does not exist")
                sys.exit()

    # Calculate all output variables and store them                       
    def calc_variables(self):
        for var,columns in self.results.items():
            if var != Freq:
                self.circuit.calc_output(var)
    
    # Convert variables to chosen output units and store in dictionary
    def convert_variables(self):
        for var,columns in self.results.items():
            if var != Freq:
                for column in columns:
                    column.convert(self.circuit.variables[var])

    def save_csv(self,path):
        #TODO replace with custom CSV writer
        with open(path+".csv","w") as f:
            # Create empty list of columns
            cols=[]
            # Add each column to create a 2D list
            for var,columns in self.results.items():
                for column in columns:
                    # Convert column object to list of strings
                    cols.append(column.get_column_list())
            # Extract each row from the 2D list
            for idx in range(len(cols[0])):
                # Add space at start of line
                f.write(" ")
                # Extract row
                row=cols[:][idx]
                # Write elements of row, applying right justification
                for element in row:
                    f.write(element.rjust(CSV_LINE_WIDTH))
                f.write("\n")

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
