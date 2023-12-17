-module(validator).
-export([start/0]).

start() ->
    spawn_link(fun() -> init() end).

init() ->
    validator().

validator() ->
    receive
        {validate, Ref, Reads, Writes, Client, Handler} ->
            Tag = make_ref(),
            send_write_checks(Writes, Tag, Handler),
            case check_writes(length(Writes), Tag) of
                ok ->
                    update(Writes),
                    clean_active_transactions(Reads, Handler),
                    Client ! {Ref, ok};
                abort ->
                    clean_active_transactions(Reads, Handler),
                    Client ! {Ref, abort}
            end,
            validator();
        stop ->
            ok;
        _Old ->
            validator()
    end.

clean_active_transactions(Reads, Handler) ->
    lists:foreach(
        fun(Entry) ->
            Entry ! {clean, Handler}
        end,
        Reads
    ).

update(Writes) ->
    lists:foreach(
        fun({_, Entry, Value}) ->
            Entry ! {write, Value}
        end,
        Writes
    ).

send_write_checks(Writes, Tag, Handler) ->
    Self = self(),
    lists:foreach(
        fun({_, Entry, _}) ->
            Entry ! {check, Tag, Self, Handler}
        end,
        Writes
    ).

check_writes(0, _) ->
    ok;
check_writes(N, Tag) ->
    receive
        {Tag, ok} ->
            check_writes(N - 1, Tag);
        {Tag, abort} ->
            abort
    end.
