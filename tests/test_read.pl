read_file(Filename, Strings) :-
    setup_call_cleanup(
    open(Filename, read, Stream),
    read_stream_string(Stream, Strings),
    close(Stream)
).

read_stream_string(Stream, Strings) :-
    read_line_to_string(Stream, String),
    ( String == end_of_file -> Strings = []
    ;
    read_stream_string(Stream, RStrings),
    Strings = [String|RStrings]
).
