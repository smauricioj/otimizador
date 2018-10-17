// Internal action code for project auction

package jia;

import jason.*;
import jason.asSemantics.*;
import jason.asSyntax.*;

@SuppressWarnings("serial")
public class schedule_cost extends DefaultInternalAction {
	//	 jia.schedule_cost(Sch, C, Ip, St, [X, Y], KT, DT, Result)

    @Override
    public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {
        // execute the internal action
    	
        ts.getAg().getLogger().info("executing internal action 'jia.schedule_cost'");
        // TODO: verificar código abaixo
        //if (!args[args.length-2].isVar()) {
        //	throw new JasonException("Last argument of schedule_cost is not a variable");
        //}
        
        int i_pe = 0;
        int n_e = 0;
        NumberTerm kt = (NumberTerm)args[5];
        NumberTerm dt = (NumberTerm)args[6];
    	for (Term t: (ListTerm)args[0]) { // Todos os eventos da agenda
            ListTerm event = (ListTerm)t; // Um evento específico
            NumberTerm et = (NumberTerm)event.get(1); // instante do evento
            if ( et.solve() < kt.solve() || et.solve() < dt.solve()) {
            	// se é passado OU anterior ao desejado, aumenta o index do primeiro evento 
            	i_pe += 1;
            }
            n_e += 1;
        }
    	
    	int n_estrela = n_e - i_pe;    	
    	int [][] K = new int[n_estrela][n_estrela];    	

        // everything ok, so returns true
        return true;
    }
}
