// Agent client in project auction

/* Initial beliefs and rules */

deadline(2).

/* Initial goals */

/* Plans */
	   	
+next(N) : queue_number(N)
	<- 	.print("Iniciando");
	   	?service_point_x(X);
	   	?service_point_y(Y);
	   	?known_time(KT);
	   	?desired_time(DT);
	   	?service_type(ST);
	   	.df_search("driver",DL);
	   	.length(DL, TP);
	   	+total_participants(TP);
	   	.time(HH,MM,SS);
	   	+cpf_time( (60*60*HH)+(60*MM)+SS )
	   	.send(DL,tell, auction(ST, X, Y, KT, DT));
	   	!!decide.
	   	
+!decide :  total_participants(TP) & cpf_time(CFPTime) & deadline(Deadline) &
			.time(HH,MM,SS) & (60*60*HH)+(60*MM)+SS <= CFPTime + Deadline &
			.findall(b(V,A), bid(V)[source(A)], L) & .length(L, N) & N == TP
	<- 	.min(L,b(V,W));
		if (V >= 922337203685477580) {
			.print("Impossible to perform my request");
			.send("end_time",tell,infeasible)
		} else {
    		.print("Winner is ", W, " with ", V);
    		.broadcast(tell, winner(W));		
		}.
		   
+!decide :  total_participants(TP) & cpf_time(CFPTime) & deadline(Deadline) &
			.time(HH,MM,SS) & (60*60*HH)+(60*MM)+SS > CFPTime + Deadline &
			.findall(b(V,A), bid(V)[source(A)], L) & .length(L, N) & N >= 1
	<- 	.min(L,b(V,W));
		if (V >= 922337203685477580) {
			.print("Impossible to perform my request");
			.send("end_time",tell,infeasible)
		} else {
    		.print("Winner is ", W, " with ", V);
    		.broadcast(tell, winner(W));		
		}.
		
+!decide <-	.wait(30); !!decide.


{ include("$jacamoJar/templates/common-cartago.asl") }
{ include("$jacamoJar/templates/common-moise.asl") }

// uncomment the include below to have an agent compliant with its organisation
//{ include("$moiseJar/asl/org-obedient.asl") }
