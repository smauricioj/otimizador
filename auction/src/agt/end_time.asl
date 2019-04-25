// Agent end_time in project auction

/* Initial beliefs and rules */

/* Initial goals */

!start.

/* Plans */

+!start : .time(H,M,S)	<-  +initial_time(H,M,S).

+next(N) : queue_number(N) & end_time(E) & active(V) & .time(H,M,S) & .my_name(Name)
	<-	?initial_time(IH,IM,IS);
		jia.send_data(Name,((H-IH)*60*60)+((M-IM)*60)+S-IS)
		.broadcast(tell, end);
		.wait(E);
		if (V == true) {
			.stopMAS;
		}.

+infeasible : end_time(E)
	<-  .wait(E);
		if (V == true) {
			.stopMAS;
		}.
		
{ include("$jacamoJar/templates/common-cartago.asl") }
{ include("$jacamoJar/templates/common-moise.asl") }

// uncomment the include below to have an agent compliant with its organisation
//{ include("$moiseJar/asl/org-obedient.asl") }
