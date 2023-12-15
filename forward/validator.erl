-module(validator).
-export([start/0]).

start() ->
    spawn_link(fun() -> init() end).

init()->
    validator().

validator() ->
    receive
        {validate, Ref, Writes, Client, Handler} ->
            Tag = make_ref(),
            send_write_checks(Writes, Tag, Handler),  %% TODO: COMPLETE
            case check_writes(length(Writes), Tag) of  %% TODO: COMPLETE
                ok ->
                    update(Writes, Handler),  %% TODO: COMPLETE
                    Client ! {Ref, ok};
                abort ->
                    Client ! {Ref, abort} %% TODO: ADD SOME CODE
            end,
            validator();
        stop ->
            ok;
        _Old ->
            validator()
    end.
    
update(Writes, Handler) ->
    lists:foreach(fun({_, Entry, Value}) -> 
                  Entry ! {write, Value, Handler} %% TODO: ADD SOME CODE
                  end, 
                  Writes).

send_write_checks(Writes, Tag, Handler) ->
    Self = self(),
    lists:foreach(fun({_, Entry, _}) -> 
                  Entry ! {check, Tag, Self, Handler}
                  end, 
                  Writes).

check_writes(0, _) ->
    ok;
check_writes(N, Tag) ->
    receive
        {Tag, ok} ->
            check_writes(N-1, Tag);
        {Tag, abort} ->
            abort
    end.
