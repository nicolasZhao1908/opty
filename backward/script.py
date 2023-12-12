import subprocess
import os
import re
import pandas as pd


def parse(text):
    # Define regular expressions to extract total transactions and percentages
    total_transactions_pattern = re.compile(r"Transactions TOTAL:(\d+)")
    percentage_pattern = re.compile(r"-> (\d+\.\d+) %")

    # Find all matches in the log messages
    total_transactions_matches = total_transactions_pattern.findall(text)
    percentage_matches = percentage_pattern.findall(text)
    return (total_transactions_matches, percentage_matches)


def measure_clients():
    subprocess.run(["erl", "-make"], check=False)
    iterations = 5
    num_entries = 5
    rxt = 1
    wxt = 1
    duration = 10
    num_clients = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]  # add values
    output_dir = "experiments/clients"
    timeout = duration + 5
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/summary.csv", "w", encoding="utf-8") as summary_file:
        summary_file.write("clients,entries,rxt,wxt,duration,transactions,ok\n")
        for c in num_clients:
            for it in range(iterations):
                envs = os.environ.copy()
                envs["CLIENT"] = str(c)
                envs["ENTRIES"] = str(num_entries)
                envs["RXT"] = str(rxt)
                envs["WXT"] = str(wxt)
                envs["DURATION"] = str(duration)
                print(
                    f"Interation {it}: {c} clients, {num_entries} entries, {rxt} rxt, {wxt} wxt, {duration} duration"
                )
                filename = f"{c}clients_{num_entries}entries_{rxt}rxt_{wxt}wxt_{duration}duration.{it}.out"
                with open(
                    f"{output_dir}/{filename}", "a+", encoding="utf-8"
                ) as outfile:
                    try:
                        subprocess.run(
                            [
                                "erl",
                                "-noshell",
                                "-pa",
                                "ebin",
                                "-eval",
                                f"opty:start({c},{num_entries},{rxt},{wxt},{duration})",
                            ],
                            check=False,
                            env=envs,
                            timeout=timeout,
                            stdout=outfile,
                        )
                    except subprocess.TimeoutExpired:
                        outfile.seek(0)
                        (trs, oks) = parse(outfile.read())
                        for tr, ok in zip(trs, oks):
                            summary_file.write(
                                f"{c},{num_entries},{rxt},{wxt},{duration},{tr},{ok}\n"
                            )
                    summary_file.flush()


def print_avg(filepath, columns):
    df = pd.read_csv(filepath, sep=",")
    transactions = df.groupby(columns)[["transactions"]].mean()
    trs_res = list(transactions.itertuples(index=True, name=None))
    oks = df.groupby(columns)[["ok"]].mean()
    oks_res = list(oks.itertuples(index=True, name=None))
    print("##### TRANSACTIONS #####")
    for tr in trs_res:
        print(f"({tr[0]}, {tr[1]})")
    print()
    print("##### Ok (%) #####")
    for ok in oks_res:
        print(f"({ok[0]}, {ok[1]})")


def main():
    # measure_clients()
    experiment = "clients"
    filepath = f"experiments/{experiment}/summary.csv"
    print_avg(filepath, [experiment])


if __name__ == "__main__":
    main()
