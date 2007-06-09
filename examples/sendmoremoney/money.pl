
% SEND + MORE = MONEY
% Adapted from: http://en.wikipedia.org/wiki/Constraint_programming

:- use_module(library('bounds')).

sendmore(Digits) :-
   Digits = [S,E,N,D,M,O,R,Y],     % Create variables
   Digits in 0..9,               % Associate domains to variables
   S #\= 0,                        % Constraint: S must be different from 0
   M #\= 0,
   all_different(Digits),           % all the elements must take different values
                1000*S + 100*E + 10*N + D     % Other constraints
              + 1000*M + 100*O + 10*R + E
   #= 10000*M + 1000*O + 100*N + 10*E + Y,
   label(Digits).               % Start the search

