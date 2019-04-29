# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 13:14:13 2018

@author: Sergio P.
"""

from models.leilao import Leilao
from models.gerador import Gerador
from models.resultado import Resultado
from models.instancia import Instancia

from json import load
from getopt import getopt, GetoptError
from sqlite3 import connect
from sys import argv
from os import listdir, path, mkdir

if __name__ == "__main__":

    if not path.isfile('conf.json'):
        raise NameError
    with open('conf.json') as file:
        conf = load(file)

    actual_path = path.dirname(path.abspath("__file__"))
    instancia_path = path.join(actual_path,'models\\instancias\\'+conf['instancias_folder'])
    if not path.isdir(instancia_path):
        mkdir(instancia_path)

    conf['actual_path'] = actual_path
    conf['instancia_path'] = instancia_path

    try:
        singles = 'olgr'
        opts, args = getopt(argv[1:],singles)
    except GetoptError as err:
        print str(err)
        exit()

    opt_list = [opt for opt, opt_args in opts]

    if '-g' in opt_list:
        print "#"*70
        print "#"
        print u"# Iniciando processo de gerar novas instâncias."

        gerador_data = conf['gerador_data']

        for cen in range(gerador_data['n_cen']):
            print "# ",gerador_data['n_cen']-cen
            ger = Gerador(conf)
            ger.set_data(gerador_data['n_req'], gerador_data['n_veh'], gerador_data['q_veh'], gerador_data['t_ser'])
            ger.save_ins()
            del ger

        print u"# Fim do processo de gerar novas instâncias."
        print "#"
        print "#"*70

    if '-o' in opt_list or '-l' in opt_list:
        if '-o' in opt_list:
            from models.otimizador import Otimizador
            text = u"# Iniciando processo de otimizar instâncias."
            input_text = 'Qual instancia(s) otimizar? > '
            def method(ins_id, *args):
                Otimizador(conf, ins_id).begin()
        else:
            from models.leilao import Leilao
            text = u"# Iniciando processo de leiloar instâncias."
            input_text = 'Qual instancia(s) realizar leilao? > '
            input_text_2 = 'Liberar VNS para agentes? > '
            def method(ins_id, *args):
                l = Leilao(conf, ins_id, args[0])
                l.begin()
                l.result()

        print "#"*70
        print "#"
        print text
        stop = False
        while not stop:
            r = raw_input(input_text)
            vns_free = False

            if '-l' in opt_list and r.lower() not in ['s','static']:
                r2 = raw_input(input_text_2)
                if r2.lower() == 'y':
                    vns_free = True

            if r.lower() == 's':
                stop = True
            elif r == 'all':
                for filename in listdir(instancia_path):
                    print filename
                    ins_id = filename.split('.')[0]
                    if int(ins_id.split('_')[0]) == 0:
                        continue
                    method(ins_id, vns_free)
            else:
                method(r, vns_free)

    if '-r' in opt_list:
        ins = Instancia('05_02_001.json')
        tau = ins.get_tau()
        for k, v in tau.iteritems():
            if k[0] == 0 and k[1] in [2,4]:
                print "Key: ",k," and Value: ",v
            if k[0] == 6 and k[1] in [2,4]:
                print "Key: ",k," and Value: ",v

    exit()