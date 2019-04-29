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

	def __init__(self, ins_id, vns_free):
		#TODO arrumar o conf.
		self.actual_path = path.dirname(path.abspath("__file__"))
		self.rtime = None
		self.optimal_method = "Leilao"
		self.vns_free = vns_free
		if self.vns_free:
			self.optimal_method += " VNS"
		self.end_time_active = 'true'
		if ins_id != 'static':
			self.static = False
			self.ins = Instancia('{}.json'.format(ins_id))
		else:
			self.static = True
			self.ins = Instancia('00_00_000.json')
		self.res = Resultado(self.ins, self.optimal_method)
		with open(path.join(self.actual_path, 'auction\\tmp\\data.csv'), 'w') as file:
			file.close()


	def begin(self):
		if not self.static:
			req = self.ins.get_req()
			static_data = self.ins.get_static_data()

			jcm_text = ''''''
			jcm_text += 'mas auction { \n\n\t'
			agent_data = dict()
			agent_data['instances'] = static_data['number_of_vehicles']
			agent_data['x'] = self.ins.deposito_x
			agent_data['y'] = self.ins.deposito_y
			if self.vns_free:
				agent_data['vns_free'] = 'vns_free'
			else:
				agent_data['vns_free'] = 'vns_block'
			jcm_text += '''
			agent driver_: driver.asl {{
				instances: {instances}
				beliefs: schedule([["client_000",0,0,{x},{y},"drop"]])
				goals: {vns_free}
				focus: tools.queue
				\n}} \n\t'''.format(**agent_data)
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
					 queue_number({}),
					 active({})
			focus: tools.queue
		}}\n\n\t'''.format(2000,len(req)+1,self.end_time_active)
			jcm_text += 'workspace tools { artifact queue: tools.Queue() \n}\n\n\t'
			jcm_text += 'asl-path: auction/src/agt,src/agt\n\n'
			jcm_text += '}'

			with open(path.join(self.actual_path,'auction/auction.jcm'), 'w') as file:
				file.write(jcm_text)
				file.close()
		
		args = 'java '
		args += '-classpath %JACAMO_HOME%/libs/*;auction/bin/classes jacamo.infra.RunJaCaMoProject '
		args += '{}/auction/auction.jcm'.format(self.actual_path)
		check_call(args.split(' '), shell = True)

	def result(self):
		def distance_between(event0, event1):
			x0 = event0[3]
			y0 = event0[4]
			x1 = event1[3]
			y1 = event1[4]
			return np.sqrt(np.power(x0-x1,2)+np.power(y0-y1,2))

		if not self.static:
			try:			
				df = pd.read_csv(path.join(self.actual_path, 'auction\\tmp\\data.csv'), sep = ';', header = None)
			except pd.errors.EmptyDataError:
				print "Instancia infactivel"
				self.res.reset_data_DB()
			else:
				w_times = np.array([])
				t_times = np.array([])
				traveled_distance = 0
				for _, serie in df.iterrows():
					if serie[0] == 'end_time':
						self.rtime = float(serie[1])
					else:
					    client_list = list()
					    Sch = literal_eval(serie[1])
					    for index, event in enumerate(Sch):
					    	if index > 0:
					    		traveled_distance += distance_between(event, Sch[index-1])
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
					    traveled_distance += distance_between(Sch[-1],["client_000",0,0,0,0])
				print "-"*50
				print traveled_distance
				print np.sum(w_times)
				print np.sum(t_times)
				obj = 0.33*traveled_distance + 0.33*np.sum(w_times) + 0.33*np.sum(t_times)
				self.res.result_data_DB_leilao_global(self.rtime, obj, w_times.mean(), w_times.std(), t_times.mean(), t_times.std(), traveled_distance)