// Agent end_time in project auction

/* Initial beliefs and rules */

/* Initial goals */

/* Plans */

+next(N) : queue_number(N) & end_time(E)
	<-	.broadcast(tell, end);
		.wait(E);
		.stopMAS.

+infeasible : end_time(E)
	<-  .wait(E);
		.stopMAS.
		
{ include("$jacamoJar/templates/common-cartago.asl") }
{ include("$jacamoJar/templates/common-moise.asl") }

// uncomment the include below to have an agent compliant with its organisation
//{ include("$moiseJar/asl/org-obedient.asl") }
