
import pandas as pd
import networkx as nx

import numpy as np
import matplotlib
#matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from epinetwork.Simulation import simulation
from epinetwork.modelos import SEAIR
from epinetwork.MobilityNetwork import MobilityNetwork
from epinetwork.Control_protocol import controlProtocol
from epinetwork.SimulationsEnsemble import simulationsEnsemble
from epinetwork.Control_protocol import randomControl
import copy
import random

def f(x,n_links):
    y=1./(1.+x)**1.0326
    A=sum(y)
    z=np.rint(((n_links)/A)*y)
    return (x,z)
    #return 40/(1+x)**1.0326  precovid

def g(x,n_links):
    y=1./(1.+x)**0.7905
    A=sum(y)
    z=np.rint(((n_links)/A)*y)
    return (x,z)
    #return 10/(1+x)**0.7905


def distance_matrix(n,d_max):
    # Vectores de los ejes 'x' y 'y'
    X = np.random.randint(d_max, size = n)
    Y = np.random.randint(d_max, size = n)

    # Matriz de ceros
    Z = np.zeros((n,n))

    #Distancias entre todos los puntos
    for i in range(n):
        for j in range(n):
            s = (X[i] - X[j], Y[i] - Y[j])
            d_ij = np.linalg.norm(s)
            Z[i][j] = d_ij

    Z1 = np.triu(Z)

    return Z1

def adjacency_matrixt(n,matrix,d_distribution):
    # Lista de Matrices adyacentes
    adj = np.zeros((n,n))
    bins = d_distribution[0]

    for i in range(len(bins)-1):
        # Índices de los datos que que están el el intervalo [i,i+1)
        condition = ((matrix>=bins[i]) & (matrix<bins[i+1]))
        index = np.array(np.where( condition )).T
        total_index = len(index)


        if (total_index > 0):
            No_distances = int(d_distribution[1][i])
            if (No_distances<total_index):
                for id in random.sample(list(index),No_distances):
                    adj[id[0],id[1]] = 1
            else:
                adj+=condition.astype(int)

    adj+=adj.T

    return adj

def from_geometric_network(nodes,d_distribution):
    d_max=d_distribution[0][-1]
    dist_m = distance_matrix(nodes,d_max)
    adj_mt = adjacency_matrixt(nodes, dist_m, d_distribution)
    return adj_mt


if __name__ == '__main__':
    # Vectores de los ejes x y y
    import time
    n = 100 #patches
    d_max = 10
    #n_links = 50*2.9
    Rel=0.8
    bins = np.arange(0.5,d_max)


    number_of_simulations = 250

    #vector de parametros para una zona
    Ro=(2. + 4.5)/2.

    param = [0]*5

    param[1] = sigma = (0.2 + 0.33)/2.
    param[2] = gamma = (0.055 + 0.2)/2.
    param[3] = m = (0.2 + 0.8)/2.
    param[4] = eta = 0.2
    param[0] = beta = Ro/(1./sigma + (m+(1.-m)*eta)/gamma)
    #initial conditions para una zona
    y = [0]*5
    S = y[0] = 1000.
    E = y[1] = 0.0
    A = y[2] = 0.0
    I = y[3] = 0.0
    R = y[4] = 0.0

    infection_peak_normal=[]
    infection_size_normal=[]
    infection_peak_covid=[]
    infection_size_covid=[]
    n_links = np.arange(30,401,10)
    point4=0.
    for l in n_links:
        y[1] = 0.0
        y[2] = 0.0
        y[3] = 0.0
        y[4] = 0.0
        sim = simulation() #se crea objeto simulacion
        sim.add_many_patches_parameters(n,param)  # se agregan n zonas con parametros dados en param
        sim.set_initial_conditions_all_patches(y)
        y[1]=1. # Se agrega 1 infectado mosquito a las condiciones iniciales
        sim.set_initial_conditions_patch(1,y)
        sim.set_model(SEAIR) #Se establece el modelo para hacer la simulacion
        sim.infected_variable = 3
        sim.recovered_variable = 4
        sim.set_simulation_time(360)
        ensemble = simulationsEnsemble() # se crea el objeto ensamble_de_simulaciones
        ensemble_Covid19 = simulationsEnsemble()
        d_dist_preCovid=f(bins,l)
        d_dist_Covid=g(bins,l*Rel)

        for i in range(number_of_simulations) :
            adj_matrix=from_geometric_network(n,d_dist_preCovid)
            P = MobilityNetwork()
            P.from_adjacency_matrix(adj_matrix, 0.8) #para cada simulacion se genera nueva mobilidad
            sim.set_conectivity_network(P)
            del(P)
            ensemble.add_simulation(sim)
            adj_matrix2=from_geometric_network(n,d_dist_Covid)
            P = MobilityNetwork()
            P.from_adjacency_matrix(adj_matrix2, 0.8) #para cada simulacion se genera nueva mobilidad
            sim.set_conectivity_network(P)
            ensemble_Covid19.add_simulation(sim)

        ensemble.multiprocessing_run_all(8) #12 is the number of processes
        ensemble_Covid19.multiprocessing_run_all(8)

        infection_peak_normal.append(ensemble.calculate_max_infected())
        ensemble.average_suseptible()
        R = ensemble.susceptible_average[0] - ensemble.susceptible_average[-1]
        infection_size_normal.append(R)

        infection_peak_covid.append(ensemble_Covid19.calculate_max_infected())
        ensemble_Covid19.average_suseptible()
        R = ensemble_Covid19.susceptible_average[0] - ensemble_Covid19.susceptible_average[-1]
        infection_size_covid.append(R)
        print("procesado de 300", l)

    np.save('infection_peak_normal',np.array(infection_peak_normal))
    np.save('infection_size_normal',np.array(infection_size_normal))
    np.save('infection_peak_covid',np.array(infection_peak_covid))
    np.save('infection_size_covid',np.array(infection_size_covid))
    np.save('n_links',n_links)

    # axes = ensemble.plot_infected_average()
    # axes.lines[0].set_label('Normal mobility')
    # axes1 = ensemble_Covid19.plot_infected_average(axes)
    # axes1.lines[1].set_label('Stay at home campaing')
    #
    # plt.legend()
    # plt.show()
