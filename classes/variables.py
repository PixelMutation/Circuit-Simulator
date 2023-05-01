from sympy import *


# Possible output variables
Vin  = Symbol("Vin"  )
Vout = Symbol("Vout" )
Iin  = Symbol("Iin"  )
Iout = Symbol("Iout" )
Zin  = Symbol("Zin"  )
Zout = Symbol("Zout" )
Pin  = Symbol("Pin"  )
Pout = Symbol("Pout" )
Av   = Symbol("Av"   )
Ai   = Symbol("Ai"   )
Ap   = Symbol("Ap"   ) 
T   = Symbol("T"   ) 

# Frequency variable
Freq   = Symbol("Freq"   ) 

# Table used to convert from strings to symbols
var_table={
    "Freq"  : Freq,
    "Vin"   : Vin,    
    "Vout"  : Vout,  
    "Iin"   : Iin,    
    "Iout"  : Iout,  
    "Zin"   : Zin,    
    "Zout"  : Zout,  
    "Pin"   : Pin,    
    "Pout"  : Pout,  
    "Av"    : Av,      
    "Ai"    : Ai,      
    "Ap"    : Ap, 
    "T"     : T,     
}

# Intermediate variables
A,B,C,D,VS,ZS,ZL=symbols("A,B,C,D,VS,ZS,ZL")
inv_A,inv_B,inv_C,inv_D=symbols("inv_A,inv_B,inv_C,inv_D")

# Sympy equations for each variable, to be converted to lambdas
# This allows any new variable to easily be defined
equations={
    Vin  :   Iin*Zin, # good
    Vout :   Vin*inv_A+Iin*inv_B, # (1/(A*D-B*C))*(Vin*D+Iin*-B),# bad (due to inv_A or inv_B)
    Iin  :   VS/(ZS+Zin), # good
    Iout :   Vin*inv_C+Iin*inv_D, # (1/(A*D-B*C))*(Vin*-C+Iin*A),# bad
    Zin  :   (A*ZL+B)/(C*ZL+D), # good
    Zout :   (D*ZS+B)/(C*ZS+A), # bad (assume ZS wrong?)
    Pin  :   Vin*conjugate(Iin), # good
    Pout :   Vout*conjugate(Iin), # bad (due to Vout)
    Av   :   Vout/Vin,# ZL/(A*ZL+B), # bad
    Ai   :   Iout/Iin,# 1 /(C*ZL+D), # bad
    Ap   :   Av*conjugate(Ai),
    T    :   2/(A*ZL+B+C*ZL*ZS+D*ZS),
}

# Stores the dependencies of each variable that must be calculated first
dependencies={
    Vin     : [Iin,Zin],
    Vout    : [Vin,Iin,inv_A,inv_B],# [A,B,C,D,Vin,Iin],
    Iin     : [VS,ZS,Zin],
    Iout    : [Vin,inv_C,Iin,inv_D],# [A,B,C,D,Vin,Iin],
    Zin     : [A,B,C,D,ZL],
    Zout    : [A,B,C,D,ZS],
    Pin     : [Vin,Iin],
    Pout    : [Vout,Iin],
    Av      : [Vout,Vin], # [A,B,C,ZL],
    Ai      : [Iout,Iin], # [B,C,D,ZL],
    Ap      : [Av,Ai],
    T       : [A,B,C,D,ZS,ZL],
}