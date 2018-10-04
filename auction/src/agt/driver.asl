// Agent driver in project auction

/* Initial beliefs and rules */

capacity(4).
init_pos_x(5).
init_pos_y(5).
auctions_in_place([]).
schedule_clients([]).
schedule_times([]).
schedule_positions([]).

/* Initial goals */

/* Plans */

+auction(St, X, Y, KT, DT)[source(A)] : true
	<-  .send(A,tell,bid(math.random * 100 + 10));
		?auctions_in_place(L);
		.concat(L,[A],NL);
		.abolish(auctions_in_place(_));
		+auctions_in_place(NL)
		.
		
+winner(W)[source(A)] : auctions_in_place(L) & .member(A,L) &
						.my_name(N) & N = W
	<-  ?auction(St, X, Y, KT, DT)[source(A)];
		?schedule_clients(SC);
		?schedule_times(ST);
		?schedule_positions(SP);
		?capacity(C);
		
		// TODO: calculo de inserção de novos pedidos
		
		.concat(SC,[A],New_SC);
		.concat(SP,[[X,Y]],New_SP);
		
		.abolish(schedule_clients(_));
		.abolish(schedule_positions(_));
		
		+schedule_clients(New_SC);
		+schedule_positions(New_SP);
		
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
