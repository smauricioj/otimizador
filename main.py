# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 13:14:13 2018

@author: Sergio P.
"""

from models.otimizador import Otimizador
from models.gerador import Gerador
from models.resultado import Resultado
from models.instancia import Instancia
from models.db_manager import Db_manager
from getopt import getopt, GetoptError
from sqlite3 import connect
from sys import argv
from os import listdir, path

if __name__ == "__main__":

    try:
        singles = 'ogrt'
        opts, args = getopt(argv[1:],singles)
    except GetoptError as err:
        print str(err)
        exit()
    otimizar = False
    gerar = False
    resultar = False
    tabelar = False
    for opt, opt_args in opts:
        if opt == '-o':
            otimizar = True
        if opt == '-g':
            gerar = True
        if opt == '-r':
            resultar = True
        if opt == '-t':
            tabelar = True

    if gerar:
                
        # ################################################### #
        #                                                     #
        # PANIC BUTTON - Caso delete todas as instâncias      #
        #                                                     #
        # q_veh = 4                                           #
        # for cen in range(15):                               #
        #     for n_req in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]:                       #
        #         n_veh = int(n_req / q_veh) + 1              #
        #         for n_v in range(n_veh, n_veh+2):
        #             ger = Gerador(n_req)           #
        #             ger.set_data(n_v, q_veh, 1)
        #             ger.save_ins()                         #
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
                if r in ('Y','N'):
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

    if otimizar:
        print "#"*70
        print "#"
        print u"# Iniciando processo de otimizar instâncias."
        stop = False
        while not stop:
            r = raw_input('Qual instancia(s) otimizar? > ')
            if r == 'all':
                actual_path = path.dirname(path.abspath("__file__"))
                instancia_path = path.join(actual_path,'models\\instancias')
                for filename in listdir(instancia_path):
                    print filename
                    ins_id = filename.split('.')[0]
                    n_req, n_veh, n_ins = [int(x) for x in ins_id.split('_')]
                    if n_req in [3,5,7]:
                        Otimizador(ins_id).begin()
            elif r == 'S':
                stop = True
            else:
                Otimizador(r).begin()

    if resultar:
        Resultado(Instancia('00_00_000.json')).plot_global_result_data()

    if tabelar:                
        actual_path = path.dirname(path.abspath("__file__"))
        scripts_path = path.join(actual_path,'models\\db_scripts')
        instancia_path = path.join(actual_path,'models\\instancias')

        db_man = Db_manager('persistent_data.db', scripts_path)

        # for row in db_man.execute("SELECT * FROM requests"):
        #     print row

        # exit()

        # for filename in listdir(instancia_path):
        #     print filename
        #     ins = Instancia(filename)
        #     n, m, n_ins = [int(x) for x in filename.split('.')[0].split('_')]
        #     data = []
        #     for i, req in enumerate(ins.get_req()):
        #         data.append( (n, m, n_ins, i, req['service_type'], req['desired_time'],
        #                                       req['known_time'], req['service_point_x'],
        #                                       req['service_point_y']) )
        #     db_man.execute_script('script.txt', data)

        db_man.commit()
        db_man.close()

    exit()