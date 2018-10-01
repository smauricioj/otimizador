// Agent driver in project auction

/* Initial beliefs and rules */

pos_x(5).
pos_y(5).
velocity(1).
schedule_clients([]).
schedule_times([]).

/* Initial goals */

// !start.

/* Plans */

+auction(X, Y, KT, DT)[source(A)] : true
	<-  .send(A,tell,bid(math.random * 100 + 10)).
	
+winner(W)[source(A)] : .my_name(N) & N = M & schedule_clients(SC)
	<-  .print("Venci");
		.concat(SC,[A],New_SC);
		.abolish(schedule_clients(_));
		+schedule_clients(New_SC).

{ include("$jacamoJar/templates/common-cartago.asl") }
{ include("$jacamoJar/templates/common-moise.asl") }

// uncomment the include below to have an agent compliant with its organisation
//{ include("$moiseJar/asl/org-obedient.asl") }
