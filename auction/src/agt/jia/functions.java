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
	public static double travel_distance(ListTerm event, ListTerm last_event) throws NoValueException {
		
		NumberTerm x0Term = (NumberTerm)last_event.get(3);
		NumberTerm y0Term = (NumberTerm)last_event.get(4);
		NumberTerm x1Term = (NumberTerm)event.get(3);
		NumberTerm y1Term = (NumberTerm)event.get(4);
		double x0 = x0Term.solve();
		double y0 = y0Term.solve();
		double x1 = x1Term.solve();
		double y1 = y1Term.solve();
		
		return Math.round( Math.sqrt( Math.pow(x0-x1, 2) + Math.pow(y0-y1, 2) ) * 100.0) / 100.0;		
	}
	
	public static double[] metrics(ListTerm Sch, String client_name, TransitionSystem ts) throws NoValueException {
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
			final_event.add(ASSyntax.createNumber(0)); //dummies
		}
		final_event.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_X));
		final_event.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_Y));
			// final_event é criado para garantir que o veículo volta pro depósito no fim da operação
			// (ou que pelo menos isso é considerado na hora de calcular as métricas haha)
		
		ListTerm later_event = (ListTerm)Sch.get(Sch.size()-1);
		NumberTerm later_atendimento = (NumberTerm)later_event.get(1);
			// later_event usado pra calcular se a rota respeita o limite de tempo máximo da simulação
		
		for (int index = 0; index < Sch.size(); index++) {
    		ListTerm event = (ListTerm)Sch.get(index); // evento sendo atualmente avaliado
			StringTerm cliente = (StringTerm)event.get(0); // nome do cliente
			NumberTerm atendimento = (NumberTerm)event.get(1); // tempo de atendimento
			
			if (index != 0) {
				/** Calculo do tempo de viagem
				 * 	so realizado a partir do segundo evento, já que é retroativo **/	    		
	    		metrics[0] += functions.travel_distance(event, (ListTerm)Sch.get(index-1));
			}
			
			if (!cliente_list.contains(cliente.toString())) {
				/** Calculo do atraso dos passageiros
				 *  so realizado no primeiro atendimento ao cliente (pick_up)
				 *  ponderado por parameters.CONTROL_GAMMA entre o atual e os passados **/
				NumberTerm desejado = (NumberTerm)event.get(2);
				pick_up_list.add(atendimento.solve());
				cliente_list.add(cliente.toString());
				
				if (cliente.toString().equals("\""+client_name+"\"")) {
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
			
			if (cliente_list.size() > parameters.VEHICLE_CAPACITY || atendimento.solve() > parameters.MAX_TIME) {
				/** Se, a qualquer momento, o numero de clientes passar 
				 *  da capacidade do veículo ou o instante de atendimento
				 *  for maior do que a simulação, o custo é infinito **/
				metrics[0] = Double.POSITIVE_INFINITY;
				break;
			}
			
		}
		
		if (functions.travel_distance(later_event, final_event) + later_atendimento.solve() > parameters.MAX_TIME ) {
			metrics[0] = Double.POSITIVE_INFINITY;
		} else {
			metrics[0] += functions.travel_distance((ListTerm)Sch.get(Sch.size()-1), final_event);
		} /** Se é possível terminar a rota antes de acabar a simulação, ok, se não infinito **/	
		
		return metrics;
	}
	
	public static double metrics_insertion_cost(double[] metrics_new, double[] metrics_base) {
		
		double final_cost = 0;
		
		final_cost += parameters.CONTROL_C0*(metrics_new[0]-metrics_base[0]);
		final_cost += parameters.CONTROL_C1*(metrics_new[1]-metrics_base[1]);
		final_cost += (1 - parameters.CONTROL_C0 - parameters.CONTROL_C1)*(metrics_new[2]-metrics_base[2]);
		
		return final_cost;		
	}
}




























