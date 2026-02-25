"""
ELIXIR TECHNOLOGY
Veri Filtreleri
"""

import numpy as np


FILTERS = {
    'Filtre Yok': {
        'id': 'none',
        'description': 'Ham veri, filtre uygulanmaz',
        'colors': []
    },
    'Muslum Erbay': {
        'id': 'muslum_erbay',
        'description': 'En dusuk ve en yuksek degerleri vurgular',
        'colors': [('#0000FF', 'Min'), ('#FF0000', 'Max')]
    },
    'Termal': {
        'id': 'thermal',
        'description': 'Sicaklik haritasi (mavi-kirmizi)',
        'colors': [('#0000CC', 'Soguk'), ('#00CCFF', 'Serin'), ('#FFFF00', 'Ilik'), ('#FF6600', 'Sicak'), ('#FF0000', 'Cok Sicak')]
    },
    'Toprak Katmani': {
        'id': 'soil_layer',
        'description': 'Toprak tabakalarini ayirt eder',
        'colors': [('#3B2507', 'Derin'), ('#8B5A2B', 'Orta'), ('#D2B48C', 'Yuzey')]
    },
    'Metal Dedektoru': {
        'id': 'metal_detect',
        'description': 'Metal anomalileri vurgular',
        'colors': [('#1A1A1A', 'Yok'), ('#FFD700', 'Zayif'), ('#FF4500', 'Guclu')]
    },
    'Su Tabakasi': {
        'id': 'water_layer',
        'description': 'Yeraltı su tablasini gosterir',
        'colors': [('#2F1B0E', 'Kuru'), ('#1E90FF', 'Nemli'), ('#0000CD', 'Su')]
    },
    'Gradyan': {
        'id': 'gradient',
        'description': 'Deger degisim oranini gosterir',
        'colors': [('#000000', 'Dusuk'), ('#00FF00', 'Orta'), ('#FFFFFF', 'Yuksek')]
    },
    'Kontrast': {
        'id': 'contrast',
        'description': 'Yuksek kontrastli goruntuleme',
        'colors': [('#000000', 'Min'), ('#FFFFFF', 'Max')]
    },
    'Anomali': {
        'id': 'anomaly',
        'description': 'Ortalamadan sapmalari vurgular',
        'colors': [('#333333', 'Normal'), ('#FF00FF', 'Anomali')]
    },
    'Derinlik': {
        'id': 'depth_map',
        'description': 'Derinlik tahmini renklendirme',
        'colors': [('#E8D4B8', 'Yakin'), ('#8B4513', 'Orta'), ('#1A0A00', 'Derin')]
    },
}


def apply_filter(data_matrix, filter_name, rows, cols):
    if data_matrix is None or len(data_matrix) == 0:
        return data_matrix

    matrix = np.array(data_matrix, dtype=float)

    if filter_name == 'Filtre Yok' or filter_name not in FILTERS:
        return matrix

    filter_id = FILTERS[filter_name]['id']

    if filter_id == 'muslum_erbay':
        return _filter_muslum_erbay(matrix)
    elif filter_id == 'thermal':
        return _filter_thermal(matrix)
    elif filter_id == 'soil_layer':
        return _filter_soil_layer(matrix)
    elif filter_id == 'metal_detect':
        return _filter_metal_detect(matrix)
    elif filter_id == 'water_layer':
        return _filter_water_layer(matrix)
    elif filter_id == 'gradient':
        return _filter_gradient(matrix)
    elif filter_id == 'contrast':
        return _filter_contrast(matrix)
    elif filter_id == 'anomaly':
        return _filter_anomaly(matrix)
    elif filter_id == 'depth_map':
        return _filter_depth_map(matrix)

    return matrix


def _filter_muslum_erbay(matrix):
    result = np.zeros_like(matrix)
    if np.max(matrix) == np.min(matrix):
        return result

    min_val = np.min(matrix[matrix > 0]) if np.any(matrix > 0) else 0
    max_val = np.max(matrix)
    threshold_low = min_val + (max_val - min_val) * 0.15
    threshold_high = max_val - (max_val - min_val) * 0.15

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix[i][j]
            if val <= threshold_low and val > 0:
                result[i][j] = 10
            elif val >= threshold_high:
                result[i][j] = 245
            else:
                result[i][j] = 80

    return result


def _filter_thermal(matrix):
    if np.max(matrix) > np.min(matrix):
        normalized = (matrix - np.min(matrix)) / (np.max(matrix) - np.min(matrix))
    else:
        normalized = np.zeros_like(matrix)
    return (normalized * 255).astype(np.uint8)


def _filter_soil_layer(matrix):
    if np.max(matrix) > np.min(matrix):
        normalized = (matrix - np.min(matrix)) / (np.max(matrix) - np.min(matrix))
    else:
        normalized = np.zeros_like(matrix)
    result = np.zeros_like(matrix)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            v = normalized[i][j]
            if v < 0.33:
                result[i][j] = v * 3 * 85
            elif v < 0.66:
                result[i][j] = 85 + (v - 0.33) * 3 * 85
            else:
                result[i][j] = 170 + (v - 0.66) * 3 * 85
    return result


def _filter_metal_detect(matrix):
    if np.max(matrix) == np.min(matrix):
        return np.zeros_like(matrix)
    mean = np.mean(matrix[matrix > 0]) if np.any(matrix > 0) else 0
    std = np.std(matrix[matrix > 0]) if np.any(matrix > 0) else 1
    result = np.zeros_like(matrix)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            deviation = abs(matrix[i][j] - mean) / max(std, 1)
            if deviation > 2:
                result[i][j] = 255
            elif deviation > 1:
                result[i][j] = 180
            else:
                result[i][j] = 30
    return result


def _filter_water_layer(matrix):
    if np.max(matrix) > np.min(matrix):
        normalized = (matrix - np.min(matrix)) / (np.max(matrix) - np.min(matrix))
    else:
        normalized = np.zeros_like(matrix)
    return (normalized * 255).astype(np.uint8)


def _filter_gradient(matrix):
    result = np.zeros_like(matrix)
    rows, cols = matrix.shape
    for i in range(rows):
        for j in range(cols):
            gradients = []
            if j < cols - 1:
                gradients.append(abs(matrix[i][j] - matrix[i][j + 1]))
            if i < rows - 1:
                gradients.append(abs(matrix[i][j] - matrix[i + 1][j]))
            if j > 0:
                gradients.append(abs(matrix[i][j] - matrix[i][j - 1]))
            if i > 0:
                gradients.append(abs(matrix[i][j] - matrix[i - 1][j]))
            result[i][j] = max(gradients) if gradients else 0

    if np.max(result) > 0:
        result = result / np.max(result) * 255

    return result


def _filter_contrast(matrix):
    if np.max(matrix) > np.min(matrix):
        normalized = (matrix - np.min(matrix)) / (np.max(matrix) - np.min(matrix))
    else:
        normalized = np.zeros_like(matrix)
    contrasted = np.clip((normalized - 0.5) * 3 + 0.5, 0, 1)
    return (contrasted * 255).astype(np.uint8)


def _filter_anomaly(matrix):
    if np.max(matrix) == np.min(matrix):
        return np.zeros_like(matrix)
    mean = np.mean(matrix[matrix > 0]) if np.any(matrix > 0) else 0
    std = np.std(matrix[matrix > 0]) if np.any(matrix > 0) else 1
    result = np.zeros_like(matrix)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            deviation = abs(matrix[i][j] - mean) / max(std, 1)
            result[i][j] = min(255, deviation * 100)
    return result


def _filter_depth_map(matrix):
    if np.max(matrix) > np.min(matrix):
        normalized = 1.0 - (matrix - np.min(matrix)) / (np.max(matrix) - np.min(matrix))
    else:
        normalized = np.zeros_like(matrix)
    return (normalized * 255).astype(np.uint8)


def get_filter_color_for_value(filter_name, value, normalized=True):
    filter_id = FILTERS.get(filter_name, {}).get('id', 'none')

    if not normalized:
        value = value / 255.0

    if filter_id == 'muslum_erbay':
        if value < 0.15:
            return (0, 0, 255)
        elif value > 0.85:
            return (255, 0, 0)
        else:
            return (60, 60, 60)
    elif filter_id == 'thermal':
        if value < 0.2:
            return (0, 0, 200)
        elif value < 0.4:
            return (0, 200, 255)
        elif value < 0.6:
            return (255, 255, 0)
        elif value < 0.8:
            return (255, 100, 0)
        else:
            return (255, 0, 0)
    elif filter_id == 'soil_layer':
        if value < 0.33:
            return (59, 37, 7)
        elif value < 0.66:
            return (139, 90, 43)
        else:
            return (210, 180, 140)
    elif filter_id == 'metal_detect':
        if value < 0.3:
            return (26, 26, 26)
        elif value < 0.7:
            return (255, 215, 0)
        else:
            return (255, 69, 0)
    elif filter_id == 'water_layer':
        if value < 0.33:
            return (47, 27, 14)
        elif value < 0.66:
            return (30, 144, 255)
        else:
            return (0, 0, 205)
    elif filter_id == 'gradient':
        g = int(value * 255)
        return (0, g, 0)
    elif filter_id == 'contrast':
        v = int(value * 255)
        return (v, v, v)
    elif filter_id == 'anomaly':
        if value < 0.3:
            return (50, 50, 50)
        else:
            m = int(value * 255)
            return (m, 0, m)
    elif filter_id == 'depth_map':
        if value < 0.33:
            return (232, 212, 184)
        elif value < 0.66:
            return (139, 69, 19)
        else:
            return (26, 10, 0)

    if value < 0.25:
        t = value / 0.25
        return (0, int(80 * t), int(180 * (1 - t) + 50))
    elif value < 0.5:
        t = (value - 0.25) / 0.25
        return (0, int(80 + 175 * t), int(50 * (1 - t)))
    elif value < 0.75:
        t = (value - 0.5) / 0.25
        return (int(255 * t), int(215 - 50 * t), 0)
    else:
        t = (value - 0.75) / 0.25
        return (255, int(165 * (1 - t)), 0)
