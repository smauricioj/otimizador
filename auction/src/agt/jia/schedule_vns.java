// Internal action code for project auction

package jia;

import java.util.Random;

import jason.*;
import jason.asSemantics.*;
import jason.asSyntax.*;

@SuppressWarnings("serial")
public class schedule_vns extends DefaultInternalAction {
	
	private double known_time = 0;
	
	private ListTerm OneOneExchange(TransitionSystem ts, ListTerm Sch, int i_pe) throws Exception {
		ListTerm NewSch = Sch.cloneLT();
		ListTerm Sch_backup = Sch.cloneLT();
		double [] Sch_metrics = functions.metrics(Sch, "", ts);
		double [] NewSch_metrics = functions.metrics(NewSch, "", ts);
		double vns_cost = Double.MAX_VALUE;
		
		OUTER_LOOP: 
        	for (int index = i_pe+1; index < Sch.size(); index++) {		            // todos os eventos futuros
        		Term event_1 = NewSch.remove(index);
        		ListTerm NewSch_backup = NewSch.cloneLT();
        		for (int next_index = index; next_index < NewSch.size(); next_index++) { // todos os eventos futuros
        			Term event_2 = NewSch.remove(next_index);
        			NewSch.add(next_index, event_1);
        			NewSch.add(index, event_2);
        			NewSch = functions.Sch_time_fit(NewSch, next_index-1);
        			NewSch_metrics = functions.metrics(NewSch, "", ts);
        			vns_cost = functions.metrics_diff_cost(NewSch_metrics, Sch_metrics);
        			if (vns_cost < 0) {
        				Sch = NewSch;
        				break OUTER_LOOP;
        			}
    				NewSch = NewSch_backup.cloneLT();							// volta Sch SEM event_1
        		}
        		NewSch = Sch_backup.cloneLT();									// volta Sch COM event_1
        	}
		
		return Sch;
	}
	
	private ListTerm OneZeroExchange(TransitionSystem ts, ListTerm Sch, int i_pe) throws Exception {
		ListTerm NewSch = Sch.cloneLT();
		ListTerm Sch_backup = Sch.cloneLT();
		double [] Sch_metrics = functions.metrics(Sch, "", ts);
		double [] NewSch_metrics = functions.metrics(NewSch, "", ts);
		double vns_cost = Double.MAX_VALUE;
		
		OUTER_LOOP: 
        	for (int index = i_pe+1; index < Sch.size(); index++) {		            // todos os eventos futuros
        		Term event = NewSch.remove(index);
        		ListTerm NewSch_backup = NewSch.cloneLT();
        		for (int next_index = index; next_index < NewSch.size(); next_index++) { // todos os eventos futuros
        			if (index != next_index) 	{                               // para eventos diferentes
            			NewSch.add(next_index, event);
            			NewSch = functions.Sch_time_fit(NewSch, next_index-1);
            			NewSch_metrics = functions.metrics(NewSch, "", ts);
            			vns_cost = functions.metrics_diff_cost(NewSch_metrics, Sch_metrics);
            			if (vns_cost < 0) {
            				Sch = NewSch;
            				break OUTER_LOOP;
            			}
        			}
    				NewSch = NewSch_backup.cloneLT();							// volta Sch SEM event
        		}
        		NewSch = Sch_backup.cloneLT();									// volta Sch COM event
        	}
		
		return Sch;
	}

    @Override
    public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {
        // execute the internal action
    	//   	 jia.schedule_vns(Sch, KT, NewSch)
        // ts.getAg().getLogger().info("executing internal action 'jia.schedule_vns'");
        
        ListTerm Sch = (ListTerm)args[0];
        
        NumberTerm Kt = (NumberTerm)args[1]; // instante conhecido (agora)
        this.known_time = Kt.solve();
        
        int i_pe = 0;                        // indice do primeiro evento
		Random rand = new Random();
		int choice = 0;
        
        for (Term t: Sch) {    // Todos os eventos da agenda
            ListTerm event = (ListTerm)t;    // Um evento específico
            NumberTerm et = (NumberTerm)event.get(1); // instante do evento
            if ( et.solve() < this.known_time ) {
            	/* se é passado aumenta o index do primeiro evento */
            	i_pe += 1;
            } else {
            	break;
            }
        }
        
    	if ( (Sch.size() - i_pe) > 1 ) { // pelo menos dois eventos no futuro
    		choice = rand.nextInt(2);
    		if (choice == 0) {
        		Sch = this.OneZeroExchange(ts, Sch, i_pe);    			
    		} else {
        		Sch = this.OneOneExchange(ts, Sch, i_pe);
    		}
    	}
    	return un.unifies(args[args.length-1], Sch);
    }
}
