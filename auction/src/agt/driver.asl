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

+auction(service, D)[source(A)] : true <- .send(A,tell,bid(D, math.random * 100 + 10));
                                          .print("Respondendo").

{ include("$jacamoJar/templates/common-cartago.asl") }
{ include("$jacamoJar/templates/common-moise.asl") }

// uncomment the include below to have an agent compliant with its organisation
//{ include("$moiseJar/asl/org-obedient.asl") }
