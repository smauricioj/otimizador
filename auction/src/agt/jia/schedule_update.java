// Internal action code for project auction

package jia;

import jason.*;
import jason.asSemantics.*;
import jason.asSyntax.*;

@SuppressWarnings("serial")
public class schedule_update extends DefaultInternalAction {
	
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
    	//	 jia.schedule_update(Sch, I_i, I_j, St, X, Y, DT, A, NewSch)
    	
        ts.getAg().getLogger().info("executing internal action 'jia.schedule_cost'");
        if (!args[args.length-1].isVar()) {
        	throw new JasonException("Last argument of schedule_cost is not a variable");
        }
        
        ListTerm Sch = (ListTerm)args[0];
        NumberTerm i_term = (NumberTerm)args[1];
        int i = (int) i_term.solve();
        NumberTerm j_term = (NumberTerm)args[2];
        int j = (int) j_term.solve();
        StringTerm St = (StringTerm)args[3];
        NumberTerm x = (NumberTerm)args[4];
        NumberTerm y = (NumberTerm)args[5];
        NumberTerm Dt = (NumberTerm)args[6];
        Atom A = (Atom)args[7];

    	
    	/** Os eventos no Sch são definidos por:
    	 *  	[cliente, atendimento, desejado, x, y]
    	 *  Abaixo, dois eventos (buscar e levar) são criados
    	 *  de acordo com o cliente. **/
    	
    	ListTerm new_event_i = ASSyntax.createList(ASSyntax.createString(A.toString()),
    											   ASSyntax.createNumber(0),
    			                                   ASSyntax.createNumber(Dt.solve()));
    	
    	ListTerm new_event_j = ASSyntax.createList(ASSyntax.createString(A.toString()),
				   							       ASSyntax.createNumber(0),
								                   ASSyntax.createNumber(Dt.solve()));
    	
    	if ( St.toString().equals("\"drop\"") ) {
    		new_event_i.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_X));
    		new_event_i.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_Y));
    		
    		new_event_j.add(ASSyntax.createNumber(x.solve()));
    		new_event_j.add(ASSyntax.createNumber(y.solve()));    		
    	} else {
    		new_event_j.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_X));
    		new_event_j.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_Y));
    		
    		new_event_i.add(ASSyntax.createNumber(x.solve()));
    		new_event_i.add(ASSyntax.createNumber(y.solve()));    		
    	}
    	
    	/** Os testes são realizados sobre um clone do agendamento
    	 *  Após a insersão em i e j, todos os eventos após i são
    	 *  atualizados, modificando seu tempo de atendimento de
    	 *  acordo com as distancias **/
    	
    	ListTerm Sch_novo = Sch.cloneLT();
    	Sch_novo.add(j+1, new_event_j);
    	Sch_novo.add(i+1, new_event_i);
    	for ( int index = i+1; index < Sch_novo.size(); index++ ) {
    		ListTerm event = (ListTerm)Sch_novo.get(index);
    		ListTerm last_event = (ListTerm)Sch_novo.get(index-1);

    		NumberTerm t0Term = (NumberTerm)last_event.get(1);
    		double tempo_viagem = this.travel_distance(event, last_event);
    		double instante_atendimento = t0Term.solve() + parameters.SERVICE_TIME + tempo_viagem;
			event.set(1, ASSyntax.createNumber(Math.max(Dt.solve(), instante_atendimento)));
    		
    		Sch_novo.set(index, event);
    	}
    	
    	return un.unifies(args[args.length-1], Sch_novo);
    	
    }
}
