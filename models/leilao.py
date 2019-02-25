# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 12:31:43 2018

@author: Sergio P.
"""

from instancia import Instancia
from resultado import Resultado
from subprocess import call, check_call
from os import path
from time import clock
import pandas as pd
import numpy as np
from ast import literal_eval

class Leilao:

	def __init__(self, ins_id):
		self.actual_path = path.dirname(path.abspath("__file__"))
		self.rtime = None
		self.optimal_method = 0
		if ins_id != 'static':
			self.static = False
			self.ins = Instancia('{}.json'.format(ins_id))
		else:
			self.static = True
			self.ins = Instancia('00_00_000.json')
		self.res = Resultado(self.ins, self.optimal_method)
		with open(path.join(self.actual_path, 'tmp\\data.csv'), 'w') as file:
			file.close()


	def begin(self):
		if not self.static:
			req = self.ins.get_req()
			static_data = self.ins.get_static_data()

			jcm_text = ''''''
			jcm_text += 'mas auction { \n\n\t'
			jcm_text += 'agent driver_: driver.asl {{ instances: {}\n}} \n\t'.format(static_data['number_of_vehicles'])
			for i, req_data in enumerate(req):
				req_data['queue_number'] = str(i+1)
				req_data['counter'] = str(i+1).zfill(3)
				snippet = '''
		agent client_{counter}: client.asl {{
			beliefs: service_type("{service_type}"),
				     desired_time({desired_time}),
				     known_time({known_time}),
				     service_point_x({service_point_x}),
				     service_point_y({service_point_y}),
				     queue_number({queue_number})
			focus: tools.queue
		}}\n\n\t'''.format(**req_data)
				jcm_text += snippet
			jcm_text += '''
		agent end_time: end_time.asl {{
			beliefs: end_time({}),
					 queue_number({})
			focus: tools.queue
		}}\n\n\t'''.format(2000,len(req)+1)
			jcm_text += 'workspace tools { artifact queue: tools.Queue() \n}\n\n\t'
			jcm_text += 'asl-path: auction/src/agt,src/agt\n\n'
			jcm_text += '}'

			with open(path.join(self.actual_path,'auction/auction.jcm'), 'w') as file:
				file.write(jcm_text)
				file.close()
		
		args = 'java '
		args += '-classpath %JACAMO_HOME%/libs/*;auction/bin/classes jacamo.infra.RunJaCaMoProject '
		args += '{}/auction/auction.jcm'.format(self.actual_path)
		t0 = clock()
		check_call(args.split(' '), shell = True)
		self.rtime = clock() - t0

	def result(self):
		df = pd.read_csv(path.join(self.actual_path, 'auction\\tmp\\data.csv'), sep = ';', header = None)
		w_times = np.array([])
		t_times = np.array([])
		for _, serie in df.iterrows():
		    k = serie[0].split('_')[-1]
		    client_list = list()
		    for event in literal_eval(serie[1]):
		        client = int(event[0].split('_')[-1])
		        if client != 0:
		            if client not in client_list:
		                client_list.append(client)
		                ini_time = event[1]
		                desired_time = event[2]
		            else:
		                end_time = event[1]
		                self.res.result_data_DB_leilao_specific(client, desired_time, ini_time, end_time)
		                w_times = np.append(w_times, ini_time - desired_time)
		                t_times = np.append(t_times, end_time - ini_time)
		self.res.result_data_DB_leilao_global(self.rtime, 0, w_times.mean(), w_times.std(), t_times.mean(), t_times.std())