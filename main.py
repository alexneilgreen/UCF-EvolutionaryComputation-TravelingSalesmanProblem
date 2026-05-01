"""This file contains the genetic algorithms, distance calculations, and data loading functions"""
# References
#? https://deap.readthedocs.io/en/master/api/tools.html
#? https://deap.readthedocs.io/en/master/api/tools.html#deap.tools.cxOrdered
#? Inversion Mutation - Textbook Pages 69-70

# Standard libraries or third-party packages
import argparse
import csv
import math
import os
import random
import sys
import numpy as np
from deap import base, creator, tools

# Local Imports
import src.utility as utility

# Debug Var
DEBUG = False

# Random seed generation
SEED = 42

# Global GA Values
POP = 300   # Population Size
GEN = 1000  # Number of generations
CXR = 0.85  # Crossover rate
MUT = 0.2   # Mutation rate
TRN = 3     # Tournament size

# DEAP Setup
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

# Load Data
def load_data(filepath):
    cities = []
    coords = []

    with open(filepath, "r") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            lat = float(parts[-2])
            lon = float(parts[-1])
            city = " ".join(parts[:-2]).replace("_", " ")
            cities.append(city)
            coords.append([lat, lon])

    return cities, np.array(coords, dtype=np.float64)

# Haversine Distance Calculator
def hav_dist(lat1, lon1, lat2, lon2):
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1

    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2

    dist = 2 * 3958.8 * math.asin(math.sqrt(a)) # 3958.8 is the earth's radius in miles

    return dist

# Distance Matrix Generator
def distance_matrix(coords):
    n = len (coords)
    matrix = np.zeros((n, n), dtype=np.float64)

    for i in range (n):
        for j in range (i+1, n):
            dist = hav_dist(coords[i, 0], coords[i, 1], coords[j, 0], coords[j, 1])
            matrix[i, j] = dist
            matrix[j, i] = dist

    return matrix

# Inversion Mutation
def inversion_mutation(individual, indpb):
    if random.random() < indpb:
        size = len(individual)
        a, b = sorted(random.sample(range(size), 2))    # Randomly pick two distinct positions
        individual[a:b] = individual[a:b][::-1]         # Reverse the order within those positions
    return (individual,)

# Genetic Algorithm
def run(distance, n_cities):
    # Set Random Seed
    random.seed(SEED)
    np.random.seed(SEED)

    # Fitness Function
    def evaluate(individual):
        total = 0.0

        for i in range (n_cities):
            total += distance[individual[i], individual[(i+1) % n_cities]]

        return (total,)

    # Setup DEAP Toolbox
    toolbox = base.Toolbox()
    toolbox.register("indices", random.sample, range(n_cities), n_cities)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
    toolbox.register("population", tools.initRepeat,  list, toolbox.individual)
    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxOrdered)
    toolbox.register("mutate", inversion_mutation, indpb=0.825)  
    toolbox.register("select", tools.selTournament, tournsize=TRN)

    best_route = tools.HallOfFame(1)    # Keep the single best individual route
    pop = toolbox.population(n=POP)     # Initial Population

    # Evaluate Initial Population Fitness
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    best_route.update(pop)

    # Saved for Plotting
    best_per_gen = []

    # Evolution loop
    for gen in range (1, (GEN+1)):
        # Selection
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        # Crossover
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXR:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        # Mutation
        for mutant in offspring:
            if random.random() < MUT:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluation
        invalid = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = list(map(toolbox.evaluate, invalid))
        for ind, fit in zip(invalid, fitnesses):
            ind.fitness.values = fit

        # Keep Best Route
        offspring[0] = toolbox.clone(best_route[0])
        pop[:] = offspring
        best_route.update(pop)

        best_per_gen.append(best_route[0].fitness.values[0])

    best_tour = list(best_route[0])
    best_distance = best_route[0].fitness.values[0]
    return best_tour, best_distance, best_per_gen

def main():

    if not os.path.isfile("src/tsp.dat"):
        utility.log("src/tsp.dat was not found")
        return
    
    # Load Data
    cities, coords = load_data("src/tsp.dat")
    n_cities = len(cities)

    # Test load_data
    if (DEBUG == True):
        print("\n----- Number of Cities -----")
        print(n_cities)

        print("\n----- City Names -----")
        print(cities)

        print("\n----- Coordinates -----")
        print(coords)

    # Build Distance Matrix
    distances = distance_matrix(coords)

    best_tour, best_distance, best_per_gen = run(distances, n_cities)

    # Log Results
    utility.log(f"\n\tBest Tour:")
    for order, idx in enumerate(best_tour, start=1):
        utility.log(f"\n\t\t  {order:>2}. {cities[idx]}")
    utility.log(f"\n\tBest Distance = {best_distance:,.4f} miles")

    # Ensure results directory exists
    os.makedirs("results", exist_ok=True)

    # Plot Fitness over Generations
    utility.plot_fitness(best_per_gen, output_path="results/fitness_over_generations.png")

    # Plot Best Tour
    utility.plot_tour(best_tour, coords, output_path="results/best_tour.png")
    
    # Save Results to CSV
    utility.save_tour_csv(best_tour, cities, best_distance, output_path="results/best_tour.csv")

    return

if __name__ == "__main__":
    main()