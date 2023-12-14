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


def measure():
    subprocess.run(["erl", "-make"], check=False)
    iterations = 5
    num_entries = 5
    rxt = 1
    wxt = range(1, 16)
    duration = 10
    num_clients = 4
    output_dir = "experiments/wxt"
    timeout = duration + 5
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/summary.csv", "w", encoding="utf-8") as summary_file:
        summary_file.write("clients,entries,rxt,wxt,duration,transactions,ok\n")
        for c in wxt:
            for it in range(iterations):
                print(
                    f"Interation {it}: {num_clients} clients, {num_entries} entries, {rxt} rxt, {c} wxt, {duration} duration"
                )
                filename = f"{num_clients}clients_{num_entries}entries_{rxt}rxt_{c}wxt_{duration}duration.{it}.out"
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
                                f"opty:start({num_clients},{num_entries},{rxt},{c},{duration})",
                            ],
                            check=False,
                            timeout=timeout,
                            stdout=outfile,
                        )
                    except subprocess.TimeoutExpired:
                        outfile.seek(0)
                        (trs, oks) = parse(outfile.read())
                        for tr, ok in zip(trs, oks):
                            summary_file.write(
                                f"{num_clients},{num_entries},{rxt},{c},{duration},{tr},{ok}\n"
                            )
                    summary_file.flush()


def measure_exp6():
    subprocess.run(["erl", "-make"], check=False)
    iterations = 5
    num_entries = 10
    rxt = 1
    wxt = 1
    duration = 10
    num_clients = 4
    subset_size = range(1, num_entries + 1)
    output_dir = "experiments/subset"
    timeout = duration + 5
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/summary.csv", "w", encoding="utf-8") as summary_file:
        summary_file.write(
            "clients,entries,rxt,wxt,duration,subset_size,transactions,ok\n"
        )
        for c in subset_size:
            for it in range(iterations):
                print(
                    f"Iteration {it}: {num_clients} clients, {num_entries} entries, {rxt} rxt, {wxt} wxt, {duration} duration, {c} subset_size"
                )
                filename = f"{num_clients}clients_{num_entries}entries_{rxt}rxt_{c}wxt_{duration}duration_{c}subset_size.{it}.out"
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
                                f"opty:start({num_clients},{num_entries},{rxt},{wxt},{duration},{c})",
                            ],
                            check=False,
                            timeout=timeout,
                            stdout=outfile,
                        )
                    except subprocess.TimeoutExpired:
                        outfile.seek(0)
                        (trs, oks) = parse(outfile.read())
                        for tr, ok in zip(trs, oks):
                            summary_file.write(
                                f"{num_clients},{num_entries},{rxt},{wxt},{duration},{c},{tr},{ok}\n"
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
    #measure_exp6()
    filepath = "experiments/subset/summary.csv"
    print_avg(filepath, ["subset_size"])


if __name__ == "__main__":
    main()
