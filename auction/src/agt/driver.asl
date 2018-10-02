// Agent driver in project auction

/* Initial beliefs and rules */

init_pos_x(5).
init_pos_y(5).
schedule_clients([]).
schedule_times([]).
schedule_positions([]).

/* Initial goals */

/* Plans */

+auction(X, Y, KT, DT)[source(A)] : true
	<-  .send(A,tell,bid(math.random * 100 + 10)).
	
+winner(W)[source(A)] : .my_name(N) & N = W
	<-  .print("Venci");
		?schedule_clients(SC);
		.concat(SC,[A],New_SC);
		.abolish(schedule_clients(_));
		+schedule_clients(New_SC).

{ include("$jacamoJar/templates/common-cartago.asl") }
{ include("$jacamoJar/templates/common-moise.asl") }

// uncomment the include below to have an agent compliant with its organisation
//{ include("$moiseJar/asl/org-obedient.asl") }
