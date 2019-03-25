// Internal action code for project auction

package jia;

import jason.*;
import jason.asSemantics.*;
import jason.asSyntax.*;
import java.util.List;
import java.util.ArrayList;

@SuppressWarnings("serial")
public class schedule_cost extends DefaultInternalAction {
	
	private String service_type = "";
	private String client_name = "_";
	private double service_position_x = 0;
	private double service_position_y = 0;
	private double desired_time = 0;
	private double known_time = 0;
	
	private ListTerm Sch_after_insertion(ListTerm Sch, int i, int j) throws NoValueException {
		/** Os eventos no Sch são definidos por:
    	 *  	[cliente, atendimento, desejado, x, y, tipo]
    	 *  Abaixo, dois eventos (buscar e levar) são criados
    	 *  de acordo com o cliente. **/
    	
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
        
        new_event_i.add(ASSyntax.createString(this.service_type.substring(1, this.service_type.length()-1)));
        new_event_j.add(ASSyntax.createString(this.service_type.substring(1, this.service_type.length()-1)));
    	
    	/** Os testes são realizados sobre um clone do agendamento
    	 *  Após a insersão em i e j, todos os eventos após i são
    	 *  atualizados, modificando seu tempo de atendimento de
    	 *  acordo com as distancias **/
        
    	Sch.add(j+1, new_event_j);
    	Sch.add(i+1, new_event_i);
    	
    	return functions.Sch_time_fit(Sch, i+1);
	}
	
	private double kappa_ij(ListTerm Sch, int i, int j, TransitionSystem ts) throws NoValueException {		
		/** Calcula custo da inserção do pedido em i e j **/
		
		ListTerm Internal_Sch = Sch.cloneLT();
    	
    	ListTerm Sch_insert = this.Sch_after_insertion(Internal_Sch, i, j);	
    	
    	/** As métricas de avaliação do agendamento são calculadas
    	 *  usando método e depois subtraídas, ponderando com
    	 *  os parâmetros de controle. Esse é o resultado final **/
    	
    	double[] metrics_base = functions.metrics(Sch, this.client_name, ts);
    	
    	double[] metrics = functions.metrics(Sch_insert, this.client_name, ts);
		
		return functions.metrics_diff_cost(metrics, metrics_base);
	}

    @Override
    public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {
        // execute the internal action
    	//	 jia.schedule_cost(Sch, St, X, Y, KT, DT, A, Result)
    	
        // ts.getAg().getLogger().info("executing internal action 'jia.schedule_cost'");
        if (!args[args.length-1].isVar()) {
        	throw new JasonException("Last argument of schedule_cost is not a variable");
        }
        
        ListTerm Sch = (ListTerm)args[0];    // agendamento atual
        
        int i_pe = 0;                        // indice do primeiro evento
        int n_e = Sch.size();                         // total de eventos
        
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

        Atom A = (Atom)args[6]; // nome do agente a ser atendido
        this.client_name = A.toString();
        
    	for (Term t: Sch) {    // Todos os eventos da agenda
            ListTerm event = (ListTerm)t;    // Um evento específico
            NumberTerm et = (NumberTerm)event.get(1); // instante do evento
            if ( et.solve() < this.known_time || et.solve() < this.desired_time) {
            	/* se é passado OU anterior ao desejado,
            	   aumenta o index do primeiro evento    */
            	i_pe += 1;
            } else {
            	break;
            }
        }
    	
    	double actValue = Double.POSITIVE_INFINITY;      // menor valor até agora
    	double minValue = actValue;        // valor atual
    	int min_i = 0;
    	int min_j = 0;
    	
    	int n_estrela = n_e - i_pe; // número de espaços disponíveis
    	if ( n_estrela == 0 ) { // caso só tenha como inserir no fim (é feio, eu sei)
    		i_pe = n_e - 1;
    		minValue = this.kappa_ij(Sch, i_pe, i_pe, ts);
			min_i = i_pe;
			min_j = i_pe;
    	} else {    	
	    	for (int i = 0; i < n_estrela; i ++) {		// número de linhas Kappa
	    		for (int j = 0; j < n_estrela; j ++) {	// número de colunas Kappa
	    			if (j >= i){
	    				// calcula o custo da inserção na triangular superior
	    				actValue = this.kappa_ij(Sch, i+i_pe, j+i_pe, ts);
	    			} else {
	    				continue;
	    			}
	    			
	    			if (actValue < minValue) {
	    				// se o atual é menor do que o menor até agora, atualiza
	    				minValue = actValue;
	    				min_i = i+i_pe;
	    				min_j = j+i_pe;
	    			}
	    		}
	    	}
    	}

        Sch = this.Sch_after_insertion(Sch, min_i, min_j);
    	
    	ListTerm result = ASSyntax.createList();
    	result.add(ASSyntax.createNumber(Math.round(minValue*10.0)/10.0));        
        result.add(ASSyntax.createList(Sch));
    	
        // unifica o resultado com a variável passada
    	return un.unifies(args[args.length-1], result);
    }
}






















