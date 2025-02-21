#  MobilityNetwork.py
#
#  Copyright 2018 Jorge Velazquez Castro
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random as rand


class MobilityNetwork:

	def __init__(self):
		self.matrix = None
		self.network = None
		self.adjacency_network = None

	def weight_edges(self, min_residential):
		"""
		Give weights to the edges of the of a networkx network, it also
		adds the corresponding weight to the diagonal in order to
		represent a mobility network where the rows are normalized.
		"""
		Net = self.adjacency_network
		n=nx.number_of_nodes(Net)
		for i in Net.nodes():
			Net.add_edge(i,i)

		for u,v,d in Net.edges(data=True):
			if u == v:
				d['weight']=rand.uniform(min_residential,1)
			else:
				d['weight']=rand.uniform(0,min_residential)

		B=nx.to_numpy_matrix(Net,weight='weight')

		for i in range (0,n):
			suma=0
			for j in range (0,n):
				suma=suma+B[i,j]
			B[i,:]=B[i,:]/suma

		NewNet=nx.from_numpy_matrix(B)

		self.matrix = np.squeeze(np.asarray(B))
		self.network = NewNet

		return B

	def add_nodes_property(self,property,value):
		for node in self.network.nodes():
			self.network.nodes[node][property] = value[node]


	def binomial(self,n,p,min_residential):
		"""
		Se crea un matriz en el cual se muestra la interaccion de los parches

		Parameters
		--------
		n : int
			Numero de nodos en la red
		p : float
			Parametro de la matriz binomial
		min_residential: float
			Minima fraccion de tiempo que los individuos estan en sus propios parches.
			Es decir la diagonal tendra numeros mayores o iguales a este valor

		Returns
		------
		numpy matriz of size : n x n
		"""


		self.adjacency_network=nx.binomial_graph(n,p)
		self.weight_edges( min_residential)

	def barabsi_albert(self,n,m,min_residential):
		"""
		Se crea un matriz en el cual se muestra la interaccion de los
		parches con el algoritmo de Barabasi albert (red de mundo pequeno)

		Parameters
		--------
		n : int
			Numero de nodos en la red
		m : float
			Number of edges to attach from a new node to exiting nodes
		min_residential: float
			Minima fraccion de tiempo que los individuos estan en sus propios parches.
			Es decir la diagonal tendra numeros mayores o iguales a este valor

		Returns
		------
		numpy matriz of size : n x n
		"""

		self.adjacency_network=nx.barabasi_albert_graph(n,m)
		self.weight_edges( min_residential)

	def random(self,n,m,min_residential):

		self.adjacency_network=nx.gnm_random_graph(n,m)
		self.weight_edges( min_residential)

	def from_adjacency_matrix(self,adjacency_m, min_residential):
		if(isinstance(adjacency_m, str)):
			Adj = np.loadtxt(adjacency_m)
		else:
			Adj = adjacency_m
			
		self.adjacency_network=nx.from_numpy_matrix(Adj)
		return self.weight_edges(min_residential)

	def from_netowrkx(self,G):
		self.network = G
		B=nx.to_numpy_matrix(G,weight='weight')
		self.matrix = np.squeeze(np.asarray(B))
		self.adjacency_network = G

	def draw_network(self):
		nx.draw_networkx(self.network)
		plt.show()
