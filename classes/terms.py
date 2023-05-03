import sys
import numpy as np
from numpy import linspace,logspace,log10
# from math import log10

# def find_and_cast_float(item,dict,throw=True):


class Terms:
    # thevenin=True
    # VS=None
    # ZS=None
    # ZL=None
    # freqs=None
    # logarithmic=False

    def __init__(self,terms_dict):
        # Get source and load resistance
        if "RS" in terms_dict:
            self.ZS=float(terms_dict["RS"])
        elif "GS" in terms_dict:
            self.ZS=1/float(terms_dict["GS"])
        else:
            raise AttributeError("Missing source resistance RS or GS in TERMS")
        if "RL" in terms_dict:
            self.ZL=float(terms_dict["RL"])
        elif "GL" in terms_dict:
            self.ZL=1/float(terms_dict["GL"])
        else:
            raise AttributeError("Missing load resistance RL or GL in TERMS")
        
        # Get source voltage (converting if norton source)
        self.thevenin="VT" in terms_dict
        if self.thevenin:
            # print("Thevenin")
            self.VS=float(terms_dict["VT"])
        else:
            if "IN" in terms_dict:
                # print("Norton")
                # #TODO add norton logic
                # sys.exit()
                IN=float(terms_dict["IN"])
                self.VS=IN*self.ZS
            else:
                raise AttributeError("Could not find Thevenin or Norton source in TERMS")
        # TODO use unified functions to check presence in dict, cast and throw errors if required
        
        # Find frequency range
        if "Nfreqs" in terms_dict:
            if "Fstart" in terms_dict:
                self.logarithmic=False
                start=float(terms_dict["Fstart"])
                if "Fend" in terms_dict:
                    end=float(terms_dict["Fend"])
                    self.freqs=linspace(start,end,int(float(terms_dict["Nfreqs"])))
                else:
                    raise AttributeError("Fend not found in TERMS")
            elif "LFstart" in terms_dict:
                self.logarithmic=True
                start=log10(float(terms_dict["LFstart"]))
                if "LFend" in terms_dict:
                    end=log10(float(terms_dict["LFend"]))
                    self.freqs=logspace(start,end,int(float(terms_dict["Nfreqs"])))
                else:
                    raise AttributeError("LFend not found in TERMS")
            else:
                raise AttributeError("LFend not found in TERMS")
        else:
            raise AttributeError("Nfreqs not found in TERMS")
    def __str__(self):
        floats=""
        for f in self.freqs:
            floats+='%.2E' % f + ", "
        string=[
            "Terms object:",
            f"    Thevenin: {self.thevenin}",
            f"    Logarithmic: {self.logarithmic}",
            f"    VS: {self.VS} V",
            f"    ZS: {self.ZS} Ohms",
            f"    ZL: {self.ZL} Ohms",
            f"    Nfreqs: {len(self.freqs)}",
            f"    Range: {self.freqs[0]}Hz to {self.freqs[-1]}Hz ",
        ]
        return '\n'.join(string)