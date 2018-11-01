// Agent driver in project auction

/* Initial beliefs and rules
 * schedule form -> [ [ci, ti, di, xi, yi] | for all i in schedule ]
 *     onde : c = cliente
 *            t = instante real de atendimento
 *            d = instante desejado de atendimento
 * 			  x, y = posicao cartesiana de atendiment * */

auctions_in_place([]).
schedule([["c0",0,0,5,5]]).
schedule_test([["c0",0,0,5,5],
	           ["c1",2,2,5,7], ["c2",6,5,8,7],
	           ["c2",10.6,10.6,5,5], ["c1",11.6,11.6,5,5]]).

/* Initial goals */

/* Plans */

+auction(St, X, Y, KT, DT)[source(A)] : true
	<-  ?schedule(Sch);
		jia.schedule_cost(Sch, St, X, Y, Kt, Dt, Result);
		.nth(0,Result,Bid_value);		
		.nth(1,Result,Insertion_i);
		.nth(2,Result,Insertion_j);
		.send(A,tell,bid(Bid_value));
		?auctions_in_place(L);
		.concat(L,[[A, Insertion_i, Insertion_j]],NL);
		.abolish(auctions_in_place(_));
		+auctions_in_place(NL)
		.
		
+winner(W)[source(A)] : auctions_in_place(L) & .member([A,I_i,I_j],L) &
						.my_name(N) & N = W
	<-  ?auction(St, X, Y, KT, DT)[source(A)];
		?schedule(Sch);
		
		// TODO: insercao de novos pedid		
		jia.schedule_update(Sch, I_i, I_j, St, X, Y, Dt, A, NewSch)
		.print(NewSch);
		
		!!remove_auction_in_place(A)
		.

+winner(W)[source(A)] : auctions_in_place(L) & .member(A,L)
	<-	!!remove_auction_in_place(A).
		
+!remove_auction_in_place(A) : true
	<-	?auctions_in_place(L);
		.delete([A,_,_],L,NL);
		.abolish(auctions_in_place(_));
		+auctions_in_place(NL)
		.
		
{ include("$jacamoJar/templates/common-cartago.asl") }
{ include("$jacamoJar/templates/common-moise.asl") }

// uncomment the include below to have an agent compliant with its organisation
//{ include("$moiseJar/asl/org-obedient.asl") }
