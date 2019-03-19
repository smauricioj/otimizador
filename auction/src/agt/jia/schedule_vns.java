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
        ts.getAg().getLogger().info("executing internal action 'jia.schedule_vns'");
        
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
        
        int n_estrela = n_e - i_pe; // número de eventos no futuro
		ListTerm NewSch = Sch.cloneLT();
    	if ( n_estrela > 0 ) {
    		Random rand = new Random();   		
        	
        	for (int i = i_pe; i < n_estrela+i_pe; i ++) {		// todos os eventos futuros
        		int rand_event_index = rand.nextInt(n_estrela) + i_pe; 
        		
        	}  		
    	}
    	return un.unifies(args[args.length-1], NewSch);
    }
}
