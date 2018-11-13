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
		self.actual_path = path.dirname(path.abspath("__file__"))
		if ins_id != 'static':
			self.ins = Instancia('{}.json'.format(ins_id))
			self.static = False
		else:
			self.static = True


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
			jcm_text += 'workspace tools { artifact queue: tools.Queue() \n}\n\n\t'
			jcm_text += 'asl-path: auction/src/agt,src/agt\n\n'
			jcm_text += '}'

			with open(path.join(self.actual_path,'auction/auction.jcm'), 'w') as file:
				file.write(jcm_text)
				file.close()
		
		args = 'java '
		args += '-classpath %JACAMO_HOME%/libs/*;auction/bin/classes jacamo.infra.JaCaMoLauncher '
		args += '{}/auction/auction.jcm'.format(self.actual_path)
		check_call(args.split(' '), shell = True)
