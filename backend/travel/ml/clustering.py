from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np

class PlaceClusterer:
    def __init__(self, places):
        self.places = list(places)
        self.scaler = StandardScaler()
    
    def cluster_places(self, n_clusters=4):
        n_clusters = min(n_clusters, len(self.places) // 2)
        if n_clusters < 2:
            return {'Все места': [p.id for p in self.places]}
        
        features = []
        for p in self.places:
            price = float(p.price_tenge or 0) / 1000
            rating = float(p.rating or 4.0)
            duration = float(p.duration_hours or 2.0)
            is_indoor = 1.0 if p.is_indoor else 0.0
            
            features.append([rating, price, duration, is_indoor])
        
        X = self.scaler.fit_transform(features)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        
        clusters = {}
        cluster_names = ['Бюджетные', 'Премиум', 'Популярные', 'Активные']
        
        for i in range(n_clusters):
            cluster_places = [self.places[j] for j in range(len(self.places)) if labels[j] == i]
            if cluster_places:
                name = self._get_cluster_name(cluster_places, cluster_names[i])
                clusters[name] = [p.id for p in cluster_places]
        
        return clusters
    
    def _get_cluster_name(self, places, default_name):
        avg_price = sum(p.price_tenge or 0 for p in places) / len(places)
        avg_rating = sum(p.rating or 0 for p in places) / len(places)
        
        if avg_price < 2000:
            return '💰 Бюджетные'
        elif avg_price > 10000:
            return '💎 Премиум'
        elif avg_rating > 4.5:
            return '⭐ Популярные'
        else:
            return default_name