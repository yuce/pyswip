% This example is adapted from http://eclipse.crosscoreop.com/examples/puzzle1.pl.txt

:- use_module(library('bounds')).

solve(Board) :-
	Board = [NW,N,NE,W,E,SW,S,SE],
	Board in 0..12,
	sum(Board, #=, 12),
	NW + N + NE #= 5,
	NE + E + SE #= 5,
	NW + W + SW #= 5,
	SW + S + SE #= 5,

	label(Board).
