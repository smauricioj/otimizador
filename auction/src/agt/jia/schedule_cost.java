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
	
	private double kappa_ij(ListTerm Sch, int i, int j, TransitionSystem ts) throws NoValueException {		
		/** Calcula custo da inserção do pedido em i e j **/
		
    	double[] metrics_base = functions.metrics(Sch, this.client_name, ts);
    	
    	/** Os eventos no Sch são definidos por:
    	 *  	[cliente, atendimento, desejado, x, y]
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
    		double tempo_viagem = functions.travel_distance(event, last_event);
    		double instante_atendimento = t0Term.solve() + parameters.SERVICE_TIME + tempo_viagem;
    		event.set(1, ASSyntax.createNumber(Math.max(this.desired_time, instante_atendimento)));
    		
    		Sch_novo.set(index, event);
    	}    	
    	
    	/** As métricas de avaliação do agendamento são calculadas
    	 *  usando método interno e depois somadas, ponderando com
    	 *  os parâmetros de controle. Esse é o resultado final **/
    	
    	double[] metrics = functions.metrics(Sch_novo, this.client_name, ts);
    	
    	//ts.getAg().getLogger().info("metrics_1_distancia -> "+metrics[0]);
    	//ts.getAg().getLogger().info("metrics_2_distancia -> "+metrics_base[0]);
    	//ts.getAg().getLogger().info("--------------------------------------");
    	//ts.getAg().getLogger().info("metrics_1_atraso -> "+metrics[1]);
    	//ts.getAg().getLogger().info("metrics_2_atraso -> "+metrics_base[1]);
    	//ts.getAg().getLogger().info("--------------------------------------");
    	//ts.getAg().getLogger().info("metrics_1_tempo -> "+metrics[2]);
    	//ts.getAg().getLogger().info("metrics_2_tempo -> "+metrics_base[2]);
    	//ts.getAg().getLogger().info("--------------------------------------");
		
		return functions.metrics_insertion_cost(metrics, metrics_base);
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
    	int min_i = Integer.MAX_VALUE;
    	int min_j = Integer.MAX_VALUE;
    	
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
    	
    	ListTerm result = ASSyntax.createList();
    	result.add(ASSyntax.createNumber(Math.round(minValue)));

        /** Os eventos no Sch são definidos por:
         *      [cliente, atendimento, desejado, x, y]
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
            
            new_event_j.add(ASSyntax.createNumber(this.service_position_x));
            new_event_j.add(ASSyntax.createNumber(this.service_position_y));          
        } else {
            new_event_j.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_X));
            new_event_j.add(ASSyntax.createNumber(parameters.VEHICLE_INITIAL_POSITION_Y));
            
            new_event_i.add(ASSyntax.createNumber(this.service_position_x));
            new_event_i.add(ASSyntax.createNumber(this.service_position_y));          
        }
        
        /** Os testes são realizados sobre um clone do agendamento
         *  Após a insersão em i e j, todos os eventos após i são
         *  atualizados, modificando seu tempo de atendimento de
         *  acordo com as distancias **/
        
        ListTerm Sch_novo = Sch.cloneLT();
        Sch_novo.add(min_j+1, new_event_j);
        Sch_novo.add(min_i+1, new_event_i);
        for ( int index = min_i+1; index < Sch_novo.size(); index++ ) {
            ListTerm event = (ListTerm)Sch_novo.get(index);
            ListTerm last_event = (ListTerm)Sch_novo.get(index-1);

            NumberTerm t0Term = (NumberTerm)last_event.get(1);
            double tempo_viagem = functions.travel_distance(event, last_event);
            double instante_atendimento = t0Term.solve() + parameters.SERVICE_TIME + tempo_viagem;
            event.set(1, ASSyntax.createNumber(Math.max(Dt.solve(), instante_atendimento)));
            
            Sch_novo.set(index, event);
        }
        
        result.add(ASSyntax.createList(Sch_novo));
    	
        // unifica o resultado com a variável passada
    	return un.unifies(args[args.length-1], result);
    }
}






















