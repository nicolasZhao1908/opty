- Each entry keeps references (timestamp)
    - Timestamp from read == Timestamp from read: valid
    - Timestamp from read != Timestamp from read: someone has changed the entry
      since i last read. NOT VALID.
- Number of clients, operations and size of store impacts the number of
  conflicts
 
paxy:start(
    number_clients,
    number_entries,
    read_per_transaction,
    write_per_transaction,
    duration of experiment,
    subset of stores for each client
)
