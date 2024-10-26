
% Towers of Hanoi
% Based on: http://en.wikipedia.org/wiki/Prolog

hanoi(N) :-
    move(N, left, right, center).

move(0, _, _, _) :-
    !.
move(N, A, B, C) :-
  M is N-1,
  move(M, A, C, B),
  notify([A,B]),
  move(M, C, B, A).
  