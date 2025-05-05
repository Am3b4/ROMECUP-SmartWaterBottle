from math import radians, sin, cos, atan2, sqrt, degrees
from typing import List, Tuple


EARTH_RADIUS_M = 6_371_000  # Earth radius in meters


def calcolaBoundingBox(
    lat_centro: float,
    lon_centro: float,
    raggio_m: float
) -> Tuple[float, float, float, float]:
    """
    Calcola il bounding box (min_lat, max_lat, min_lon, max_lon) per un cerchio sulla Terra.
    """
    rad_dist = raggio_m / EARTH_RADIUS_M
    lat0 = radians(lat_centro)

    delta_lat = degrees(rad_dist)
    min_lat = lat_centro - delta_lat
    max_lat = lat_centro + delta_lat

    delta_lon = degrees(rad_dist / cos(lat0))
    min_lon = lon_centro - delta_lon
    max_lon = lon_centro + delta_lon

    return min_lat, max_lat, min_lon, max_lon


def calcolaDistanzaHaversine(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calcola la distanza in metri tra due punti geo con formula Haversine.
    """

    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    phi1, lambda1, phi2, lambda2 = map(radians, (lat1, lon1, lat2, lon2))
    dphi = phi2 - phi1
    dlambda = lambda2 - lambda1
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS_M * c


def filtraOrdinaFontanelle(
    candidati: List,
    lat_centro: float,
    lon_centro: float,
    raggio_m: float
) -> List:
    """
    Calcola la distanza esatta per ogni candidato, filtra per raggio, ordina.
    """
    lista: List = []
    for poi in candidati:
        dist = calcolaDistanzaHaversine(lat_centro, lon_centro, poi.latitudine, poi.longitudine)
        if dist <= raggio_m:
            lista.append({
                "id": poi.id,
                "indirizzo": poi.indirizzo,
                "latitudine": poi.latitudine,
                "longitudine": poi.longitudine,
                "tipo": poi.tipo,
                'distanza_m': dist,
                }
            )
    lista.sort(key=lambda x: x['distanza_m'])
    return lista
