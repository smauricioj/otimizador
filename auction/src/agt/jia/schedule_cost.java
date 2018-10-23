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
    	Random rand = new Random(); //máquina de randoms
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
        
        StringTerm St = (StringTerm)args[1]; // tipo de serviço
        this.service_type = St.toString();
        
        NumberTerm Pos_x = (NumberTerm)args[2];    // posição x do novo pedido
        this.service_position_x = Pos_x.solve();
        
        NumberTerm Pos_y = (NumberTerm)args[3];    // posição y do novo pedido
        this.service_position_y = Pos_y.solve();
        
        NumberTerm Kt = (NumberTerm)args[4]; // instante conhecido (agora)
        this.known_time = Kt.solve();
        		
        NumberTerm Dt = (NumberTerm)args[5]; // instante desejado (no futuro)
        this.desired_time = Dt.solve();
        
    	for (Term t: Sch) {    // Todos os eventos da agenda
            ListTerm event = (ListTerm)t;    // Um evento específico
            NumberTerm et = (NumberTerm)event.get(1); // instante do evento
            if ( et.solve() < Kt.solve() || et.solve() < Dt.solve()) {
            	/* se é passado OU anterior ao desejado,
            	   aumenta o index do primeiro evento    */ 
            	i_pe += 1;
            }
            n_e += 1;
        }
    	
    	int n_estrela = n_e - i_pe; // número de espaços disponíveis
    	double inf = Double.POSITIVE_INFINITY; // infinito
    	double minValue = inf;      // menor valor até agora
    	double actValue = 0;        // valor atual
    	for (int i = 0; i < n_estrela; i ++) {		// número de linhas
    		for (int j = 0; j < n_estrela; j ++) {	// número de colunas
    			if (j < i) {
    				// a matriz deve ser triangular superior
    				actValue = inf;
    			} else {
    				// calcula o custo da inserção
    				actValue = this.kappa_ij(Sch, i+n_estrela, j+n_estrela);
    			}
    			
    			if (actValue < minValue) {
    				// se o atual é menor do que o menor até agora, atualiza
    				minValue = actValue;
    			}
    		}
    	}

        // unifica o resultado com a variável passada
    	return un.unifies(args[args.length-1], ASSyntax.createNumber(minValue));
    }
}






















