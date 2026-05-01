"""This file contains the logging and plotting functions"""

# Standard libraries or third-party packages
import os
import csv
import matplotlib
import matplotlib.pyplot as plt

LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
log_file = open(LOG_PATH, "w")

# Logging function
def log(message):
    print(message, end="")
    log_file.write(message)
    log_file.flush()

# Save final results to csv
def save_tour_csv(tour, cities, distance, output_path="results/best_tour.csv"):
    with open(output_path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Order", "City"])
        for order, idx in enumerate(tour, start=1):
            writer.writerow([order, cities[idx]])
        writer.writerow([])
        writer.writerow(["Total Distance (miles)", f"{distance:.4f}"])

# Plot Fitness over Generations
def plot_fitness(best_per_gen, output_path="results/fitness_over_generations.png"):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(best_per_gen, linewidth=2)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Tour Distance (miles)")
    ax.set_title("Best Tour Distance Per Generation")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

# Plot Best Tour Path
def plot_tour(tour, coords, output_path="results/best_tour.png"):
    # Build ordered lat/lon lists
    lons = []
    lats = []
    for i in tour:
        lons.append(coords[i, 1])  # Longitude is the x column
        lats.append(coords[i, 0])  # Latitude is the y column

    # Close loop and append first city to end
    lons.append(coords[tour[0], 1])
    lats.append(coords[tour[0], 0])

    # Plot
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(lons, lats, "-o", markersize=5, linewidth=1, color="blue")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Best TSP Tour")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return