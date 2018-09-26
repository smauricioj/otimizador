// Agent client in project auction

/* Initial beliefs and rules */

/* Initial goals */

!start.

/* Plans */

+!start	: known_time(KT) & desired_time(DT) &
	      service_point_x(X) & service_point_y(Y)
	<- // .wait(KT * 1000);
	   .print("Iniciando")
	   .broadcast(tell, auction(service, transport(X, Y, DT)));
	   .at("now + 1 s", {+!decide(transport(X, Y, DT))}).
	   
+!decide(Service) : .findall(b(V,A), bid(Service,V)[source(A)],L) &
                   .length(L,N) &
                   N >= 1
	<- .min(L,b(V,W));
	   .print("Winner for ", Service, " is ", W, " with ", V);
	   .broadcast(tell, winner(Service, W)).
                   

{ include("$jacamoJar/templates/common-cartago.asl") }
{ include("$jacamoJar/templates/common-moise.asl") }

// uncomment the include below to have an agent compliant with its organisation
//{ include("$moiseJar/asl/org-obedient.asl") }
