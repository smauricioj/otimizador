# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 13:14:13 2018

@author: Sergio P.
"""

from json import load
from getopt import getopt, GetoptError
from sys import argv
from os import listdir, path, mkdir
from ast import literal_eval

if __name__ == "__main__":

    if not path.isfile('conf.json'):
        raise NameError
    with open('conf.json') as file:
        conf = load(file)

    conf['actual_path'] = path.dirname(path.abspath("__file__"))
    conf['instancia_path'] = path.join( conf['actual_path'],'models\\instancias\\'+conf['instancias_folder'])
    if not path.isdir(conf['instancia_path']):
        mkdir(conf['instancia_path'])

    try:
        singles = 'olgr'
        opts, args = getopt(argv[1:],singles)
    except GetoptError as err:
        print str(err)
        exit()

    opt_list = [opt for opt, opt_args in opts]

    if '-g' in opt_list:
        from models.gerador import Gerador

        print "#"*70
        print "#"
        print u"# Iniciando processo de gerar novas instâncias."

        gerador_data = conf['gerador_data']

        for cen in range(gerador_data['n_cen']):
            print "# ",gerador_data['n_cen']-cen
            for n_req in gerador_data['n_req']:
                for n_veh in gerador_data['n_veh']:
                    ger = Gerador(conf)
                    ger.set_data(n_req, n_veh, gerador_data['q_veh'], gerador_data['t_ser'])
                    ger.save_ins()
                    del ger

        print u"# Fim do processo de gerar novas instâncias."
        print "#"
        print "#"*70

    if '-o' in opt_list or '-l' in opt_list:
        if '-o' in opt_list:
            from models.otimizador import Otimizador
            processo = 'otimizar'
            processo_data = 'otimizador_data'
            def method(ins_id):
                Otimizador(conf, ins_id).begin()
        else:
            from models.leilao import Leilao
            processo = 'leiloar'
            processo_data = 'leilao_data'
            def method(ins_id):
                Leilao(conf, ins_id).begin()

        print "#"*70
        print "#"
        print u"# Iniciando processo de {} instâncias.".format(processo)

        ins_id = conf[processo_data]['ins_id']

        if ins_id == 'all' or ':' in ins_id:
            if ':' in ins_id:
                filtro, values = ins_id.split(':')
                order = ['req','veh'].index(filtro)
            for filename in listdir(conf['instancia_path']):
                print '# ', filename
                file_ins_id = filename.split('.')[0]
                if int(file_ins_id.split('_')[0]) == 0:
                    continue
                if ':' in ins_id and int(file_ins_id.split('_')[order]) not in literal_eval(values):
                    # print 'entrei com ',int(file_ins_id.split('_')[order]),' e ',value
                    continue
                method(file_ins_id)
        else:
            if ins_id == 'static' and '-l' in opt_list:
                pass
            elif ins_id not in [filename.split('.')[0] for filename in listdir(conf['instancia_path'])]:
                raise NameError
            elif ins_id.split('_')[0] == 0:
                raise NameError
            method(ins_id)

    if '-r' in opt_list:
        from models.instancia import Instancia

        ins = Instancia('05_02_001.json')
        tau = ins.get_tau()
        for k, v in tau.iteritems():
            if k[0] == 0 and k[1] in [2,4]:
                print "Key: ",k," and Value: ",v
            if k[0] == 6 and k[1] in [2,4]:
                print "Key: ",k," and Value: ",v