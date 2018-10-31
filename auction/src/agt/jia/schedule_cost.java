// Internal action code for project auction

package jia;

import jason.*;
import jason.asSemantics.*;
import jason.asSyntax.*;
import java.util.Random;
import java.util.List;
import java.util.ArrayList;

@SuppressWarnings("serial")
public class schedule_cost extends DefaultInternalAction {
	
	private String service_type = "";
	private String client_name = "_";
	private double service_position_x = 0;
	private double service_position_y = 0;
	private double desired_time = 0;
	private double known_time = 0;
	
	private double travel_distance(ListTerm event, ListTerm last_event) throws NoValueException {
		
		NumberTerm x0Term = (NumberTerm)last_event.get(3);
		NumberTerm y0Term = (NumberTerm)last_event.get(4);
		NumberTerm x1Term = (NumberTerm)event.get(3);
		NumberTerm y1Term = (NumberTerm)event.get(4);
		double x0 = x0Term.solve();
		double y0 = y0Term.solve();
		double x1 = x1Term.solve();
		double y1 = y1Term.solve();
		
		return Math.round( Math.sqrt( Math.pow(x0-x1, 2) + Math.pow(y0-y1, 2) ) );
		
	}
	
	private double[] metrics(ListTerm Sch) throws NoValueException {
		/** Cálculo das métricas de avaliação do agendamento
		 * 		Recebe:  ListTerm Sch -> agendamento a ser avaliado
		 * 		Retorna: double[3]    -> métricas de avaliação
		 * 
		 *  O vetor contém as métricas de: distância percorrida;
		 *  atraso de atendimento; e tempo de viagem.**/
		
		double[] metrics = new double[3]; // retorno final
		List<String> cliente_list = new ArrayList<String>(); // lista com o nome dos clientes sendo atendidos
		List<Double> pick_up_list = new ArrayList<Double>(); // lista com os tempos de atendimento
		ListTerm final_event = ASSyntax.createList();
		for (int i = 0; i < 3; i++) {
			final_event.add(ASSyntax.createNumber(0));
		}
		final_event.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_X));
		final_event.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_Y));
			// final_event é criado para garantir que o veículo volta pro depósito no fim da operação
			// (ou que pelo menos isso é considerado na hora de calcular as métricas haha)
		
		for (int index = 0; index < Sch.size(); index++) {
    		ListTerm event = (ListTerm)Sch.get(index); // evento sendo atualmente avaliado
			StringTerm cliente = (StringTerm)event.get(0); // nome do cliente
			NumberTerm atendimento = (NumberTerm)event.get(1); // tempo de atendimento
			
			if (index != 0) {
				/** Calculo do tempo de viagem
				 * 	so realizado a partir do segundo evento, já que é retroativo **/
	    		ListTerm last_event = (ListTerm)Sch.get(index-1);
	    		NumberTerm last_atendimento = (NumberTerm)last_event.get(1);
	    		
	    		metrics[0] += atendimento.solve() - last_atendimento.solve() - parameters.SERVICE_TIME;
			}
			
			if (!cliente_list.contains(cliente.toString())) {
				/** Calculo do atraso dos passageiros
				 *  so realizado no primeiro atendimento ao cliente (pick_up)
				 *  ponderado por parameters.CONTROL_GAMMA entre o atual e os passados **/
				NumberTerm desejado = (NumberTerm)event.get(2);
				pick_up_list.add(atendimento.solve());
				cliente_list.add(cliente.toString());
				
				if (cliente.toString().equals("\""+this.client_name+"\"")) {
					metrics[1] += (1 - parameters.CONTROL_GAMMA)*(atendimento.solve() - desejado.solve());
				} else {
					metrics[1] += parameters.CONTROL_GAMMA*(atendimento.solve() - desejado.solve());
				}
			} else {
				/** Calculo do tempo de viagem dos passageiros
				 *  so realizado no segundo atendimento ao cliente (drop_off) **/
				int cliente_index = cliente_list.indexOf(cliente.toString());
				cliente_list.remove(cliente_index);
				
				metrics[2] += atendimento.solve() - pick_up_list.remove(cliente_index);				
			}
			
			if (cliente_list.size() > parameters.VEHICLE_CAPACITY) {
				/** Se, a qualquer momento, o numero de clientes passar 
				 *  da capacidade do veículo, custo é infinito **/
				metrics[0] = Double.POSITIVE_INFINITY;
				break;
			}
			
		}
		
		metrics[0] += this.travel_distance((ListTerm)Sch.get(Sch.size()-1), final_event);		
		
		return metrics;
	}
	
	private double kappa_ij(ListTerm Sch, int i, int j) throws NoValueException {		
		/** Calcula custo da inserção do pedido em i e j **/
		
    	double[] metrics_base = this.metrics(Sch);
    	double final_kappa = 0;
    	
    	/** Os eventos no Sch são definidos por:
    	 *  	[cliente, atendimento, desejado, x, y]
    	 *  Abaixo, dois eventos (buscar e levar) são criados
    	 *  de acordo com o cliente. **/
    	
    	ListTerm new_event_i = ASSyntax.createList(ASSyntax.createString(this.client_name),
    											   ASSyntax.createNumber(0),
    			                                   ASSyntax.createNumber(this.desired_time));
    	
    	ListTerm new_event_j = ASSyntax.createList(ASSyntax.createString(this.client_name),
				   							       ASSyntax.createNumber(0),
								                   ASSyntax.createNumber(this.desired_time));
    	
    	if ( this.service_type.equals("\"drop\"") ) {
    		new_event_i.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_X));
    		new_event_i.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_Y));
    		
    		new_event_j.add(ASSyntax.createNumber(this.service_position_x));
    		new_event_j.add(ASSyntax.createNumber(this.service_position_y));    		
    	} else {
    		new_event_j.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_X));
    		new_event_j.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_Y));
    		
    		new_event_i.add(ASSyntax.createNumber(this.service_position_x));
    		new_event_i.add(ASSyntax.createNumber(this.service_position_y));    		
    	}
    	
    	/** Os testes são realizados sobre um clone do agendamento
    	 *  Após a insersão em i e j, todos os eventos após i são
    	 *  atualizados, modificando seu tempo de atendimento de
    	 *  acordo com as distancias **/
    	
    	ListTerm Sch_novo = Sch.cloneLT();
    	Sch_novo.add(i+1, new_event_i);
    	Sch_novo.add(j+2, new_event_j);
    	for ( int index = i+1; index < Sch_novo.size(); index++ ) {
    		ListTerm event = (ListTerm)Sch_novo.get(index);
    		ListTerm last_event = (ListTerm)Sch_novo.get(index-1);

    		NumberTerm t0Term = (NumberTerm)last_event.get(1);
    		double tempo_viagem = this.travel_distance(event, last_event);
    		double instante_atendimento = t0Term.solve() + parameters.SERVICE_TIME + tempo_viagem;
			event.set(1, ASSyntax.createNumber(instante_atendimento));
    		
    		Sch_novo.set(index, event);
    	}
    	
    	/** As métricas de avaliação do agendamento são calculadas
    	 *  usando método interno e depois somadas, ponderando com
    	 *  os parâmetros de controle. Esse é o resultado final **/
    	
    	double[] metrics = this.metrics(Sch_novo);
    	
    	final_kappa += parameters.CONTROL_C0*(metrics[0]-metrics_base[0]);
    	final_kappa += parameters.CONTROL_C1*(metrics[1]-metrics_base[1]);
    	final_kappa += (1 - parameters.CONTROL_C0 - parameters.CONTROL_C1)*(metrics[2]-metrics_base[2]);
		
		return final_kappa;
	}

    @Override
    public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {
        // execute the internal action
    	//	 jia.schedule_cost(Sch, St, X, Y, KT, DT, Result)
    	
        ts.getAg().getLogger().info("executing internal action 'jia.schedule_cost'");
        if (!args[args.length-1].isVar()) {
        	throw new JasonException("Last argument of schedule_cost is not a variable");
        }
        
        int i_pe = 0;                        // indice do primeiro evento
        int n_e = 0;                         // total de eventos
        ListTerm Sch = (ListTerm)args[0];    // agendamento atual
        
        StringTerm St = (StringTerm)args[1]; // tipo de serviço
        this.service_type = St.toString();
        
        NumberTerm Pos_x = (NumberTerm)args[2];    // posição x do novo pedido
        this.service_position_x = Pos_x.solve();
        
        NumberTerm Pos_y = (NumberTerm)args[3];    // posição y do novo pedido
        this.service_position_y = Pos_y.solve();
        
        NumberTerm Kt = (NumberTerm)args[4]; // instante conhecido (agora)
        this.known_time = Kt.solve();
        		
        NumberTerm Dt = (NumberTerm)args[5]; // instante desejado (no futuro)
        this.desired_time = Dt.solve();
        
    	for (Term t: Sch) {    // Todos os eventos da agenda
            ListTerm event = (ListTerm)t;    // Um evento específico
            NumberTerm et = (NumberTerm)event.get(1); // instante do evento
            if ( et.solve() < this.known_time || et.solve() < this.desired_time) {
            	/* se é passado OU anterior ao desejado,
            	   aumenta o index do primeiro evento    */
            	i_pe += 1;
            }
            n_e += 1;
        }
    	
    	int n_estrela = n_e - i_pe; // número de espaços disponíveis
    	if ( n_e == 1 ) { // caso primeira inserção do motorista (é feio, eu sei)
    		n_estrela = 1;
    		i_pe = 0;
    	}
    	
    	double actValue = Double.POSITIVE_INFINITY;      // menor valor até agora
    	double minValue = actValue;        // valor atual
    	for (int i = 0; i < n_estrela; i ++) {		// número de linhas
    		for (int j = 0; j < n_estrela; j ++) {	// número de colunas
    			if (j >= i){
    				// calcula o custo da inserção na triangular superior
    				actValue = this.kappa_ij(Sch, i+i_pe, j+i_pe);
    			}
    			
    			if (actValue < minValue) {
    				// se o atual é menor do que o menor até agora, atualiza
    				minValue = actValue;
    				System.out.println(i+" "+j);
    			}
    		}
    	}

        // unifica o resultado com a variável passada
    	return un.unifies(args[args.length-1], ASSyntax.createNumber(minValue));
    }
}






















