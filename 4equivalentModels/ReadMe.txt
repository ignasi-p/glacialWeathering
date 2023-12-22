This folder contains four input Phreeqc files with equivalent
models of the chemical weathering at Kangerlussuaq, as described
in the parent folder.

The four models are:
 - Q = 0 (ratio Calcite / DIC) and R = 0 (ratio Gypsum / SO4).
   In this model all carbon originates from dissolved CO2, and
   all sulfur (SO4) originates from the oxidation of sulfides.
 - Q = 0.5 and R = 0
   In this model 50% of the carbon originates from dissolved CO2, and
   the other half from calcite.
   All sulfur (SO4) originates from the oxidation of sulfides.
 - Q = 0.5 and R = 0
   In this model all carbon originates from dissolved CO2, and
   50% of the sulfur (SO4) originates from the dissolution of gypsum
   while the other half of the sulfate originates from the
   oxidation of sulfides.
 - Q = 0.4 and R = 0.4
   In this model 40% of the carbon originates from dissolved CO2, and
   the rest from calcite.  40% of the sulfur (SO4) originates from
   the dissolution of gypsum while the rest of the sulfate originates
   from the oxidation of sulfides.

The four Phreeqc input files are named 'Kangerlussuaq_Q=0_R=0.pqi' etc.

A short python script is used to create the tsv-files plotted by Phreeqc.
The file 'user_graphs.pqi' is inserted at run-time in each of the
four Phreeqc input files.