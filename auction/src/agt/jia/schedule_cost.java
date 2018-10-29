// Internal action code for project auction

package jia;

import jason.*;
import jason.asSemantics.*;
import jason.asSyntax.*;
import java.util.Random;

@SuppressWarnings("serial")
public class schedule_cost extends DefaultInternalAction {
	
	private String service_type = "";
	private String client_name = "_";
	private double service_position_x = 0;
	private double service_position_y = 0;
	private double desired_time = 0;
	private double known_time = 0;
	
	
	private double kappa_ij(ListTerm Sch, int i, int j) throws NoValueException {		
		/** Calcula custo da inser��o do pedido em i e j **/
		
    	Random rand = new Random(); //m�quina de randoms
    	double inf = Double.POSITIVE_INFINITY; // infinito
    	
    	/** Os eventos no Sch s�o definidos por:
    	 *  	[cliente, atendimento, desejado, x, y]
    	 *  Abaixo, dois eventos (buscar e levar) s�o criados
    	 *  de acordo com o cliente. **/
    	
	private double kappa_ij(ListTerm Sch, int i, int j) throws NoValueException {
    	Random rand = new Random(); //m�quina de randoms
    	double inf = Double.POSITIVE_INFINITY; // infinito
    	
    	ListTerm new_event_i = ASSyntax.createList(ASSyntax.createString(this.client_name),
    											   ASSyntax.createNumber(0),
    			                                   ASSyntax.createNumber(this.desired_time));
    	
    	ListTerm new_event_j = ASSyntax.createList(ASSyntax.createString(this.client_name),
				   							       ASSyntax.createNumber(0),
								                   ASSyntax.createNumber(this.desired_time));
    	
    	if ( this.service_type.equals("\"drop\"") ) {
    		new_event_i.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_X));
    		new_event_i.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_Y));
    		
    		new_event_j.add(ASSyntax.createNumber(this.service_position_x));
    		new_event_j.add(ASSyntax.createNumber(this.service_position_y));    		
    	} else {
    		new_event_j.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_X));
    		new_event_j.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_Y));
    		
    		new_event_i.add(ASSyntax.createNumber(this.service_position_x));
    		new_event_i.add(ASSyntax.createNumber(this.service_position_y));    		
    	}
    	
    	/** Os testes s�o realizados sobre um clone do agendamento
    	 *  Ap�s a insers�o em i e j, todos os eventos ap�s i s�o
    	 *  atualizados, modificando seu tempo de atendimento de
    	 *  acordo com as distancias **/
    	
    	ListTerm Sch_novo = Sch.cloneLT();
    	Sch_novo.add(i+1, new_event_i);
    	Sch_novo.add(j+2, new_event_j);
//    	System.out.println(" "+i+" "+j+" ");
    	for ( int index = i+1; index < Sch_novo.size(); index++ ) {
    		ListTerm event = (ListTerm)Sch_novo.get(index);
    		ListTerm last_event = (ListTerm)Sch_novo.get(index-1);

    		NumberTerm t0Term = (NumberTerm)last_event.get(1);
    		NumberTerm x0Term = (NumberTerm)last_event.get(3);
    		NumberTerm y0Term = (NumberTerm)last_event.get(4);
    		NumberTerm x1Term = (NumberTerm)event.get(3);
    		NumberTerm y1Term = (NumberTerm)event.get(4);
    		double x0 = x0Term.solve();
			double y0 = y0Term.solve();
			double x1 = x1Term.solve();
			double y1 = y1Term.solve();
    		double tempo_viagem = Math.round( Math.sqrt( Math.pow(x0-x1, 2) + Math.pow(y0-y1, 2) ) );
    		double instante_atendimento = t0Term.solve() + parameters.SERVICE_TIME + tempo_viagem;
			event.set(1, ASSyntax.createNumber(instante_atendimento));
    		
    		Sch_novo.set(index, event);
    	}
    	
    	System.out.println(Sch_novo);
    	
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






















