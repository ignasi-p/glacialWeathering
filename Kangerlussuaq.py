"""
Forward reaction-path model of chemical weathering using
[PHREEQC](https://www.usgs.gov/software/phreeqc-version-3) --
see Charlton and Parkhurst (2011) http://dx.doi.org/10.1016/j.cageo.2011.02.005

includes plotting of model results with the literature water compositions
from Kangerlussuaq, Greenland.
"""
from time import time
from win32com.client import Dispatch
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import math

# -------------------------------------------------------------
# Set values for the following two parameters and run the script
# to verify that the results are the same, whatever the values are.
# If you get the error: Epidote is less than zero, then
# decrease either Q or R (or both).
# -------------------------------------------------------------
Q = 0.1  # ratio Calcite / DIC
R = 0.3  # ratio Gypsum /SO4
# -------------------------------------------------------------

if Q < 0 or R < 0:
    raise ValueError("Neither Q nor R may be less than zero!")

# -------------------------------------------------------------
# Forward reaction-path model for weathering reactions
# at Kangerlussuaq.
# Model parameters:
#    (these ratios are estimated from the compositional trends of
#    the waters being modeled, in this case reported in the liteature)
Sum_Cat_eqv_2_DIC = 3.182
SO4_2_DIC = 1.093
Alk_2_DIC = 0.87
MgCa_2_NaK = 5.35
Ca_2_Mg = 6.03
Na_2_K = 1.00
DIC_2_NaK = 3.68
SO4_2_NaK = 4.02
DIC_2_Mg = 4.83
SO4_2_Mg = 5.28

# -------------------------------------------------------------
def get_selected_output(db_path, input_string):
    """Load database via linked library object and run input string.
    The results (selected_output) are in a "tuple" of tuples.
    """
    phreeqc = Dispatch('IPhreeqcCOM.Object')
    phreeqc.LoadDatabase(db_path)
    phreeqc.RunString(input_string)
    return phreeqc.GetSelectedOutputArray()
# -------------------------------------------------------------
def check_minerals():
    if Calcite < 0:
        test_print()
        raise ValueError("Calcite is less than zero!")
    if Gypsum < 0:
        test_print()
        raise ValueError("Gypsum is less than zero!")
    if Plagioclase < 0:
        test_print()
        raise ValueError("Plagioclase is less than zero!")
    if Hornblende < 0:
        test_print()
        raise ValueError("Hornblende is less than zero!")
    if Orthoclase < 0:
        test_print()
        raise ValueError("K-feldspar is less than zero!")
    if Epidote < 0:
        test_print()
        raise ValueError("Epidote is less than zero!")
    if CO2 < 0:
        test_print()
        raise ValueError("CO2 is less than zero!")
    if Pyrite < 0:
        test_print()
        raise ValueError("Pyrite is less than zero!")
# -------------------------------------------------------------
def test_print():
    print("--- Parameters used in the model:")
    print("Q="+str(Q)+"; R="+str(R))
    print("X="+str(X)+"; Z="+str(Z))
    print("H_mins="+str(H_mins))
    print("H_tot="+str(H_tot))
    print("H_sil="+str(H_sil))
    print("MgCa_2_NaK_sil="+str(MgCa_2_NaK_sil))
    print("Ca_2_Mg_sil="+str(Ca_2_Mg_sil))
    print("Na_2_K="+str(Na_2_K))
    print("H_MgCa_sil="+str(H_MgCa_sil))
    print("H_NaK_sil="+str(H_NaK_sil))
    print("H_Mg_sil="+str(H_Mg_sil))
    print("H_Ca_sil="+str(H_Ca_sil))
    print("H_Na_sil="+str(H_Na_sil))
    print("H_K_sil="+str(H_K_sil))
    txt = "%10.6f" % Calcite ; print("Calcite = "+txt.strip())
    txt = "%10.6f" % Gypsum ; print("Gypsum = "+txt.strip())
    txt = "%10.6f" % Plagioclase ; print("Plagioclase = "+txt.strip())
    txt = "%10.6f" % Hornblende ; print("Hornblende = "+txt.strip())
    txt = "%10.6f" % Orthoclase ; print("Orthoclase = "+txt.strip())
    txt = "%10.6f" % Epidote ; print("Epidote = "+txt.strip())
    txt = "%10.6f" % CO2 ; print("CO2 = "+txt.strip())
    txt = "%10.6f" % Pyrite ; print("Pyrite = "+txt.strip())
    txt = "%10.6f" % O2 ; print("O2 = "+txt.strip())
#------------------------------------------------------
#
# X = the silicate to carbonate H+ consumption ratio.
# 		= (∑Cat*/DIC*) − 2  − 2 (SO4*/DIC*) ( R / Q )
if Q == 0 :
    X = float("NaN")
else:
    X =  (Sum_Cat_eqv_2_DIC/Q) - 2.0 - 2.0 * SO4_2_DIC * (R / Q)
# Z = CO2 / H2SO4, the molar ratio of carbon dioxide to sulfuric acid
#     = (1/(SO4*/DIC*)) (1 − Q) / (1  − R)
Z = (1/SO4_2_DIC) * (1-Q)/(1-R)
# (MgCa/NaK)_sil = the molar ratio of (Ca+Mg)-silicates to
#                       (Na+K)-silicates weathered by acid
#                = (MgCa/NaK)* − Q (DIC*/NaK*) − R (SO4*/NaK*)
MgCa_2_NaK_sil = MgCa_2_NaK - Q * DIC_2_NaK - R * SO4_2_NaK
# (Ca/Mg)_sil = the ratio of Ca to Mg silicate weathered by acid.
#             = (Ca/Mg)* − Q (DIC*/Mg*) − R (SO4*/Mg*)
Ca_2_Mg_sil = Ca_2_Mg - (Q * DIC_2_Mg) - R * SO4_2_Mg

# ---- it does not matter what value is used for `Sum_Cat_eqv`
#      all amounts of minerals and CO2+O2 reacting are relative
#      to this value
Sum_Cat_eqv = 1 # = ∑Cat*
# H_mins = the amount of acid consumed by minerals for a given value of ∑Cat*
#        = ∑Cat* ( 1 − (Q/(∑Cat*/DIC*))− 2 R (SO4*/DIC*) / (∑Cat*/DIC*) )
H_mins = Sum_Cat_eqv * ( 1 - (Q/Sum_Cat_eqv_2_DIC) \
            - (2 * R * SO4_2_DIC / Sum_Cat_eqv_2_DIC) )
# H_tot = the total amount of acid added within the model for a given value of ∑Cat*
#      = H_mins + ∑Cat* ( 1 − (Alk*/DIC*) ) / (∑Cat*/DIC*)
H_tot = H_mins + Sum_Cat_eqv * ( 1 - Alk_2_DIC ) / Sum_Cat_eqv_2_DIC
# H_sil = Acid used by silicates = H_mins (X / (1+X))
if math.isnan(X) :
    H_sil = H_mins
else:
    H_sil = H_mins * (X / (1+X))
# H_MgCa_sil = Acid used by Mg+Ca silicates
#            = 2 H_sil (MgCa/NaK)_sil / (1 + 2 (MgCa/NaK)_sil)
H_MgCa_sil = 2 * H_sil * MgCa_2_NaK_sil / (1 + 2 * MgCa_2_NaK_sil)
# H_NaK_sil = Acid used by Na+K silicates
#           = H_sil / (1 + 2 (MgCa/NaK)_sil)
H_NaK_sil = H_sil / (1 + 2 * MgCa_2_NaK_sil)
# H_Mg_sil = Acid used by Mg silicates
#          = H_MgCa_sil / (1+(Ca/Mg)_sil)
H_Mg_sil = H_MgCa_sil / (1+Ca_2_Mg_sil)
H_Ca_sil = H_MgCa_sil * Ca_2_Mg_sil / (1+Ca_2_Mg_sil)
H_Na_sil = H_NaK_sil * Na_2_K / (1+Na_2_K)
H_K_sil  = H_NaK_sil / (1+Na_2_K)

if math.isnan(X) :
    Calcite = 0
else:
    Calcite = H_mins * (1-(X/(1+X)))
Gypsum = (H_tot / (2+Z)) * (R / (1-R))
Plagioclase = H_Na_sil / 0.75
Hornblende = 0.5 * H_Mg_sil / 1.8
Orthoclase = H_K_sil - (0.3 * Hornblende)
Epidote = (1/2) * (0.5 * H_Ca_sil - 0.25 * Plagioclase - 1.75 * Hornblende)
CO2 = H_tot * Z / (2+Z)
Pyrite = (1/2) * H_tot / (2+Z)
O2 = 3.75 * Pyrite + 0.275 * Hornblende
check_minerals()

test_print()

# Write Phreeqc input
input_string_top = """
TITLE .
      ----
      **** Waters in Kangerlussuaq (Greenland) ****
      Forward model (using 'REACTION') of the increase of solutes
      from meltwater to stream (for example).
      Minerals, O2 and CO2 react to increase the concentrations of solutes.
      ----

KNOBS
     -pe_step_size      2
     -step_size     2
     -iterations        200
     -diagonal_scale            true

# In the REACTION simulation CO2 is added, and it reacts with
# carbonate minerals to produce extra dissolved carbon (HCO3-).
# By adding a tracer "C_", it is possible to keep track of
# the original amount of CO2 added in the REACTION.
# The tracer "Carb_" is set equal to the amount of
# calcite dissolved in the REACTION.
SOLUTION_MASTER_SPECIES
    C_  C_  0   C_  12.011
    Carb_   Carb_   0   Carb_   12.011
SOLUTION_SPECIES
C_  = C_
    log_k   0
Carb_  = Carb_
    log_k   0
H2O + .01e- = H2O-0.01
      log_k -9

PHASES
Chalcedony
    SiO2 + 2H2O = H4SiO4
    log_k   -3.87
     -delta_H   4.72    kcal
     -analytic  -0.09   0.0     -1032.0         0.0     0.0
K-feldspar      #from sit.dat
    KAlSi3O8 + 8 H2O = K+ + Al(OH)4- + 3 H4SiO4
    -log_k  -20.573
    -delta_h 30.820 kcal
Ferrihydrite            #from ThermodDemV:  Ferrihydrite(6L)
    Fe(OH)3 + 3 H+ = Fe+3 + 3 H2O
    log_k       3.003
    delta_h 22.692      #kJ/mol     #04maj/nav
     -analytic  -4.8289219E+2  -7.376669E-2  2.8192532E+4  1.7273543E+2  -1.2526874E+6
Epidote
    Ca2Al2Fe(SiO4)3OH + 4 H+ + 8 H2O = 2 Ca+2 + Fe(OH)3 + 2 Al(OH)3 + 3 H4SiO4
    log_k   0   #used only in "REACTION", log_k not needed
Hornblende
    (Ca1.75K0.3)(Mg1.8Fe2.8Al0.4)(Al1.9Si6.1)O22(OH)2 + 7.4 H+ + 0.275 O2 + 15.15 H2O = 0.3 K+ + 1.75 Ca+2 + 1.8 Mg+2 + 2.8 Fe(OH)3 + 2.3 Al(OH)3 + 6.1 H4SiO4
    log_k   0   #used only in "REACTION", log_k not needed


# skip most of the stuff in the output file
PRINT ;  -saturation_indices  false ;  -species false

SOLUTION 1 ==== "Pure" water
    temp        5
    pH      7   charge
    pe      13
    redox       pe
    units       umol/kgw
    C(4)        1.00E-15
    C_      1.00E-15
    Na      1.00E-15
    K       1.00E-15
    Mg      1.00E-15
    Ca      1.00E-15
    Fe      1.00E-15
    S(6)        1.00E-15
    Al      1.00E-15
    Si      1.00E-15
    density     1
    -water      1   # kg
EQUILIBRIUM_PHASES
    Ferrihydrite        0   0.1
SAVE solution 1
END

TITLE ==== Add acids and minerals
USER_PUNCH 1
 -headings      TDS_mg/L    Na(umol/L)  K(umol/L)   Ca(ueq/L)   Mg(ueq/L)   SO4(ueq/L)  Alk(ueq/L)  C_alk(ueq/L)    DIC(umol/L) Na+K_umol/L Ca+Mg_ueq/L M_ueq/L Acid_ueq/L  (C_)_ueq/L  Si_umol/L   CO2_umol/L  (Alk+SO4)_ueq/L (DIC+SO4)_ueq/L C.weath_umol/L  Ca+Mg-SO4_umol/L    Ca+Mg-Alk_ueq/L Ca+Mg/Na+K(eq)
 -start
 10 main_c = TOT("K")*39.1+TOT("Na")*22.99+TOT("Ca")*40.08+TOT("Mg")*24.31
 15 other_c = TOT("Si")*60.08+TOT("Fe")*55.85
 20 main_a = TOT("Cl")*35.45+TOT("S(6)")*96.06+TOT("C(4)")*60.01
 30 x = MOL("H+")*1.0079+MOL("OH-")*17.01
 35 tds = x + main_c + other_c + main_a
 40 PUNCH 1000*tds
100 PUNCH TOT("Na")*10^6
110 PUNCH TOT("K")*10^6
120 PUNCH 2*TOT("Ca")*10^6
130 PUNCH 2*TOT("Mg")*10^6
140 PUNCH 2*TOT("S(6)")*10^6
150 PUNCH ALK*10^6
155 C_alk = MOL("HCO3-") +MOL("CaHCO3+") +MOL("MgHCO3+") +MOL("NaHCO3") +2*(MOL("CO3-2") +MOL("CaCO3") +MOL("MgCO3"))
156 PUNCH C_alk*10^6
160 PUNCH TOT("C(4)")*10^6
170 PUNCH (TOT("Na")+TOT("K"))*10^6
180 PUNCH 2*(TOT("Ca")+TOT("Mg"))*10^6
190 PUNCH (TOT("Na")+TOT("K")+2*(TOT("Ca")+TOT("Mg")))*10^6
200 PUNCH (TOT("C_")+2*TOT("S(6)"))*10^6
210 PUNCH TOT("C_")*10^6
220 PUNCH TOT("Si")*10^6
230 PUNCH MOL("CO2")*10^6
240 PUNCH (ALK+2*TOT("S(6)"))*10^6
250 PUNCH (TOT("C(4)")+2*TOT("S(6)"))*10^6
260 PUNCH TOT("Carb_")*10^6
270 PUNCH (TOT("Ca")+TOT("Mg")-TOT("S(6)"))*10^6
280 PUNCH (2*(TOT("Ca")+TOT("Mg"))-ALK)*10^6
290 PUNCH (2*(TOT("Ca")+TOT("Mg"))/(TOT("Na")+TOT("K")))
 -end
SELECTED_OUTPUT 1
    #-file          Kangerlussuaq_res.txt
    -high_precision         false
    -reset          true
    -simulation         false
    -state          false
    -distance           false
    -time           false
    -step           false
    -water          false
    -charge_balance         false
    -totals         Alkalinity  C(4)  Na  K  Ca  Al  Si  S(6)
    -saturation_indices         Calcite  Gypsum  CO2(g)  Anorthite
            Albite  K-feldspar  Kaolinite
    -user_punch         true
SELECTED_OUTPUT 1
    -active  true

USE solution 1
EQUILIBRIUM_PHASES 1  Solids that may precipitate
    O2(g)       -0.677780705    1
    Calcite     0   0
    Kaolinite       0   0
    Chalcedony      0   0
#    K-feldspar     0   0
    Gypsum      0   0
    Ferrihydrite            0   0
REACTION 1 Add acids and minerals
"""

# these are the relative amounts of minerals and CO2+O2 added in the reaction
input_string_mid = ""
txt = "%15.8f" % (2*Pyrite) ; input_string_mid = input_string_mid + "#  H2SO4  " + txt + "\n"
txt = "%15.8f" % Pyrite ; input_string_mid = input_string_mid +     "   Pyrite " + txt + "  #  FeS2 + 3.75 O2 + 3.5 H2O = Fe(OH)3 + 2 SO4-2 + 4 H+\n"
txt = "%15.8f" % O2 ; input_string_mid = input_string_mid +         "   O2(g)  " + txt + "\n"
txt = "%15.8f" % CO2 ; input_string_mid = input_string_mid +        "   CO2    " + txt + "\n"
txt = "%15.8f" % CO2 ; input_string_mid = input_string_mid +        "   C_     " + txt + "\n"
txt = "%15.8f" % Plagioclase ; input_string_mid = input_string_mid +"   Na0.75Ca0.25Al1.25Si2.75O8  " + txt + "\n"
txt = "%15.8f" % Hornblende ; input_string_mid = input_string_mid + "   Hornblende   " + txt + "\n"
txt = "%15.8f" % Orthoclase ; input_string_mid = input_string_mid + "   KAlSi3O8     " + txt + "\n"
txt = "%15.8f" % Epidote ; input_string_mid = input_string_mid +    "   Epidote      " + txt + "\n"
txt = "%15.8f" % Calcite ; input_string_mid = input_string_mid +    "   Calcite      " + txt + "\n"
txt = "%15.8f" % Calcite ; input_string_mid = input_string_mid +    "   Carb_        " + txt + "\n"
txt = "%15.8f" % Gypsum ; input_string_mid = input_string_mid +     "   CaSO4        " + txt + "\n"

print("--- REACTION input to Phreeqc:")
print(input_string_mid)

# these are the REACTION amounts. Because the waters have very low TDS,
# a few millimoles are enough
input_string_bottom = """
0   0.02    0.05    0.1 0.2 0.3 0.4 0.5 0.6 0.8 1   \\
    1.5 2   2.25    2.5 2.75    3   3.25    3.5 3.75    4   \\
    4.25    4.5 4.75    5   5.25    5.5 5.75    6   6.25    6.5 \\
    6.75    7   8   9   10  11  12  14  16 18 20 25 30        \\
    millimoles
END
"""

t1 = time()

# Set up the input for Phreeqc
input_string = input_string_top + input_string_mid + input_string_bottom

# Save the input file in case you want to run PhreeqC outside Python
pqi = 'Kangerlussuaq.pqi'
f = open(pqi,'w')
f.writelines(input_string)
f.close()

# Get the results (do the calculation) - The results (selected_output) are in a "tuple" of tuples
result = get_selected_output('wateq4f.dat', input_string)
# Get results from the tuples into Python lists
# The column numbers and headings are:
# 0    1  2    3       4    5   6    7        8       9   10 11 12 13 14  15     16         17        18        19           20        21            22         23       24         25        26        27         28         29          30          31          32           33        34       35         36         37       38             39              40            41             42              43                44
# soln pH pe reaction temp Alk mu pct_err Alkalinity C(4) Na K  Ca Al Si S(6) si_Calcite si_Gypsum si_CO2(g) si_Anorthite si_Albite si_K-feldspar si_Kaolinite TDS_mg/L Na(umol/L) K(umol/L) Ca(ueq/L) Mg(ueq/L) SO4(ueq/L) Alk(ueq/L) C_alk(ueq/L) DIC(umol/L) Na+K_umol/L Ca+Mg_ueq/L M_ueq/L Acid_ueq/L (C_)_ueq/L Si_umol/L CO2_umol/L (Alk+SO4)_ueq/L (DIC+SO4)_ueq/L C.weath_umol/L Ca+Mg-SO4_umol/L Ca+Mg-Alk_ueq/L Ca+Mg/Na+K(eq)
pH_calc = [column[1] for column in result][1:]
SO4eq_calc  = [column[28] for column in result][1:]
Caeq_calc = [elem[26] for elem in result][1:]
Alk_calc = [column[29] for column in result][1:]
DIC_calc = [column[31] for column in result][1:]
NaK_calc = [elem[32] for elem in result][1:]
MgCa_calc = [elem[33] for elem in result][1:]
Sum_cat_calc = [column[34] for column in result][1:]
Si_calc = [column[37] for column in result][1:]
SO4Alk_calc = [column[39] for column in result][1:]
CaMg_SO4_calc = [column[42] for column in result][1:]
calcite_calc = [elem[16] for elem in result][1:]
gypsum_calc = [elem[17] for elem in result][1:]
lgPCO2_calc = [elem[18] for elem in result][1:]
# convert micro equivalents to micro mols
SO4_calc = [0.5 * i for i in SO4eq_calc]
Ca_calc = [0.5 * i for i in Caeq_calc]
zero_x = [0,5000]
zero_y = [0,0]

# the experimental data
dta=pd.read_csv('Kangerlussuaq_Data.csv',sep=',',encoding='ANSI',decimal='.')
#print(dta.head())
streams = dta[(dta['Water Type']>=6) & (dta['Water Type']<7)]
lakes = dta[(dta['Water Type']>=7) & (dta['Water Type']<8)]
glOutlets = dta[dta['Water Type']==5]
supraBasal = dta[(dta['Water Type']==3) | (dta['Water Type']==4)]
sandurPW = dta[dta['Water Type']==8.3]
morainePW = dta[dta['Water Type']==8.1]
del dta

# Plot:

def plotit (ax,colx,coly,legend=False):
    """
    Plots into a matplotlib axes (ax) experimental data
    in pandas DataFrames in the columns colx and coly
    """
    # markers: see the Notes section in
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
    # The following colors are based on https://www.nature.com/articles/nmeth.1618
    # see python named colors in
    # https://matplotlib.org/stable/gallery/color/named_colors.html#sphx-glr-gallery-color-named-colors-py
    if legend :
        ax.scatter(supraBasal[colx],supraBasal[coly],c="#009E73",marker="v",zorder=6,label="Supra & basal meltwaters") # bluish green, v = triangle down
        ax.scatter(glOutlets[colx],glOutlets[coly],c="#E69F00",marker="D",zorder=5,label="Glacier outlets") # orange, D = diamond
        ax.scatter(streams[colx],streams[coly],c="#F0E442",marker="o",zorder=4,label="Glacial streams") # yellow
        ax.scatter(lakes[colx],lakes[coly],c="#0072B2",marker="^",zorder=3,label="Glacial lakes and ponds") # blue, ^ = triangle up
        ax.scatter(sandurPW[colx],sandurPW[coly],c='#56B4E9',marker="o", zorder=2,label="Sandur porewaters") # Sky blue
        ax.plot(morainePW[colx],morainePW[coly],"ks",zorder=1,label="Moraine porewaters") # k = black, s = square
    else :
        ax.scatter(supraBasal[colx],supraBasal[coly],c="#009E73",marker="v",zorder=6) # bluish green, v = triangle down
        ax.scatter(glOutlets[colx],glOutlets[coly],c="#E69F00",marker="D",zorder=5) # orange, D = diamond
        ax.scatter(streams[colx],streams[coly],c="#F0E442",marker="o",zorder=4) # yellow
        ax.scatter(lakes[colx],lakes[coly],c="#0072B2",marker="^",zorder=3) # blue, ^ = triangle up
        ax.scatter(sandurPW[colx],sandurPW[coly],c='#56B4E9',marker="o", zorder=2) # Sky blue
        ax.plot(morainePW[colx],morainePW[coly],"ks",zorder=1) # k = black, s = square
    return
    
# Create a figure containing two rows and two columns.
fig, axs=plt.subplots(2,2,layout='constrained',figsize=(5.12,3.84),dpi=100) # two columns and two rows

axs[0,0].plot(SO4_calc, Ca_calc, 'k',zorder=7)
strx = "SO4* (umol/l)"; stry = "Ca* (umol/l)"
plotit(axs[0,0],strx,stry,legend=True)
axs[0,0].axis([0, 1500, 0, 1500])
axs[0,0].set_xlabel('SO4* ($\mu$mol/kg$\mathsf{_{H_2O}}$)')
axs[0,0].set_ylabel('Ca* ($\mu$mol/kg$\mathsf{_{H_2O}}$)')

axs[0,1].set_xscale("log"); axs[0,1].set_yscale("log")
axs[0,1].xaxis.set_major_locator(ticker.LogLocator(numticks=999))
axs[0,1].xaxis.set_minor_locator(ticker.LogLocator(numticks=999, subs="auto"))
axs[0,1].plot(MgCa_calc, NaK_calc, 'k',zorder=7)
strx = "Ca*+Mg* (ueq/l)"; stry = "Na*+K* (umol/l)"
plotit(axs[0,1],strx,stry)
axs[0,1].axis([1, 10000, 1, 1000])
axs[0,1].set_xlabel('(Mg+Ca)* ($\mu$eq/kg$\mathsf{_{H_2O}}$)')
axs[0,1].set_ylabel('(Na+K)* ($\mu$mol/kg$\mathsf{_{H_2O}}$)')

axs[1,0].plot(SO4eq_calc, Alk_calc, 'k',zorder=7)
strx = "SO4* (ueq/l)"; stry = "Alk* ueq/L"
plotit(axs[1,0],strx,stry)
axs[1,0].axis([0, 3000, 0, 3000])
axs[1,0].set_xlabel('SO4* ($\mu$eq/kg$\mathsf{_{H_2O}}$)')
axs[1,0].set_ylabel('Alk* ($\mu$eq/kg$\mathsf{_{H_2O}}$)')

fig.legend(fontsize='small', bbox_to_anchor=(0.6,0.12), loc='lower left', borderaxespad=0)

axs[1,1].axis('off')

plt.savefig("images\\model_fig_1.png")
plt.show()

# Create another figure containing two rows and two columns.
fig, ax=plt.subplots(2,2,layout='constrained',figsize=(5.12,3.84),dpi=100) # two columns and two rows

ax[0,0].plot(SO4Alk_calc, Sum_cat_calc, 'k',zorder=7) # 'k' = black
strx = "(HCO3+SO4)* ueq/L"; stry = "SumCat* ueq/L"
plotit(ax[0,0],strx,stry)
ax[0,0].axis([0, 5000, 0, 5000])
ax[0,0].set_xlabel('(SO4+Alk)* ($\mu$eq/kg$\mathsf{_{H_2O}}$)')
ax[0,0].set_ylabel('$\sum$Cat* ($\mu$eq/kg$\mathsf{_{H_2O}}$)')

ax[0,1].set_yscale("log")
ax[0,1].plot(Sum_cat_calc, Si_calc, 'k',zorder=7)
strx = "SumCat* ueq/L"; stry = "Si (umol/l)"
plotit(ax[0,1],strx,stry)
ax[0,1].axis([0, 5000, 0.1, 1000])
ax[0,1].set_xlabel('$\sum$Cat* ($\mu$eq/kg$\mathsf{_{H_2O}}$)')
ax[0,1].set_ylabel('Silicon ($\mu$mol/kg$\mathsf{_{H_2O}}$)')

ax[1,0].plot(Alk_calc, pH_calc, 'k',zorder=7) # 'k' = black
strx = "Alk* ueq/L"; stry = "pH"
plotit(ax[1,0],strx,stry)
ax[1,0].axis([0, 3000, 5, 10])
ax[1,0].set_xlabel('Alk* ($\mu$eq/kg$\mathsf{_{H_2O}}$)')
ax[1,0].set_ylabel('pH')

ax[1,1].plot(Alk_calc, DIC_calc, 'k',zorder=7) # 'k' = black
strx = "Alk* ueq/L"; stry = "DICexp* umol/L"
plotit(ax[1,1],strx,stry)
ax[1,1].axis([0, 4000, 0, 4000])
ax[1,1].set_xlabel('Alk* ($\mu$eq/kg$\mathsf{_{H_2O}}$)')
ax[1,1].set_ylabel('DIC*$_{exp}$ ($\mu$mol/kg$\mathsf{_{H_2O}}$)')

plt.savefig("images\\model_fig_2.png")
plt.show()

# Create another figure containing two rows and two columns.
fig, ax=plt.subplots(2,2,layout='constrained',figsize=(5.12,3.84),dpi=100) # two columns and two rows

ax[0,0].plot(Alk_calc, lgPCO2_calc, 'k',zorder=7) # 'k' = black
strx = "Alk* ueq/L"; stry = "log PCO2*"
plotit(ax[0,0],strx,stry)
ax[0,0].axis([0, 3000, -7, -1])
ax[0,0].set_xlabel('Alk* ($\mu$eq/kg$\mathsf{_{H_2O}}$)')
ax[0,0].set_ylabel('log $P\mathsf{_{CO_2}}$')

ax[0,1].plot(Sum_cat_calc, calcite_calc, 'k', zero_x,zero_y,'k--',zorder=7)
strx = "SumCat* ueq/L"; stry = "Calcite*"
plotit(ax[0,1],strx,stry)
ax[0,1].axis([0, 5000, -8, 1])
ax[0,1].set_xlabel('$\sum$Cat* ($\mu$eq/kg$\mathsf{_{H_2O}}$)')
ax[0,1].set_ylabel('SI(calcite)')

ax[1,0].yaxis.set_major_locator(ticker.MultipleLocator(2))
ax[1,0].plot(SO4_calc, gypsum_calc, 'k', zero_x,zero_y,'k--',zorder=7)
strx = "SO4* (umol/l)"; stry = "Gypsum*"
plotit(ax[1,0],strx,stry)
ax[1,0].axis([0, 1500, -8, 1])
ax[1,0].set_xlabel('SO4* ($\mu$mol/kg$\mathsf{_{H_2O}}$)')
ax[1,0].set_ylabel('SI(gypsum)')

ax[1,1].remove()

plt.savefig("images\\model_fig_3.png")
plt.show()

t2 = time() - t1
print('Operations completed after %5.3f seconds' % t2)
