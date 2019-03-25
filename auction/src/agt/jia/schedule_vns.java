// Internal action code for project auction

package jia;

import java.util.Random;

import jason.*;
import jason.asSemantics.*;
import jason.asSyntax.*;

@SuppressWarnings("serial")
public class schedule_vns extends DefaultInternalAction {
	
	private double known_time = 0;

    @Override
    public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {
        // execute the internal action
    	//   	 jia.schedule_vns(Sch, KT, NewSch)
        // ts.getAg().getLogger().info("executing internal action 'jia.schedule_vns'");
        
        ListTerm Sch = (ListTerm)args[0];
        
        int i_pe = 0;                        // indice do primeiro evento
        int n_e = Sch.size();                         // total de eventos
        
        NumberTerm Kt = (NumberTerm)args[1]; // instante conhecido (agora)
        this.known_time = Kt.solve();
        
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
        
    	if ( n_e - i_pe > 1 ) { // pelo menos dois eventos no futuro            
    		ListTerm NewSch = Sch.cloneLT();
    		ListTerm Sch_backup = Sch.cloneLT();
    		double [] Sch_metrics = functions.metrics(Sch, "", ts);
    		double [] NewSch_metrics = functions.metrics(NewSch, "", ts);
    		double vns_cost = Double.MAX_VALUE;
    		// Random rand = new Random();
    		// int rand_event_index = rand.nextInt(n_estrela) + i_pe;
    		
    		OUTER_LOOP: 
	        	for (int index = i_pe+1; index < n_e; index++) {		// todos os eventos futuros
	        		Term event = NewSch.remove(index);
	        		ListTerm NewSch_backup = NewSch.cloneLT();
	        		for (int next_index = i_pe+1; next_index < n_e; next_index++) { // todos os eventos futuros
	        			if (index != next_index) 	{  // para eventos diferentes
	            			NewSch.add(next_index, event);
	            			NewSch = functions.Sch_time_fit(NewSch, next_index-1);
	            			NewSch_metrics = functions.metrics(NewSch, "", ts);
	            			vns_cost = functions.metrics_diff_cost(NewSch_metrics, Sch_metrics);
	            			if (vns_cost < 0) {
	            				Sch = NewSch;
	            				break OUTER_LOOP;
	            			}
	        			}
        				NewSch = NewSch_backup.cloneLT();			
	        		}
	        		NewSch = Sch_backup.cloneLT();
	        	}  		
    	}
    	return un.unifies(args[args.length-1], Sch);
    }
}
