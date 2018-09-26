# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 12:31:43 2018

@author: Sergio P.
"""

from instancia import Instancia
from subprocess import call, check_call
from os import path

class Leilao:

	def __init__(self, ins_id):
		self.ins = Instancia('{}.json'.format(ins_id))
		self.actual_path = path.dirname(path.abspath("__file__"))

	def begin(self):
		n, m, Q   = self.ins.n, self.ins.m, self.ins.Q
		q, s, t   = self.ins.get_q(), self.ins.get_s(), self.ins.get_t()
		W, R, tau = self.ins.get_W(), self.ins.get_R(), self.ins.get_tau()
		arcos = tau.keys()
		origens, destinos, locais = self.ins.get_O(), self.ins.get_D(), self.ins.get_V()
		veiculos = self.ins.get_K()

		req = self.ins.get_req()
		static_data = self.ins.get_static_data()
		
		args = 'java '
		args += '-classpath %JACAMO_HOME%/libs/* jacamo.infra.RunJaCaMoProject '
		args += '{}/auction/auction.jcm jar'.format(self.actual_path)
		check_call(args.split(' '), shell = True)

		args = 'java -jar {}/auction/jacamo-auction.jar'.format(self.actual_path)
		check_call(args.split(' '), shell = True)
