:- use_module(library('clp/bounds')).

coins(S, Count, Total) :-
 	% A=1, B=5, C=10, D=50, E=100
	S = [A, B, C, D, E],
	
	Av is   1,
	Bv is   5,
	Cv is  10,
	Dv is  50,
	Ev is 100,
	
	Aup is Total // Av,
	Bup is Total // Bv,
	Cup is Total // Cv,
	Dup is Total // Dv,
	Eup is Total // Ev,
	
	A in 0..Aup,
	B in 0..Bup,
	C in 0..Cup,
	D in 0..Dup,
	E in 0..Eup,
	
	VA #= A*Av,
	VB #= B*Bv,
	VC #= C*Cv,
	VD #= D*Dv,
	VE #= E*Ev,
	
	sum(S, #=, Count),
	VA + VB + VC + VD + VE #= Total,
	
	label(S).

%  :- findall(S, coins(S, 100, 500), Ss), halt.
 %:- coins(S, 100, 500), writeln(S), fail.

	
