// Agent driver in project auction

/* Initial beliefs and rules */

capacity(4).
init_pos([5,5]).
auctions_in_place([]).
schedule([[0,0,5,5]]).

/* Initial goals */

/* Plans */

+auction(St, [X, Y], KT, DT)[source(A)] : true
	<-  ?schedule(Sch);
		?capacity(C);
		?init_pos(Ip);
		Value = math.random * 100 + 10;
		// TODO: custo de inserção
		//	jia.schedule_cost(Sch, Ip, C, St, [X, Y], KT, DT, Cost)
		jia.schedule_cost([["oi",0,5,5],["banana",5,8,6],["ultimo",7,1,1]],[5,5],4,"drop",[1,1],5,5,A);
		.send(A,tell,bid(Value));
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
		
		// TODO: inserção de novos pedidos
		//	 jia.schedule_update(Sch, Ip, St, [X, Y], KT, DT, NewSch)
		
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
