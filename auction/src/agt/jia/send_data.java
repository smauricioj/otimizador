// Internal action code for project auction

package jia;

import java.util.ArrayList;
import java.util.List;

import jason.*;
import jason.asSemantics.*;
import jason.asSyntax.*;
import java.io.*;

@SuppressWarnings("serial")	
public class send_data extends DefaultInternalAction {
	
	private double travel_distance(ListTerm event, ListTerm last_event) throws NoValueException {
		
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

    @Override
    public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {
        // execute the internal action
        ts.getAg().getLogger().info("executing internal action 'jia.send_data'");
        
        // System.out.println("Working Directory = " + System.getProperty("user.dir"));
        
        PrintWriter pw = new PrintWriter(System.getProperty("user.dir")+"ola.txt", "UTF-8");

        ListTerm Sch = (ListTerm)args[0];    // agendamento atual
        
        double[] metrics = new double[3]; // retorno final
		List<String> cliente_list = new ArrayList<String>(); // lista com o nome dos clientes sendo atendidos
		List<Double> pick_up_list = new ArrayList<Double>(); // lista com os tempos de atendimento
		List<Double> atraso_list = new ArrayList<Double>();
		
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
				metrics[1] += atendimento.solve() - desejado.solve();
			} else {
				/** Calculo do tempo de viagem dos passageiros
				 *  so realizado no segundo atendimento ao cliente (drop_off) **/
				int cliente_index = cliente_list.indexOf(cliente.toString());
				
				metrics[2] += atendimento.solve() - pick_up_list.get(cliente_index);				
			}
			
		}
		
		metrics[0] += this.travel_distance((ListTerm)Sch.get(Sch.size()-1), final_event);

        // everything ok, so returns true
        return true;
    }
}
