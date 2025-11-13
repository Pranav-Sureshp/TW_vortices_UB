#!/bin/bash
# Source the OpenFOAM profile

ulimit -s unlimited

cores=32
solver=epotFoam_isoTh #epotFoam_isoTh  # cEpotmhdEpotMultiRegionFoam
source ~/.openfoam_v2206_profile
#blockMesh   2>&1 | tee log.blockMesh_fluid
#blockMesh -region walls  2>&1 | tee log.blockMesh_walls

if [[ ! $cores -eq 1 ]]
then
#  decomposePar -latestTime  2>&1 | tee log.decomposePar
  mpirun -np $cores $solver -parallel  2>&1 | tee log.$solver
#  reconstructPar -latestTime 2>&1 | tee log.reconstructPar
else
        $solver 2>&1 | tee log.$solver
fi

