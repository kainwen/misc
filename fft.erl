-module(fft).

-include_lib("eunit/include/eunit.hrl").

-export([j/2]).

j(1, N) -> N;
j(K, N) when K > 1 ->
    H = trunc(math:pow(2, K-1)),
    case N < H of
	true ->
	    2 * j(K-1, N);
	false ->
	    2 * j(K-1, N - H) + 1
    end.

fft_test() ->
    %% k = 3, 8点fft
    ?assert([j(3, N) || N <- lists:seq(0, 7)] =:=
		[0,4,2,6,1,5,3,7]),
    %% k = 2, 4点fft
    ?assert([j(2, N) || N <- lists:seq(0, 3)] =:=
		[0,2,1,3]),
    ok.
