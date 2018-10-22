// Internal action code for project auction

package jia;

import jason.*;
import jason.asSemantics.*;
import jason.asSyntax.*;
import java.util.Random;

@SuppressWarnings("serial")
public class schedule_cost extends DefaultInternalAction {
	//	 jia.schedule_cost(Sch, C, St, [X, Y], KT, DT, Result)

    @Override
    public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {
        // execute the internal action
    	
        ts.getAg().getLogger().info("executing internal action 'jia.schedule_cost'");
        if (!args[args.length-1].isVar()) {
        	throw new JasonException("Last argument of schedule_cost is not a variable");
        }
        
        int i_pe = 0;                        //indice do primeiro evento
        int n_e = 0;                         //total de eventos
        NumberTerm kt = (NumberTerm)args[5]; // instante conhecido (agora)
        NumberTerm dt = (NumberTerm)args[6]; // instante desejado (no futuro)
    	for (Term t: (ListTerm)args[0]) {    // Todos os eventos da agenda
            ListTerm event = (ListTerm)t;    // Um evento espec�fico
            NumberTerm et = (NumberTerm)event.get(1); // instante do evento
            if ( et.solve() < kt.solve() || et.solve() < dt.solve()) {
            	/* se � passado OU anterior ao desejado,
            	   aumenta o index do primeiro evento    */ 
            	i_pe += 1;
            }
            n_e += 1;
        }
    	
    	int n_estrela = n_e - i_pe; // n�mero de espa�os dispon�veis
    	double inf = Double.POSITIVE_INFINITY; // infinito
    	double minValue = inf;      // menor valor at� agora
    	double actValue = 0;        // valor atual
    	Random rand = new Random(); //m�quina de randoms
    	for (int i = 0; i < n_estrela; i ++) {		// n�mero de linhas
    		for (int j = 0; j < n_estrela; j ++) {	// n�mero de colunas
    			if (j < i) {
    				// a matriz deve ser triangular superior
    				actValue = inf;
    			} else {
    				// calcula o custo da inser��o
    				// TODO: calculo do kappa_ij
    				actValue = rand.nextInt(50)+1;
    			}
    			
    			if (actValue < minValue) {
    				// se o atual � menor do que o menor at� agora, atualiza
    				minValue = actValue;
    			}
    		}
    	}

        // unifica o resultado com a vari�vel passada
    	return un.unifies(args[args.length-1], ASSyntax.createNumber(minValue));
    }
}






















