import csv
from collections import defaultdict


def calculate_averages_by_agv(filename):
    agv_data = defaultdict(lambda: {"t1_t4_diff": [], "t2_t3_diff": [], "final_diff": []})

    # Read the CSV file
    with open(filename, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header if there is one

        for row in reader:
            agv_id, t1, t2, t3, t4 = (
                row[0],
                float(row[1]),
                float(row[2]),
                float(row[3]),
                float(row[4]),
            )
            # Compute differences
            t1_t4_diff = t4 - t1
            t2_t3_diff = t3 - t2
            final_diff = (t1_t4_diff - t2_t3_diff) / 2

            # Store in agv-specific data
            agv_data[agv_id]["t1_t4_diff"].append(t1_t4_diff)
            agv_data[agv_id]["t2_t3_diff"].append(t2_t3_diff)
            agv_data[agv_id]["final_diff"].append(final_diff)

    overall_t1_t4_diff = []
    overall_t2_t3_diff = []
    overall_final_diff = []

    # Calculate the averages per AGV
    for agv_id, diffs in agv_data.items():
        avg_t1_t4 = (
            sum(diffs["t1_t4_diff"]) / len(diffs["t1_t4_diff"]) if diffs["t1_t4_diff"] else 0
        )
        avg_t2_t3 = (
            sum(diffs["t2_t3_diff"]) / len(diffs["t2_t3_diff"]) if diffs["t2_t3_diff"] else 0
        )
        avg_final = (
            sum(diffs["final_diff"]) / len(diffs["final_diff"]) if diffs["final_diff"] else 0
        )

        print(f"AGV {agv_id}:")
        print(f"  Average (t4 - t1): {avg_t1_t4}")
        print(f"  Average (t3 - t2): {avg_t2_t3}")
        print(f"  Average ((t4 - t1) - (t3 - t2)) / 2: {avg_final}")

        # Add to overall calculations
        overall_t1_t4_diff.extend(diffs["t1_t4_diff"])
        overall_t2_t3_diff.extend(diffs["t2_t3_diff"])
        overall_final_diff.extend(diffs["final_diff"])

    # Calculate overall averages
    avg_overall_t1_t4 = (
        sum(overall_t1_t4_diff) / len(overall_t1_t4_diff) if overall_t1_t4_diff else 0
    )
    avg_overall_t2_t3 = (
        sum(overall_t2_t3_diff) / len(overall_t2_t3_diff) if overall_t2_t3_diff else 0
    )
    avg_overall_final = (
        sum(overall_final_diff) / len(overall_final_diff) if overall_final_diff else 0
    )

    print("\nOverall:")
    print(f"  Average (t4 - t1): {avg_overall_t1_t4}")
    print(f"  Average (t3 - t2): {avg_overall_t2_t3}")
    print(f"  Average ((t4 - t1) - (t3 - t2)) / 2: {avg_overall_final}")


# Specify the file containing the data
filename = "update_location.csv"

# Calculate the averages
calculate_averages_by_agv(filename)
