# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 13:14:13 2018

@author: Sergio P.
"""

from models.otimizador import Otimizador
from models.gerador import Gerador
from getopt import getopt, GetoptError
from sys import argv

if __name__ == "__main__":

    try:
        singles = 'og'
        opts, args = getopt(argv[1:],singles)
    except GetoptError as err:
        print str(err)
        exit()
    otimizar = False
    gerar = False
    for opt, opt_args in opts:
        if opt == '-o':
            otimizar = True
        if opt == '-g':
            gerar = True

    if gerar:
        ger = Gerador()
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
                
        q_veh = 4
        for cen in range(20):
            for n_req in range(1,11):
                n_veh = int(n_req / q_veh) + 1
                for n_v in range(n_veh, n_veh+2):
                    ger.set_requests_data(n_req)
                    ger.set_static_data(n_v,q_veh,1)
                    ger.set_requests()
                    ger.save_ins()
        exit()

        for cen in range(data['n_cen']):
            ger.set_requests_data(data['n_req'])
            ger.set_static_data(data['n_veh'],data['q_veh'],data['t_ser'])
            ger.set_requests()
            ger.save_ins()

    if otimizar:
        print "#"*70
        print "#"
        print u"# Iniciando processo de otimizar instâncias."
        stop = False
        while not stop:
            r = raw_input('Qual instancia(s) otimizar? > ')
            if r == 'all':
                pass
            elif r == 'S':
                stop = True
            else:
                otm = Otimizador(r)
                otm.begin()

    exit()