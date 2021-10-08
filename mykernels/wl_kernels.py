from parcels import rng as random
import math

def AdvectionRK4Beached(particle, fieldset, time):
    """
    RK4 kernel that takes into account beached particles. It is assumed that particle.beached = 0 means
    that the particle is at the ocean and we should do normal RK4
    :param particle:
    :param fieldset:
    :param time:
    :return:
    """
    if particle.beached == 0:
        (u1, v1) = fieldset.UV[time, particle.depth, particle.lat, particle.lon]
        lon1, lat1 = (particle.lon + u1*.5*particle.dt, particle.lat + v1*.5*particle.dt)

        (u2, v2) = fieldset.UV[time + .5 * particle.dt, particle.depth, lat1, lon1]
        lon2, lat2 = (particle.lon + u2*.5*particle.dt, particle.lat + v2*.5*particle.dt)

        (u3, v3) = fieldset.UV[time + .5 * particle.dt, particle.depth, lat2, lon2]
        lon3, lat3 = (particle.lon + u3*particle.dt, particle.lat + v3*particle.dt)

        (u4, v4) = fieldset.UV[time + particle.dt, particle.depth, lat3, lon3]
        particle.lon += (u1 + 2*u2 + 2*u3 + u4) / 6. * particle.dt
        particle.lat += (v1 + 2*v2 + 2*v3 + v4) / 6. * particle.dt
        particle.beached = 1

def AdvectionRK4COAPS(particle, fieldset, time):
    """Advection of particles using fourth-order Runge-Kutta integration.
        Function needs to be converted to Kernel object before execution"""
    (u1, v1) = fieldset.UV[particle]
    lon1, lat1 = (particle.lon + u1*.5*particle.dt, particle.lat + v1*.5*particle.dt)
    (u2, v2) = fieldset.UV[time + .5 * particle.dt, particle.depth, lat1, lon1, particle]
    lon2, lat2 = (particle.lon + u2*.5*particle.dt, particle.lat + v2*.5*particle.dt)
    (u3, v3) = fieldset.UV[time + .5 * particle.dt, particle.depth, lat2, lon2, particle]
    lon3, lat3 = (particle.lon + u3*particle.dt, particle.lat + v3*particle.dt)
    (u4, v4) = fieldset.UV[time + particle.dt, particle.depth, lat3, lon3, particle]
    particle.lon += (u1 + 2*u2 + 2*u3 + u4) / 6. * particle.dt
    particle.lat += (v1 + 2*v2 + 2*v3 + v4) / 6. * particle.dt


def BrownianMotion2D(particle, fieldset, time):
    """Kernel for simple Brownian particle diffusion in zonal and meridional direction.
    Assumes that fieldset has fields Kh_zonal and Kh_meridional"""
    r = 1 / 3.
    kh_meridional = fieldset.Kh_meridional[time, particle.depth, particle.lat, particle.lon]
    particle.lat += random.uniform(-1., 1.) * math.sqrt(2 * math.fabs(particle.dt) * kh_meridional / r)
    kh_zonal = fieldset.Kh_zonal[time, particle.depth, particle.lat, particle.lon]
    particle.lon += random.uniform(-1., 1.) * math.sqrt(2 * math.fabs(particle.dt) * kh_zonal / r)