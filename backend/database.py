# ============================================================
# database.py  –  DISABLED (No Database Persistence Allowed)
# ============================================================
#
# As per project requirements:
# "Do not use MySQL. Do not use any permanent database.
#  Use temporary files only for processing."
#

def init_db():
    print("[DB] Permanent database persistence is disabled per design specification.")

def save_detection(*args, **kwargs):
    return None

def fetch_all_detections(limit=50):
    return []

def clear_all_detections():
    pass
