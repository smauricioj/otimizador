// Agent driver in project auction

/* Initial beliefs and rules
 * schedule form -> [ [ci, ti, di, xi, yi] | for all i in schedule ]
 *     onde : c = cliente
 *            t = instante real de atendimento
 *            d = instante desejado de atendimento
 * 			  x, y = posi��o cartesiana de atendimento 
 * */

capacity(4).
init_pos([5,5]).
auctions_in_place([]).
schedule([["c0",0,0,5,5]]).
schedule_test([["c0",0,0,5,5],
	           ["c1",2,2,5,7], ["c2",6,5,8,7],
	           ["c2",10.6,0,5,5], ["c1",11.6,0,5,5]]).

/* Initial goals */

/* Plans */

+auction(St, [X, Y], KT, DT)[source(A)] : true
	<-  ?schedule(Sch);
		?schedule_test(Sch_t)
		?capacity(C);
		?init_pos(Ip);
		Value = math.random * 100 + 10;
		// TODO: custo de inser��o
		jia.schedule_cost(Sch_t, [5,5], 4, "drop", [1,1], 1, 1, Result);
		.print(Result)
		.send(A,tell,bid(Result));
		?auctions_in_place(L);
		.concat(L,[A],NL);
		.abolish(auctions_in_place(_));
		+auctions_in_place(NL)
		.
		
+winner(W)[source(A)] : auctions_in_place(L) & .member(A,L) &
						.my_name(N) & N = W
	<-  ?auction(St, [X, Y], KT, DT)[source(A)];
		?schedule(Sch);
		?init_pos(Ip);
		
		// TODO: inser��o de novos pedidos
		//	 jia.schedule_update(Sch, St, [X, Y], DT, NewSch)
		
		!!remove_auction_in_place(A)
		.

+winner(W)[source(A)] : auctions_in_place(L) & .member(A,L)
	<-	!!remove_auction_in_place(A).

+!remove_auction_in_place(A) : true
	<-	?auctions_in_place(L);
		.delete(A,L,NL);
		.abolish(auctions_in_place(_));
		+auctions_in_place(NL)
		.
		
{ include("$jacamoJar/templates/common-cartago.asl") }
{ include("$jacamoJar/templates/common-moise.asl") }

// uncomment the include below to have an agent compliant with its organisation
//{ include("$moiseJar/asl/org-obedient.asl") }
