-module(handler).
-export([start/3]).

start(Client, Validator, Store) ->
    spawn_link(fun() -> init(Client, Validator, Store) end).

init(Client, Validator, Store) ->
    handler(Client, Validator, Store, []).

handler(Client, Validator, Store, Writes) ->         
    receive
        {read, Ref, N} ->
            case lists:keyfind(N, 1, Writes) of  %% TODO: COMPLETE
                {N, _, Value} ->
                    Client ! {value, Ref, Value}, %% TODO: ADD SOME CODE
                    handler(Client, Validator, Store, Writes);
                false ->
                    Entry = store:lookup(N, Store), %% TODO: ADD SOME CODE     
                    Entry ! {read, Ref, self()}, %% TODO: ADD SOME CODE  
                    handler(Client, Validator, Store, Writes)
            end;
        {write, N, Value} ->
            Entry = store:lookup(N, Store), %% TODO: ADD SOME CODE HERE AND COMPLETE NEXT LINE    
            Added = lists:keystore(N, 1, Writes, {N, Entry, Value}),     
            handler(Client, Validator, Store, Added);
        {commit, Ref} ->
            Validator ! {validate, Ref, Writes, Client, self()}; %% TODO: ADD SOME CODE
        {Ref, Value} ->
            Client ! {value, Ref, Value}, %% TODO: ADD SOME CODE HERE AND COMPLETE NEXT LINE
            handler(Client, Validator, Store, Writes);
        abort ->
            ok
    end.
