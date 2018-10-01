// Agent client in project auction

/* Initial beliefs and rules */

/* Initial goals */

!start.

/* Plans */

+!start	: known_time(KT)     & desired_time(DT)   &
	      service_point_x(X) & service_point_y(Y)
	<- // .wait(KT * 1000);
	   .print("Iniciando")
	   .broadcast(tell, auction(X, Y, KT, DT));
	   .at("now + 1 s", {+!decide}).
	   
+!decide : .findall(b(V,A), bid(V)[source(A)], L) &
           .length(L, N)
	<- if (N >= 1) {
		.min(L,b(V,W));
	    .print("Winner is ", W, " with ", V);
	    .broadcast(tell, winner(W));
	} else {
		.print("No response, giving up");
	}.

{ include("$jacamoJar/templates/common-cartago.asl") }
{ include("$jacamoJar/templates/common-moise.asl") }

// uncomment the include below to have an agent compliant with its organisation
//{ include("$moiseJar/asl/org-obedient.asl") }
