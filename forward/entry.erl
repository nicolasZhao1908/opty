-module(entry).
-export([new/1]).

new(Value) ->
    spawn_link(fun() -> init(Value) end).

init(Value) ->
    entry(Value, []).

entry(Value, ActiveReads) ->
    receive
        {read, Ref, Handler} ->
            case lists:member(Handler, ActiveReads) of
                true ->
                    entry(Value, ActiveReads);
                false ->
                    entry(Value, [Handler | ActiveReads])
            end,
            Handler ! {Ref, self(), Value};
        {write, New} ->
            entry(New, ActiveReads);
        {clean, Handler} ->
            entry(Value, lists:delete(Handler, ActiveReads));
        {check, Ref, Validator, Handler} ->
            sendFeedback(Ref, Validator, ActiveReads, Handler),
            entry(Value, ActiveReads);
        stop ->
            ok
    end.

sendFeedback(Ref, Validator, [Handler], Handler) ->
    Validator ! {Ref, ok};
sendFeedback(Ref, Validator, [], _) ->
    Validator ! {Ref, ok};
sendFeedback(Ref, Validator, _, _) ->
    Validator ! {Ref, abort}.
