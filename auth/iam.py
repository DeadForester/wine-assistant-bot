try:
    from util.iam_auth import get_iam as _get_iam
except ImportError:
    _get_iam = None

def get_iam(service_account_id: str, key_id: str, private_key: str):
    if _get_iam is None:
        raise RuntimeError("IAM auth module not available")
    return _get_iam(service_account_id, key_id, private_key)