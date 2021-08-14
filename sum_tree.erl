-module(sum_tree).

-include_lib("eunit/include/eunit.hrl").

-type tree() :: {Key::integer(),
		 Children::treelist()}
	      | null.
-type treelist() :: {Hd::tree(),
		     Tl::treelist()}
		  | nil.

-export([sum_tree/1]).

-spec sum_tree(tree()) -> integer().
sum_tree(null) -> 0;
sum_tree({Key, Children}) -> 
    Key + sum_tree_list(Children).

-spec sum_tree_list(treelist()) -> integer().
sum_tree_list(nil) -> 0;
sum_tree_list({Hd, Tl}) -> 
    sum_tree(Hd) + sum_tree_list(Tl).

-ifdef(EUNIT).
sum_tree_test() ->
    Leaf1 = {1, nil},
    Leaf2 = {2, nil},
    Tree = {3, {Leaf1, {Leaf2, nil}}},
    ?assert(sum_tree(Tree) =:= 6).
-endif.
