import subprocess
import os


def measure_clients():
    subprocess.run(["erl", "-make"], check=False)
    iterations = 5
    num_entries = 5
    rxt = 1
    wxt = 1
    duration = 10
    num_clients = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]  # add values
    output_dir = "experiments/clients"
    os.makedirs(output_dir, exist_ok=True)
    # with open(f"{output_dir}/summary.csv", "w", encoding="utf-8") as summary_file:
    #     summary_file.write("Clients,Entries,RxT,WxT,Duration\n")
    for c in num_clients:
        for it in range(iterations):
            envs = os.environ.copy()
            envs["CLIENT"] = str(c)
            envs["ENTRIES"] = str(num_entries)
            envs["RXT"] = str(rxt)
            envs["WXT"] = str(wxt)
            envs["DURATION"] = str(duration)
            print(
                f"Interation {it}: {c} clients {num_entries} entries {rxt} rxt {wxt} wxt {duration} duration {it}"
            )
            filename = f"{c}clients_{num_entries}entries_{rxt}rxt_{wxt}wxt_{duration}duration.{it}.out"
            with open(f"{output_dir}/{filename}", "w", encoding="utf-8") as outfile:
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
                        timeout=12,
                        stdout=outfile,
                    )
                except subprocess.TimeoutExpired:
                    pass
            # time.sleep(2)
            # time_ms = ''.join(c for c in time_data if c.isdigit())
            # round_data = subprocess.run(
            #     ["grep", "LAST ROUND", f"{output_dir}/{filename}"],
            #     stdout=subprocess.PIPE,
            # ).stdout.decode("utf-8")

            # summary_file.write(
            #     f"{c},{num_entries},{rxt},{wxt},{duration}\n"
            # )  # change


def get_avgs(filename, sep, group_by_col):
    # df = pd.read_csv(filename, sep=sep)
    # df.groupby([""])
    return

def main():
    measure_clients()

if __name__ == "__main__":
    main()
