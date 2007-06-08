%TO convert to gnuprolog remove the following two lines.
%:- use_module(library(clpfd)).
%:- use_module(library(lists)).
:- use_module(library('clp/bounds')).
%then search and replace all_different to fd_all_different

%It should all work.

%I got bored so I coded up a Su Doku solver in prolog using constraints.
%It took less than 30 minutes (mainly because I don't type that fast).
%Searching  on the net people have produced 1.2mb visual basic monsters
%or Apple apps that took 8 hours to code.
%Constraint programming is fast and powerful. Of course there are no bells
%or whistles in this code.

%Look at test1,test2 and see how they are run.
%This is the sicstus version.
/* 
To Run the code in sicstus,either do it via emacs or
from a shell type
 sicstus

The sicstus prompt is then | ?-

So
| ?- [sudoku].

This loads the program

| ?- test1.
This calls test1.

It should be pretty obvious how to modify it to for you current puzzel.

 

*/

test_hard :-
L = [
            [_,_,1,_,8,_,6,_,4],
            [_,3,7,6,_,_,_,_,_],
            [5,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,5,_,_,_],
            [_,_,6,_,1,_,8,_,_],
            [_,_,_,4,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,3],
            [_,_,_,_,_,7,5,2,_],
            [8,_,2,_,9,_,7,_,_]
          ],
          sudoku(L).
%          pretty_print(L).

%Expects a list of lists 9 by 9 grid.
sudoku(L) :-
	flatten(L,AllVars),
%	domain(AllVars,1,9),
    AllVars in 1..9,
	[R1,R2,R3,R4,R5,R6,R7,R8,R9] = L,
%Each row is different.
	all_different(R1), all_different(R2), all_different(R3),
	all_different(R4), all_different(R5), all_different(R6),
	all_different(R7), all_different(R8), all_different(R9),
	transpose(L,TL),
%Each column is different.
	[C1,C2,C3,C4,C5,C6,C7,C8,C9] = TL,
	all_different(C1), all_different(C2), all_different(C3),
	all_different(C4), all_different(C5), all_different(C6),
	all_different(C7), all_different(C8), all_different(C9),
%Need to put the code in to do each 3x3 square all different.
%There is a much more elegant way of coding this. But for
%illustrative purposes it is fine.
	[X11,X12,X13,X14,X15,X16,X17,X18,X19] = R1,
	[X21,X22,X23,X24,X25,X26,X27,X28,X29] = R2,
	[X31,X32,X33,X34,X35,X36,X37,X38,X39] = R3,
	[X41,X42,X43,X44,X45,X46,X47,X48,X49] = R4,
	[X51,X52,X53,X54,X55,X56,X57,X58,X59] = R5,
	[X61,X62,X63,X64,X65,X66,X67,X68,X69] = R6,
	[X71,X72,X73,X74,X75,X76,X77,X78,X79] = R7,
	[X81,X82,X83,X84,X85,X86,X87,X88,X89] = R8,
	[X91,X92,X93,X94,X95,X96,X97,X98,X99] = R9,
	
	all_different([X11,X12,X13,X21,X22,X23,X31,X32,X33]),
	all_different([X41,X42,X43,X51,X52,X53,X61,X62,X63]),
	all_different([X71,X72,X73,X81,X82,X83,X91,X92,X93]),

	all_different([X14,X15,X16,X24,X25,X26,X34,X35,X36]),
	all_different([X44,X45,X46,X54,X55,X56,X64,X65,X66]),
	all_different([X74,X75,X76,X84,X85,X86,X94,X95,X96]),

	all_different([X17,X18,X19,X27,X28,X29,X37,X38,X39]),
	all_different([X47,X48,X49,X57,X58,X59,X67,X68,X69]),
	all_different([X77,X78,X79,X87,X88,X89,X97,X98,X99]),

		
	labeling([ffc],AllVars).


flatten([],[]).
flatten([H|T],Vars) :-
	flatten(T,TVars),
	append(H,TVars,Vars).

	
/* Transpose a list of lists. */
/* This is modfied from code by Naoyuki Tamura (tamura@kobe-u.ac.jp) */
/* Used without permisson. */

transpose([Word], Cs) :- !,
/*	reverse(Word, R), */
	R = Word,
	list2columns(R, Cs).
transpose([Word|Words], Cs) :- !,
	transpose(Words, Cs0),
/*	reverse(Word, R), */
	R=Word,
	put_columns(R, Cs0, Cs).
	
list2columns([], []).
list2columns([X|Xs], [[X]|Zs]) :- list2columns(Xs, Zs).

put_columns([], Cs, Cs).
put_columns([X|Xs], [C|Cs0], [[X|C]|Cs]) :- put_columns(Xs, Cs0, Cs).



/* Pretty Print L */

pretty_print([]).
pretty_print([H|T]) :-
	write(H),nl,
	pretty_print(T).

