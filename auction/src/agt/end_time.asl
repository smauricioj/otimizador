// Agent end_time in project auction

/* Initial beliefs and rules */

/* Initial goals */

!start.

/* Plans */

+!start : .time(H,M,S)	<-  +initial_time(H,M,S).

+infeasible : active(V)
	<- if (V == true) {
			.stopMAS;
		}.

+next(N) : queue_number(N) & end_time(E) & .time(H,M,S) & .my_name(Name)
	<-	?initial_time(IH,IM,IS);
		jia.send_data(Name,((H-IH)*60*60)+((M-IM)*60)+S-IS)
		.df_search("driver", DL);
	   	.length(DL, TD);
	   	+total_drivers(TD);
	   	.send(DL,tell, end);
	   	!!end_all.
		
+!end_all : .findall(b(V,A), end_ok[source(A)], L) & .length(L, N) & total_drivers(TD) & N == TD & active(V)
	<-	if (V == true) {
			.stopMAS;
		}.
		
+!end_all : true <- .wait(10); !!end_all.
		
{ include("$jacamoJar/templates/common-cartago.asl") }
{ include("$jacamoJar/templates/common-moise.asl") }

// uncomment the include below to have an agent compliant with its organisation
//{ include("$moiseJar/asl/org-obedient.asl") }
