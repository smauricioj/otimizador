# -*- coding: utf-8 -*-
"""
Created on Thu May 03 13:27:14 2018

@author: Sergio P.
"""
import matplotlib.pyplot as plt

class Resultado:

	def __init__(self, ins):
		# n, m, Q   = ins.n, ins.m, ins.Q
		# q, s, t   = ins.get_q(), ins.get_s(), ins.get_t()
		# W, R, tau = ins.get_W(), ins.get_R(), ins.get_tau()
		# custo, arcos = tau, tau.keys()    
		# origens, destinos, locais = ins.get_O(), ins.get_D(), ins.get_V()
		# veiculos = ins.get_K()
		data = ins.get_pos_requests()
		fig, ax = plt.subplots()
		for d in data:
			ax.plot(d[1], d[2], fmt = 'bo')

		ax.set_xlim((-5,5))
		ax.set_ylim((-5,5))
		plt.grid(True)
		plt.show()
