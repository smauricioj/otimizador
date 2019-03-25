package jia;

import java.util.ArrayList;
import java.util.List;

import jason.NoValueException;
import jason.asSemantics.TransitionSystem;
import jason.asSyntax.ASSyntax;
import jason.asSyntax.ListTerm;
import jason.asSyntax.NumberTerm;
import jason.asSyntax.StringTerm;

public class functions{
	public static double travel_distance(ListTerm event_1, ListTerm event_2) throws NoValueException {
		/** Calculo da dist�ncia entre dois eventos do agendamento
		 * 
		 *      Recebe:  ListTerm event_n -> Eventos que ocorrem, em ordem
		 *      
		 *      Retorna: double           -> Valor da dist�ncia entre os eventos**/
				
		NumberTerm x0Term = (NumberTerm)event_2.get(3);
		NumberTerm y0Term = (NumberTerm)event_2.get(4);
		NumberTerm x1Term = (NumberTerm)event_1.get(3);
		NumberTerm y1Term = (NumberTerm)event_1.get(4);
		double x0 = x0Term.solve();
		double y0 = y0Term.solve();
		double x1 = x1Term.solve();
		double y1 = y1Term.solve();
		
		return Math.round( Math.sqrt( Math.pow(x0-x1, 2) + Math.pow(y0-y1, 2) ) * 100.0) / 100.0;		
	}
	
	public static double[] metrics(ListTerm Sch, String client_name, TransitionSystem ts) throws NoValueException {
		/** C�lculo das m�tricas de avalia��o do agendamento
		 * 
		 * 		Recebe:  ListTerm Sch        -> agendamento a ser avaliado
		 * 				 String client_name  -> Nome do cliente atualmente sendo inserido
		 * 				 TransitionSystem ts -> M�todo pra prints do jason
		 * 
		 * 		Retorna: double[3]    -> m�tricas de avalia��o
		 * 
		 *  O vetor cont�m as m�tricas de: dist�ncia percorrida;
		 *  atraso de atendimento; e tempo de viagem.**/
		
		double[] metrics = new double[3]; // retorno final
		List<String> cliente_list = new ArrayList<String>(); // lista com o nome dos clientes sendo atendidos
		List<Double> pick_up_list = new ArrayList<Double>(); // lista com os tempos de atendimento
		
		ListTerm final_event = ASSyntax.createList();
		for (int i = 0; i < 3; i++) {
			final_event.add(ASSyntax.createNumber(0)); //dummies
		}
		final_event.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_X));
		final_event.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_Y));
			// final_event � criado para garantir que o ve�culo volta pro dep�sito no fim da opera��o
			// (ou que pelo menos isso � considerado na hora de calcular as m�tricas haha)
		
		ListTerm later_event = (ListTerm)Sch.get(Sch.size()-1);
		NumberTerm later_atendimento = (NumberTerm)later_event.get(1);
			// later_event usado pra calcular se a rota respeita o limite de tempo m�ximo da simula��o
		
		// ts.getAg().getLogger().info("METRICS Sch ->"+Sch);
		
		for (int index = 0; index < Sch.size(); index++) {
    		ListTerm event = (ListTerm)Sch.get(index); // evento sendo atualmente avaliado
			StringTerm cliente = (StringTerm)event.get(0); // nome do cliente
			NumberTerm atendimento = (NumberTerm)event.get(1); // tempo de atendimento
			NumberTerm desejado = (NumberTerm)event.get(2); // instante desejado
			NumberTerm pos_x = (NumberTerm)event.get(3); // posicao x do antendimento
			NumberTerm pos_y = (NumberTerm)event.get(4); // posicao y do atendimento
			StringTerm tipo = (StringTerm)event.get(5);
			double weight = 1; // peso entre pedidos passados e atual no atraso
			
			if (index != 0) {
				/** Calculo do tempo de viagem
				 * 	so realizado a partir do segundo evento, j� que � retroativo **/	    		
	    		metrics[0] += functions.travel_distance(event, (ListTerm)Sch.get(index-1));
			}
			
			if (!cliente_list.contains(cliente.toString())) {
				/** Calculo do atraso dos passageiros
				 *  so realizado no primeiro atendimento ao cliente (embarque)
				 *  ponderado por parameters.CONTROL_GAMMA entre o atual e os passados
				 *  Se o pedido � de drop e come�a fora do dep�sito, o custo � infinito
				 *  Se o pedido � de pick e come�a no dep�sito, o custo � infinito
				 *  Se o pedido for antedido antes do desejado, o custo � infinito **/
				
				pick_up_list.add(atendimento.solve());
				cliente_list.add(cliente.toString());
				
				if (tipo.toString().equals("\"drop\"")) {					
					if ( ( Math.round(pos_x.solve()) != parameters.VEHICLE_INITIAL_POSITION_X ) || ( Math.round(pos_y.solve()) != parameters.VEHICLE_INITIAL_POSITION_Y ) ) {
						metrics[1] = Double.POSITIVE_INFINITY;
					}			
				}
				
				if (tipo.toString().equals("\"pick\"")) {
					if ( ( Math.round(pos_x.solve()) == parameters.VEHICLE_INITIAL_POSITION_X ) & ( Math.round(pos_y.solve()) == parameters.VEHICLE_INITIAL_POSITION_Y ) ) {
						metrics[1] = Double.POSITIVE_INFINITY;
					}					
				}
				
				if (cliente.toString().equals("\""+client_name+"\"")) {
					weight = (1 - parameters.CONTROL_GAMMA);
				} else {
					weight = parameters.CONTROL_GAMMA;
				}
				
				if (atendimento.solve() - desejado.solve() < 0) {
					metrics[1] = Double.POSITIVE_INFINITY;
				} else {
					metrics[1] += weight*(atendimento.solve() - desejado.solve());				
				}
			} else {
				/** Calculo do tempo de viagem dos passageiros
				 *  so realizado no segundo atendimento ao cliente (desembarque) **/
				int cliente_index = cliente_list.indexOf(cliente.toString());
				cliente_list.remove(cliente_index);
				
				metrics[2] += atendimento.solve() - pick_up_list.remove(cliente_index);				
			}
			
			if (cliente_list.size() > parameters.VEHICLE_CAPACITY || atendimento.solve() > parameters.MAX_TIME) {
				/** Se, a qualquer momento, o numero de clientes passar 
				 *  da capacidade do ve�culo ou o instante de atendimento
				 *  for maior do que a simula��o, o custo � infinito **/
				metrics[0] = Double.POSITIVE_INFINITY;
				break;
			}
			
		}
		
		if (functions.travel_distance(later_event, final_event) + later_atendimento.solve() > parameters.MAX_TIME ) {
			metrics[0] = Double.POSITIVE_INFINITY;
		} else {
			metrics[0] += functions.travel_distance((ListTerm)Sch.get(Sch.size()-1), final_event);
		} /** Se � poss�vel terminar a rota antes de acabar a simula��o, ok, se n�o infinito **/
		
		// ts.getAg().getLogger().info("METRICS total ->"+metrics[0]+" "+metrics[1]+" "+metrics[2]);
		
		return metrics;
	}
	
	public static double metrics_diff_cost(double[] metrics_new, double[] metrics_base) {
		/** Calcula a diferen�a entre duas m�tricas  **/
		
		double final_cost = 0;
		
		final_cost += parameters.CONTROL_C0*(metrics_new[0]-metrics_base[0]);
		final_cost += parameters.CONTROL_C1*(metrics_new[1]-metrics_base[1]);
		final_cost += (1 - parameters.CONTROL_C0 - parameters.CONTROL_C1)*(metrics_new[2]-metrics_base[2]);
		
		return final_cost;		
	}
	
	public static ListTerm Sch_time_fit(ListTerm Sch, int index_offset) throws NoValueException {
        for ( int index = index_offset; index < Sch.size(); index++ ) {
        	if (index != 0) {
                ListTerm event = (ListTerm)Sch.get(index);
                ListTerm last_event = (ListTerm)Sch.get(index-1);
                NumberTerm last_event_initial_time = (NumberTerm)last_event.get(1);
                NumberTerm event_desired_time = (NumberTerm)event.get(2);
                double travel_time = functions.travel_distance(event, last_event);
                double event_initial_time = last_event_initial_time.solve() + parameters.SERVICE_TIME + travel_time;
                event_initial_time = Math.round(event_initial_time * 100.0) / 100.0;
                event.set(1, ASSyntax.createNumber(Math.max(event_desired_time.solve(), event_initial_time)));
                
                Sch.set(index, event);        		
        	}
        }
        return Sch;
	}
}




























