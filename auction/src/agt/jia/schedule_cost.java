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
	private double service_position_x = 0;
	private double service_position_y = 0;
	private double desired_time = 0;
	private double known_time = 0;
	
	private double kappa_ij(ListTerm Sch, int i, int j) {
    	Random rand = new Random(); //m�quina de randoms
    	double inf = Double.POSITIVE_INFINITY; // infinito
    	
    	ListTerm Sch_teste = Sch.cloneLT();
    	int count = 0;
    	for (Term t : Sch_teste) {
    		ListTerm event = (ListTerm)t;
    		
    		count += 1;
    	}
    	
//    	System.out.println(" "+i+" "+j+" "+Sch_teste);
    	
//    	Sch_teste.add(1, (Term)1);
		
		return rand.nextInt(50)+1;
	}

    @Override
    public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {
        // execute the internal action
    	//	 jia.schedule_cost(Sch, St, X, Y, KT, DT, Result)
    	
        ts.getAg().getLogger().info("executing internal action 'jia.schedule_cost'");
        if (!args[args.length-1].isVar()) {
        	throw new JasonException("Last argument of schedule_cost is not a variable");
        }
        
//        System.out.println(parameters.VEHICLE_CAPACITY);
        
        int i_pe = 0;                        // indice do primeiro evento
        int n_e = 0;                         // total de eventos
        ListTerm Sch = (ListTerm)args[0];    // agendamento atual
        
        StringTerm St = (StringTerm)args[1]; // tipo de servi�o
        this.service_type = St.toString();
        
        NumberTerm Pos_x = (NumberTerm)args[2];    // posi��o x do novo pedido
        this.service_position_x = Pos_x.solve();
        
        NumberTerm Pos_y = (NumberTerm)args[3];    // posi��o y do novo pedido
        this.service_position_y = Pos_y.solve();
        
        NumberTerm Kt = (NumberTerm)args[4]; // instante conhecido (agora)
        this.known_time = Kt.solve();
        		
        NumberTerm Dt = (NumberTerm)args[5]; // instante desejado (no futuro)
        this.desired_time = Dt.solve();
        
    	for (Term t: Sch) {    // Todos os eventos da agenda
            ListTerm event = (ListTerm)t;    // Um evento espec�fico
            NumberTerm et = (NumberTerm)event.get(1); // instante do evento
            if ( et.solve() < Kt.solve() || et.solve() < Dt.solve()) {
            	/* se � passado OU anterior ao desejado,
            	   aumenta o index do primeiro evento    */
            	i_pe += 1;
            }
            n_e += 1;
        }
    	
    	int n_estrela = n_e - i_pe; // n�mero de espa�os dispon�veis
    	if ( n_e == 1 ) { // caso primeira inser��o do motorista (� feio, eu sei)
    		n_estrela = 1;
    		i_pe = 0;
    	}
//    	System.out.println("n_estrela � "+n_estrela+" e  os outros s�o "+n_e+" "+i_pe);
    	double inf = Double.POSITIVE_INFINITY; // infinito
    	double minValue = inf;      // menor valor at� agora
    	double actValue = 0;        // valor atual
    	for (int i = 0; i < n_estrela; i ++) {		// n�mero de linhas
    		for (int j = 0; j < n_estrela; j ++) {	// n�mero de colunas
    			if (j >= i){
    				// calcula o custo da inser��o na triangular superior
    				actValue = this.kappa_ij(Sch, i+i_pe, j+i_pe);
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






















