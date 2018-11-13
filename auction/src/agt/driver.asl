// Agent driver in project auction

/* Initial beliefs and rules
 * schedule form -> [ [ci, ti, di, xi, yi] | for all i in schedule ]
 *     onde : c = cliente
 *            t = instante real de atendimento
 *            d = instante desejado de atendimento
 * 			  x, y = posicao cartesiana de atendimento */

schedule([["c0",0,0,5,5]]).

/* Initial goals */

/* Plans */

+auction(St, X, Y, KT, DT)[source(A)] : true
	<-  ?schedule(Sch);
		jia.schedule_cost(Sch, St, X, Y, KT, DT, Result);
		.nth(0,Result,Bid_value);		
		.nth(1,Result,I_i);
		.nth(2,Result,I_j);
		.print(Bid_value);
		+bid_done(A,I_i,I_j);
		.send(A,tell,bid(Bid_value));
		.
		
+winner(W)[source(A)] : .my_name(N) & N = W
	<-  ?auction(St, X, Y, KT, DT)[source(A)];
		?schedule(Sch);
		?bid_done(A,I_i,I_j);	
		jia.schedule_update(Sch, I_i, I_j, St, X, Y, DT, A, NewSch);
		.print(NewSch);
		-+schedule(NewSch).
		
+end : .my_name(N)
	<-	?schedule(Sch);
		jia.send_data(N,Sch).

{ include("$jacamoJar/templates/common-cartago.asl") }
{ include("$jacamoJar/templates/common-moise.asl") }

// uncomment the include below to have an agent compliant with its organisation
//{ include("$moiseJar/asl/org-obedient.asl") }
