import numpy as np
import random
import math

def geodesic(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371  
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


class GeneticTSP:

    
    def __init__(
        self,
        places: list = None,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        elite_size: int = 5
    ):
        self.places = places or []
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.num_places = len(self.places)
        
        if self.num_places > 0:
            self.distance_matrix = self._calculate_distance_matrix()
        else:
            self.distance_matrix = np.array([])
    
    def _place_to_dict(self, place):
        return {
            'id': place.id,
            'name': place.name,
            'description': place.description,
            'latitude': float(place.latitude),
            'longitude': float(place.longitude),
            'rating': float(place.rating or 0),
            'price_level': place.price_level,
            'price_tenge': place.price_tenge,
            'duration_hours': float(place.duration_hours or 2),
            'is_indoor': place.is_indoor,
            'category': place.category.name if place.category else None,
            'destination': place.destination.name if place.destination else None
        }
    
    def _calculate_distance_matrix(self) -> np.ndarray:
        n = self.num_places
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                coord1 = (self.places[i].latitude, self.places[i].longitude)
                coord2 = (self.places[j].latitude, self.places[j].longitude)
                dist = geodesic(coord1, coord2)
                matrix[i][j] = dist
                matrix[j][i] = dist
                
        return matrix
    
    def _calculate_route_distance(self, route: list) -> float:
        if not route:
            return 0
        distance = 0
        for i in range(len(route) - 1):
            distance += self.distance_matrix[route[i]][route[i + 1]]
        distance += self.distance_matrix[route[-1]][route[0]]
        return distance
    
    def _create_individual(self) -> list:
        route = list(range(self.num_places))
        random.shuffle(route)
        return route
    
    def _create_population(self) -> list:
        return [self._create_individual() for _ in range(self.population_size)]
    
    def _fitness(self, route: list) -> float:
        return 1 / (self._calculate_route_distance(route) + 1)
    
    def _select_parent(self, population: list, fitnesses: list) -> list:
        total_fitness = sum(fitnesses)
        pick = random.uniform(0, total_fitness)
        current = 0
        
        for i, fitness in enumerate(fitnesses):
            current += fitness
            if current >= pick:
                return population[i]
        
        return population[-1]
    
    def _crossover(self, parent1: list, parent2: list) -> list:
        size = len(parent1)
        child = [-1] * size
        
        start = random.randint(0, size - 2)
        end = random.randint(start + 1, size - 1)
        
        child[start:end] = parent1[start:end]
        child_set = set(child) - {-1}
        
        p2_index = 0
        for i in range(size):
            if child[i] == -1:
                while p2_index < size and parent2[p2_index] in child_set:
                    p2_index += 1
                if p2_index < size:
                    child[i] = parent2[p2_index]
                    child_set.add(parent2[p2_index])
                    p2_index += 1
        
        missing = set(range(size)) - set(child)
        if missing:
            for i in range(size):
                if child[i] == -1:
                    child[i] = missing.pop()
                    
        return child
    
    def _mutate(self, route: list) -> list:
        if random.random() < self.mutation_rate:
            i = random.randint(0, len(route) - 1)
            j = random.randint(0, len(route) - 1)
            route[i], route[j] = route[j], route[i]
        return route
    
    def _get_best_route(self, population: list) -> tuple:
        best_route = min(population, key=self._calculate_route_distance)
        best_distance = self._calculate_route_distance(best_route)
        return best_route, best_distance
    
    def optimize(self) -> dict:
        random.seed(42)      
        np.random.seed(42)   
        original_route = list(range(self.num_places))
        original_distance = self._calculate_route_distance(original_route)
        
        population = self._create_population()
        history = []
        
        for _ in range(self.generations):
            fitnesses = [self._fitness(route) for route in population]
            best_route, best_distance = self._get_best_route(population)
            history.append(best_distance)
            
            new_population = []
            
            sorted_population = sorted(
                population, 
                key=lambda x: self._calculate_route_distance(x)
            )
            new_population.extend(sorted_population[:self.elite_size])
            
            while len(new_population) < self.population_size:
                parent1 = self._select_parent(population, fitnesses)
                parent2 = self._select_parent(population, fitnesses)
                child = self._crossover(parent1, parent2)
                child = self._mutate(child)
                new_population.append(child)
            
            population = new_population
        
        optimized_route, optimized_distance = self._get_best_route(population)
        improvement = ((original_distance - optimized_distance) / original_distance) * 100 if original_distance > 0 else 0
        
        original_places = [self._place_to_dict(self.places[i]) for i in original_route]
        optimized_places = [self._place_to_dict(self.places[i]) for i in optimized_route]
        
        return {
            'original_order': original_places,
            'original_distance': round(original_distance, 2),
            'optimized_order': optimized_places,
            'optimized_distance': round(optimized_distance, 2),
            'improvement_percent': round(improvement, 1),
            'history': [round(d, 2) for d in history],
            'time_saved_hours': round((original_distance - optimized_distance) / 30, 1)
        }
    
    def optimize_per_day(self, days_places: list) -> dict:
        results = []
        total_original = 0
        total_optimized = 0
        
        for day_num, day_places in enumerate(days_places, 1):
            if len(day_places) <= 2:
                serialized_places = [self._place_to_dict(p) for p in day_places]
                results.append({
                    'day': day_num,
                    'original_distance': 0,
                    'optimized_distance': 0,
                    'improvement': 0,
                    'optimized_order': serialized_places,
                    'time_saved_hours': 0
                })
                continue
            
            solver = GeneticTSP(
                places=day_places,
                population_size=min(20, len(day_places) * 4),
                generations=min(50, len(day_places) * 10),
                mutation_rate=0.1,
                elite_size=min(2, max(1, len(day_places) // 4))
            )
            
            result = solver.optimize()
            
            results.append({
                'day': day_num,
                'original_distance': result['original_distance'],
                'optimized_distance': result['optimized_distance'],
                'improvement': result['improvement_percent'],
                'optimized_order': result['optimized_order'],
                'time_saved_hours': result['time_saved_hours']
            })
            
            total_original += result['original_distance']
            total_optimized += result['optimized_distance']
        
        total_improvement = ((total_original - total_optimized) / total_original) * 100 if total_original > 0 else 0
        
        return {
            'days': results,
            'total_original_distance': round(total_original, 2),
            'total_optimized_distance': round(total_optimized, 2),
            'total_improvement': round(total_improvement, 1),
            'total_time_saved_hours': round((total_original - total_optimized) / 30, 1)
        }