import numpy as np
import pandas as pd

def make_json_safe(obj):

    if isinstance(obj, dict):
        return {str(k): make_json_safe(v) for k, v in obj.items()}

    elif isinstance(obj, list):
        return [make_json_safe(i) for i in obj]

    elif isinstance(obj, tuple):
        return [make_json_safe(i) for i in obj]

    elif isinstance(obj, set):
        return [make_json_safe(i) for i in obj]

    elif isinstance(obj, np.ndarray):
        return make_json_safe(obj.tolist())

    elif isinstance(obj, pd.Series):
        return make_json_safe(obj.to_dict())

    elif isinstance(obj, pd.DataFrame):
        return make_json_safe(obj.to_dict(orient="records"))

    elif isinstance(obj, np.integer):
        return int(obj)

    elif isinstance(obj, np.floating):
        return float(obj)

    elif isinstance(obj, np.bool_):
        return bool(obj)

    return obj