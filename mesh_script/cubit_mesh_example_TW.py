import sys
sys.path.append('/home/pranav/softwares/Coreform-Cubit-2025.8+61943-Lin64/Coreform-Cubit-2025.8/bin')
import cubit
sys.path.append("/home/pranav/repos/nekrs_grid_design/nekrs_mhd_examples/python")

### User Settings ###

# Set exodus file names
# meshname_fluid = "fluid"
# meshname_solid = "solid"

# Set reference length for nondimensionalisation
# Applied after mesh generation
ref_length = 1.0

# Set geometry parameters
# Note on orientation:
# u_in=(0,0,u_in)
# B_0=(B_0,0,0)

a = 1.0     # duct interior half-size in direction parallel to B
b = 1.0     # duct interior half-size in direction perpendicular to B
d = 8*3.14      # duct length
t_w = 0/1000    # duct wall thickness

L_z_fluid = 2*a
L_y_fluid = 2*b
L_x_fluid = d


# Set mesh parameters as for a low-order mesh

delta_zy_core = 6.621177e-02 ; #1.730737e-04
delta_x_axial = 3.500000e-01 ;

fluid_hart_first_row = 1.000000e-03
fluid_hart_growth_factor = 1.15
fluid_hart_num_layers = 31
fluid_side_first_row = 1.000000e-03
fluid_side_growth_factor = 1.15
fluid_side_num_layers = 31

### Generate Geometry ###

cubit.cmd(f'brick x {L_x_fluid} y {L_y_fluid} z {L_z_fluid}') # fluid region

# Imprint and merge
cubit.cmd('compress') # minimise all ID numbers

# Note, at this point:
# Centroid is at (0,0,0)
# Volume 1   = fluid region
# Surface 4  = fluid inlet
# Surface 6  = fluid outlet
# Surface 3  = y=-b fluid-solid interface (side wall)
# Surface 2  = z=-a fluid-solid interface (Hartmann wall)
# Surface 5  = y=+b fluid-solid interface (side wall)
# Surface 1  = z=+a fluid-solid interface (Hartmann wall)

### Create named sidesets ###

# create named sidesets

cubit.cmd('sideset 1 add surface 4')
cubit.cmd('sideset 1 name "fluid_inlet"')
cubit.cmd('sideset 2 add surface 6')
cubit.cmd('sideset 2 name "fluid_outlet"')

cubit.cmd('sideset 3 add surface 3 5') # fluid-solid interface
cubit.cmd('sideset 3 name "side_wall"')
cubit.cmd('sideset 4 add surface 1 2') # fluid-solid interface
cubit.cmd('sideset 4 name "hartmann_wall"')


#cubit.cmd('sideset 4 add surface 7 8 9 10')
#cubit.cmd('sideset 4 name "exterior"')
#cubit.cmd('sideset 5 add surface 12')
#cubit.cmd('sideset 5 name "solid_inlet"')
#cubit.cmd('sideset 6 add surface 11')
#cubit.cmd('sideset 6 name "solid_outlet"')

### Set up boundary layers ###

# Create Hartmann layer in fluid region
cubit.cmd('create boundary_layer 1')
cubit.cmd(f'modify boundary_layer 1 uniform height {fluid_hart_first_row} growth {fluid_hart_growth_factor} layers {fluid_hart_num_layers}')
cubit.cmd('modify boundary_layer 1 add surface 1 volume 1 surface 2 volume 1') 
cubit.cmd('modify boundary_layer 1 continuity off')

# walls 1 and 2 are Hartmann layers, 3 & 5 are side layers


# Create side layer in fluid region
cubit.cmd('create boundary_layer 2')
cubit.cmd(f'modify boundary_layer 2 uniform height {fluid_side_first_row} growth {fluid_side_growth_factor} layers {fluid_side_num_layers}')
cubit.cmd('modify boundary_layer 2 add surface 3 volume 1 surface 5 volume 1')
cubit.cmd('modify boundary_layer 2 continuity off')

### Generate Mesh ###

# Set mesh size for axial resolution (on all volumes)

cubit.cmd(f'volume 1  size {delta_x_axial}')

# Set approximate mesh size for fluid core (on inlet surface)

cubit.cmd(f'surface 4 6 size {delta_zy_core}')


# Mesh fluid inlet

cubit.cmd('surface 4 submap smooth off')
cubit.cmd('surface 4 scheme submap')
cubit.cmd('mesh surface 4')



# Sweep mesh through volume

cubit.cmd('volume 1 redistribute nodes off')
cubit.cmd('volume 1 scheme Sweep source surface 4 target surface 6 sweep transform least squares')
cubit.cmd('volume 1 autosmooth target on fixed imprints off smart smooth off')
cubit.cmd('mesh volume 1')

# create element blocks
cubit.cmd('block 1 add volume 1')

# set element type
#cubit.cmd('block 1 element type hex20')
#cubit.cmd('block 2 element type hex20')

# cubit cmd
cubit.cmd('block 1 name "fluid"')

# assign Mesh block region
cubit.cmd('create media')
cubit.cmd('modify media 1 name "fluid" ')
cubit.cmd('block 1 media "fluid" ')

# cubit assigns wall BC to sideset 3
# cubit assigns periodic BC to sideset 1,2

cubit.cmd('create cfd_bc Periodic  on sideset 1')
cubit.cmd('create cfd_bc Periodic  on sideset 2')
cubit.cmd('create cfd_bc Wall  on sideset 3')
cubit.cmd('create cfd_bc Wall  on sideset 4')

### Save mesh (exodus) ###

cubit.cmd('set exodus netcdf4 off')
#cubit.cmd('set large exodus file on')

cubit.cmd('export fluent "./rect_mesh_TW.msh"  overwrite  everything consolidate')
