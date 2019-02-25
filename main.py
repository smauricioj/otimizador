# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 13:14:13 2018

@author: Sergio P.
"""

from models.leilao import Leilao
from models.gerador import Gerador
from models.resultado import Resultado
from models.instancia import Instancia
from models.db_manager import Db_manager
from getopt import getopt, GetoptError
from sqlite3 import connect
from sys import argv
from os import listdir, path
from ast import literal_eval

import pandas as pd

if __name__ == "__main__":


    actual_path = path.dirname(path.abspath("__file__"))
    instancia_path = path.join(actual_path,'models\\instancias')
    resultados_path = path.join(actual_path,'resultados')    
    scripts_path = path.join(actual_path,'models\\db_scripts')

    try:
        singles = 'olgrt'
        opts, args = getopt(argv[1:],singles)
    except GetoptError as err:
        print str(err)
        exit()
    opt_list = [opt for opt, opt_args in opts]
    otimizar = '-o' in opt_list
    leiloar = '-l' in opt_list
    gerar = '-g' in opt_list
    resultar = '-r' in opt_list
    tabelar = '-t' in opt_list

    if gerar:
                
        # ################################################### #
        #                                                     #
        # PANIC BUTTON - Caso delete todas as instâncias      #
        #                                                     #
        # q_veh = 4                                           #
        # for cen in range(15):                               #
        #     for n_req in [6, 8, 10, 12, 14]:
        #         ger = Gerador(n_req)           #
        #         ger.set_data(4, q_veh, 1)
        #         ger.save_ins()                         #
        # exit()                                              #
        # ################################################### #

        print "#"*70
        print "#"
        print u"# Iniciando processo de gerar novas instâncias."
        commited_response = False
        while not commited_response:
            data = {}
            print u"# Para cancelar o processo, responda 'S' a qualquer pergunta."
            print ''

            def get_response(data, parameter):
                valid_response = False
                r = None
                while not valid_response:
                    r = raw_input('Qual valor do parametro "{}"? > '.format(parameter))
                    if r == 'S':
                        exit()
                    elif not r.isdigit():
                        print u'Parâmetro inválido'
                    else:
                        valid_response = True
                data[parameter] = int(r)

            parameters = ['q_veh', 'n_veh', 't_ser', 'n_req', 'n_cen']
            for p in parameters:
                get_response(data, p)

            print u"Confirmando dados."
            for k, v in data.iteritems():
                print k, ' -> ', v

            valid_response = False
            while not valid_response:
                r = raw_input('Confirma? (Y/N) > ')
                if r.upper() in ('Y','N'):
                    valid_response = True
                else:
                    print u'Resposta inválida'
            if r == 'Y':
                commited_response = True
            else:
                print u'Reiniciando processo de gerar novas instâncias'

        for cen in range(data['n_cen']):
            ger = Gerador(data['n_req'])
            ger.set_data(data['n_veh'], data['q_veh'], data['t_ser'])
            ger.save_ins()

    if otimizar or leiloar:
        if otimizar:
            from models.otimizador import Otimizador
            text = u"# Iniciando processo de otimizar instâncias."
            input_text = 'Qual instancia(s) otimizar? > '
            def method(ins_id):
                Otimizador(ins_id).begin()
        else:
            from models.leilao import Leilao
            text = u"# Iniciando processo de leiloar instâncias."
            input_text = 'Qual instancia(s) realizar leilao? > '
            def method(ins_id):
                l = Leilao(ins_id)
                l.begin()
                l.result()

        print "#"*70
        print "#"
        print text
        stop = False
        while not stop:
            r = raw_input(input_text)
            if r == 'S':
                stop = True
            elif r.split('/')[0] == 'all':
                for filename in listdir(instancia_path):
                    print filename
                    ins_id = filename.split('.')[0]
                    if int(ins_id.split('_')[0]) == 0:
                        continue
                    try:
                        post_case = r.split('/')[1]
                    except IndexError:
                        post_case = ''
                    if post_case == 'new':
                        if ins_id not in listdir(resultados_path):
                            method(ins_id)
                    else:
                        method(ins_id)
            else:
                method(r)

    if resultar:
        Resultado(Instancia('00_00_000.json')).plot_global_result_data()

    if tabelar:                
        # actual_path = path.dirname(path.abspath("__file__"))
        # scripts_path = path.join(actual_path,'models\\db_scripts')
        # instancia_path = path.join(actual_path,'models\\instancias')

        db_man = Db_manager('persistent_data.db', scripts_path)

        # for row in db_man.execute_script('get_tables.txt'):
        #     for v in row:
        #         print v
        # exit()

        db_man.execute('DELETE FROM global_results WHERE n_req == 6 and n_veh == 1 ')

        db_man.execute('DELETE FROM specific_results WHERE n_req == 6 and n_veh == 1 ')

        # for row in db_man.execute("SELECT * FROM global_results WHERE n_req == 5 "):
        #     print row

        # for filename in listdir(instancia_path):
        #     print filename
        #     if path.isfile(path.join(instancia_path, filename)):
        #         ins = Instancia(filename)
        #         n, m, n_ins = [int(x) for x in filename.split('.')[0].split('_')]
        #         data = [(n, m, n_ins, 1, m, 4, ins.get_T(), ins.get_dynamism(),
        #                                        ins.get_urgency()[0], ins.get_urgency()[1] )]
        #         for i, req in enumerate(ins.get_req()):
        #             data.append( (n, m, n_ins, i, req['service_type'], req['desired_time'],
        #                                           req['known_time'], req['service_point_x'],
        #                                           req['service_point_y']) )
        #         print data
        #         db_man.execute_script('script.txt', data)

        db_man.commit()
        db_man.close()

    exit()