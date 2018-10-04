// Agent driver in project auction

/* Initial beliefs and rules */

capacity(4).
init_pos_x(5).
init_pos_y(5).
schedule_clients([]).
schedule_times([]).
schedule_positions([]).

/* Initial goals */

/* Plans */

+auction(ST, X, Y, KT, DT)[source(A)] : true
	<-  .send(A,tell,bid(math.random * 100 + 10))
		.
	
+winner(W)[source(A)] : .my_name(N) & N = W
	<-  .print("Venci");
		?auction(ST, X, Y, KT, DT)[source(A)];
		?schedule_clients(SC);
		?schedule_times(ST);
		?schedule_positions(SP);
		?capacity(C);
		
		// TODO: calculo de inserção de novos pedidos
		
		.concat(SC,[A],New_SC);
		.concat(SP,[[X,Y]],New_SP);
		
		.abolish(schedule_clients(_));
		.abolish(schedule_positions(_));
		
		+schedule_clients(New_SC);
		+schedule_positions(New_SP)		
		.

{ include("$jacamoJar/templates/common-cartago.asl") }
{ include("$jacamoJar/templates/common-moise.asl") }

// uncomment the include below to have an agent compliant with its organisation
//{ include("$moiseJar/asl/org-obedient.asl") }
