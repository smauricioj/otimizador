// Agent client in project auction

/* Initial beliefs and rules */

/* Initial goals */

/* Plans */
	   	
+next(N) : queue_number(N) & .df_search("driver",DL)
	<- 	.print("Iniciando");
	   	?service_point_x(X);
	   	?service_point_y(Y);
	   	?known_time(KT);
	   	?desired_time(DT);
	   	?service_type(ST)
	   	.send(DL,tell, auction(ST, X, Y, KT, DT));
	   	.at("now + 1 s", {+!decide}) .
	   
+!decide : .findall(b(V,A), bid(V)[source(A)], L) & .length(L, N) & N >= 1
	<- 	.min(L,b(V,W));
		if (V >= 9223372036854775800) {
			.print("Impossible to perform my request");
			.send("end_time",tell,infeasible)
		} else {
    		.print("Winner is ", W, " with ", V);
    		.broadcast(tell, winner(W));
    		inc;			
		}.
		
+!decide <-	.wait(30); !!decide.


{ include("$jacamoJar/templates/common-cartago.asl") }
{ include("$jacamoJar/templates/common-moise.asl") }

// uncomment the include below to have an agent compliant with its organisation
//{ include("$moiseJar/asl/org-obedient.asl") }
