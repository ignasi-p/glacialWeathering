# -*- coding: utf-8 -*-
"""
Creates tsv-files containing field data from Kangerlussuaq, Greenland.
These files can then be plotted in Phreeqc 'USER_GRAPH'
and the data compared with model results.
Created on Thu Dec 21 09:28:03 2023

@author: Ignasi Puigdomenech
"""
import pandas as pd

# the experimental data
dta=pd.read_csv('../Kangerlussuaq_Data.csv',sep=',',encoding='ANSI',decimal='.')
#print(dta.head())
supraBasal = dta[(dta['Water Type']==3) | (dta['Water Type']==4)]
glOutlets = dta[dta['Water Type']==5]
streams = dta[(dta['Water Type']>=6) & (dta['Water Type']<7)]
lakes = dta[(dta['Water Type']>=7) & (dta['Water Type']<8)]
sandurPW = dta[dta['Water Type']==8.3]
morainePW = dta[dta['Water Type']==8.1]
del dta

def doit(strx,stry,elx,ely):
    sb2 = supraBasal[[strx,stry]].rename(columns={strx:elx,stry:"supraBasal-"+ely})
    #print(f"sb2=\n{sb2.head()}")

    g2 = glOutlets[[strx,stry]].rename(columns={strx:elx,stry:"glOutlets-"+ely})
    g2.insert(1,"supraBasal-"+ely,'')
    #print(f"g2=\n{g2.head()}")

    s2 = streams[[strx,stry]].rename(columns={strx:elx,stry:"streams-"+ely})
    s2.insert(1,"supraBasal-"+ely,'')
    s2.insert(2,"glOutlets-"+ely,'')
    #print(f"s2=\n{s2.head()}")

    l2 = lakes[[strx,stry]].rename(columns={strx:elx,stry:"lakes-"+ely})
    l2.insert(1,"supraBasal-"+ely,'')
    l2.insert(2,"glOutlets-"+ely,'')
    l2.insert(3,"streams-"+ely,'')
    #print(f"l2=\n{l2.head()}")

    spw2 = sandurPW[[strx,stry]].rename(columns={strx:elx,stry:"sandurPW-"+ely})
    spw2.insert(1,"supraBasal-"+ely,'')
    spw2.insert(2,"glOutlets-"+ely,'')
    spw2.insert(3,"streams-"+ely,'')
    spw2.insert(4,"lakes-"+ely,'')
    #print(f"spw2=\n{spw2.head()}")

    mpw2 = morainePW[[strx,stry]].rename(columns={strx:elx,stry:"morainePW-"+ely})
    mpw2.insert(1,"supraBasal-"+ely,'')
    mpw2.insert(2,"glOutlets-"+ely,'')
    mpw2.insert(3,"streams-"+ely,'')
    mpw2.insert(4,"lakes-"+ely,'')
    mpw2.insert(5,"sandurPW-"+ely,'')
    #print(f"mpw2=\n{mpw2.head()}")

    res = pd.concat([sb2,g2,s2,l2,spw2,mpw2],ignore_index=True, sort=False)
    #print(f"res=\n{res.head()}")
    
    #See other colors at:
    #https://learn.microsoft.com/en-us/previous-versions/windows/desktop/windows-media-center-sdk/bb189018%28v=msdn.10%29
    res.loc[-3] = ["color","LimeGreen","Orange","Gold","Blue","CornflowerBlue","Black"]
    res.loc[-2] = ["symbol","TriangleDown","Diamond","Star","Triangle","Circle","Square"]
    res.loc[-1] = ["symbol_size","9","10","6","9","9","8"]
    res.index = res.index + 3  # shifting index
    res = res.sort_index()
    #print(f"res=\n{res.head()}")
    
    return res


# ----- create the SO4-Ca tsv-file to plot in PhreeqC
strx = "SO4* (umol/l)"; stry = "Ca* (umol/l)"
elx = "SO4"; ely = "Ca"
tot = doit(strx,stry,elx,ely)
tot.to_csv('SO4-Ca.tsv',sep='\t',index=False)

# ----- create the SO4-Alk tsv-file to plot in PhreeqC
strx = "SO4* (ueq/l)"; stry = "Alk* ueq/L"
elx = "SO4"; ely = "Alk"
tot = doit(strx,stry,elx,ely)
tot.to_csv('SO4-Alk.tsv',sep='\t',index=False)

# ----- create the Mg+Ca-Na+K tsv-file to plot in PhreeqC
strx = "Ca*+Mg* (ueq/l)"; stry = "Na*+K* (umol/l)"
elx = "Mg+Ca"; ely = "Na+K"
tot = doit(strx,stry,elx,ely)
tot.to_csv('Mg+Ca-Na+K.tsv',sep='\t',index=False)

# ----- create the Alk-logPCO2 tsv-file to plot in PhreeqC
strx = "Alk* ueq/L"; stry = "log PCO2*"
elx = "Alk"; ely = "lgPCO2"
tot = doit(strx,stry,elx,ely)
tot.to_csv('Alk-logPCO2.tsv',sep='\t',index=False)
