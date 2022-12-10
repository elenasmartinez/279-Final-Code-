import gromacs 

#1hz3 from PDB bank
gmx pdb2gmx -f 1hz3.pdb -ignh -o 1hz3_processed.gro -water tip3p
#when prompted for force field select number 15, OPLSAA

#create a cubic box with 1.0 nm 
gmx editconf -f 1hz3_processed.gro -o 1hz3_newbox.gro -c -d 1.0 -bt cubic

#Add solvent to box 
gmx solvate -cp 1hz3_newbox.gro -cs spc216.gro -o 1hz3_solv.gro -p topol.top
gmx grompp -f ions.mdp -c 1hz3_solv.gro -p topol.top -o ions.tpr

# add positive ion to neutralize system
gmx genion -s ions.tpr -o 1hz3_solv_ions.gro -p topol.top -pname NA \
-nname CL -np 1
#when prompted select 13 for "SOLVENT" 

#Energy minimization
gmx grompp -f minim.mdp -c 1hz3_solv_ions.gro -p topol.top -o em.tpr
gmx mdrun -v -deffnm em

# generate graph of potential energy 
gmx energy -f em.edr -o potential.xvg
#when prompted select 10 for "potential energy"

# temperature equilibrium 
gmx grompp -f nvt.mdp -c em.gro -p topol.top -o nvt.tpr
gmx mdrun -deffnm nvt
gmx energy -f nvt.edr -o temperature.xvg
#when prompted select 15 for "temperature"

# pressure equilibrium
gmx grompp -f npt.mdp -c nvt.gro -t nvt.cpt -p topol.top -o npt.tpr
gmx mdrun -nt 4 -deffnm npt
gmx energy -f npt.edr -o pressure.xvg
#when prompted select 17 for "pressure"

# density equilibrium
gmx energy -f npt.edr -o density.xvg
#when prompted select 23 for "density"

# run MD simulation
gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr
gmx mdrun -nt 4 -deffnm md

# convert gro to pdb file of system 
gmx editconf -f md.gro -o md.pdb

# analysis of RMSD 
gmx trjconv -s md.tpr -f md.xtc -o md_noPBC.xtc -pbc mol \
-ur compact
gmx rms -s md.tpr -f md_noPBC.xtc -o rmsd.xvg -tu ns
gmx rms -s em.tpr -f md_noPBC.xtc -o rmsd_xtal.xvg -tu ns

# analysis of radius of gyration 
gmx gyrate -s md.tpr -f md_noPBC.xtc -o gyrate.xvg
