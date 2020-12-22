# PlasmaPy community meeting agenda and minutes

## Tuesday 2019 September 24 at 18:00 UT

### Video Conference Information
* [Jitsi video conference link](https://meet.jit.si/plasmapy) with [call-in information](https://meet.jit.si/static/dialInInfo.html?room=plasmapy) 
* Instant messaging: [Matrix](https://riot.im/app/#/room/#plasmapy:openastronomy.org) and [Gitter](https://gitter.im/PlasmaPy/Lobby)
* [PlasmaPy google directory](https://drive.google.com/drive/folders/0ByPG8nie6fTPMEIxTlZLZjdjYms?usp=sharing) ([minutes/agendas](https://drive.google.com/drive/folders/0ByPG8nie6fTPV1FQUEkzMTgtRTg?usp=sharing), [documents](https://drive.google.com/drive/folders/0ByPG8nie6fTPYzk2TEhTa1N6R0U?usp=sharing))
* [PlasmaPy on GitHub](https://github.com/PlasmaPy/plasmapy) ([pull requests](https://github.com/PlasmaPy/plasmapy/pulls), [issues](https://github.com/PlasmaPy/plasmapy/issues))
* [PlasmaPy Enhancement Proposals on GitHub](https://github.com/PlasmaPy/PlasmaPy-PLEPs)
* [PlasmaPy Google Calendar](https://calendar.google.com/calendar?cid=bzVsb3ZkcW0zaWxsam00ZTlrMDd2cmw5bWdAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ)

## Agenda (please feel free to edit or add items)

* dispersion relation solver needs an API
* distribution functions
* simulation subpackage needs an API (most probable topic for next week)
    * including for ParticleTracker in #675
    * Also classes for initial conditions for a plasma simulation
* initial design for diagnostics (eventually we’ll want a PLEP on it)

## dispersion relation

Use cases:

* space physics: polarizations (ratio of x, z, y) -> magnetic fluctuations
* eigenvectors
* standard $\omega(k)$ relation
* number of species, parameters varies significantly
    * difficult to have single API for all cases
    * different kinetic dispersion and fluid dispersion APIs
        * kinetic dispersion has a `u.t` of parameters
    * single, two fluid params: just a handful
* a file as input?
    * or create a class storing the parameters
    * define species as fluid or kinetic -> expect other
    * one interface

```python
p = Particle('p')

class Species(Particle):
    def __init__(self, particle_name, temperature, anisotropy, density, drift):
        ...
    
custom_ion = CustomParticle(mass=25*electron_mass, charge=2 * constants.e.si)
# for now 
species0 = Species(custom_ion, 
    anisotropy: float = 1/3.1415,
    # or solve for anisotropy from T_perpendicular, T_parallel
    density = 1e23 * u.m**-3,
    # in general, example: drift = [0, 0, 2] * (u.m/u.s), but for now don't worry about direction
    drift = 2 * (u.m/u.s),
)

# physics initialization 
# DispersionSolverPhysicsInput?
# DSPhysicalInputs - less easy to follow
# from plasmapy.dispersion import (PhysicalInputs, DispersionSolver)
# probably the best call here!
dispersion_input = DispersionInput(species = [species0],
    magnetic_field = [0, 0, 5] * u.T, 
    # kwargs:
    wavenumber = np.linspace(0, 10, 1000) / u.m,
    # wavenumber = np.array([0.1, 10, 3,]) / u.m,
    angle = np.linspace(0, np.pi, 1000),
    # v_Alfven/c needs to be controlled - magnetic_field, density give us v
    # what do we need for the relativistic dispersion?
    # Ask Daniel Verscharen and other astrophysicists
    )    

class DispersionSolver:
    solvers = {'kinetic': KineticDispersionSolver,
               'two_fluid': tfst}
    
    def __init__(self, solver_type, **solver_kwargs):
        # doc issues but easy to extend
    

KineticDispersionSolver(dispersion_input,
                 number_of_iterations = 10000,         
                 #Threshold for the determinant of the dispersion tensor:
                 # If det D <= det_D_threshold, the Newton iteration will 
                 # be stopped
                 det_D_threshold,
                 # Maximum of sum in Bessel functions (both regular 
                 # and modified)
                 # can be very low (e.g., 3) for quasi-parallel propagation
                 nmax=1000,
                 # If I_n is less than this value, higher n are neglected:
                 Bessel_zero=1.d-50,
                 # Initial guess for the frequency (complex number):
                 initial_guess=0.01+0.0001j,
                 # Amplitude mode: If 1, then ampl = delta B_x / B0. 
                 # If 2, then ampl = delta B_y / B0.
                 # If 3, then ampl = delta B_z / B0
                 # ampl_mode=3,
                 # Amplitude for the calculation of polarization
                 # properties:
                 # ampl=1.d0
                 amplBETTERNAME = (0, 0, 1)
                 )
                 
FluidDispersionSolver(dispersion_input,
                 )
                 
# def two_fluid_single_theta(beta=0.6, v_Alfven=1., me/mi=0.000545, theta=0., kmin=1e-2, kmax=10., npoints=200,wrt='n')
# c/wpi=1, V_alfven=1, wci=1.
# 
# how to handle multifluid dispersion solvers?
```



```python                
# # alternatively - future work
arch_is_best_distro = DistributionFunction(...,
    anisotropy: function,
    density: function, 
    drift: function, # or get them from innards somehow
    # Maxwellian, Bimaxwellian, Kappa...
)

species1 = Species(custom_ion,
    distribution_function = arch_is_best_distro,
    )

species1 = FluidSpecies('p')
species2 = KineticSpecies('p')

species1 = FluidSpecies('p')
species2 = KineticSpecies('p')

dispersion_input = DispersionInput(species: List[(Particle, temperature)] =...,
magnetic_field=...,)
DispersionSolver(dispersion_input)
```