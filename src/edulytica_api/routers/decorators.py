from functools import wraps
import jwt
from src.edulytica_api.models.auth import Token
from src.edulytica_api.settings import JWT_SECRET_KEY, ALGORITHM


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        payload = jwt.decode(kwargs['dependencies'], JWT_SECRET_KEY, ALGORITHM)
        user_id = payload['sub']
        data = kwargs['session'].query(Token).filter_by(user_id=user_id, access_toke=kwargs['dependencies'],
                                                                    status=True).first()
        if data:
            return func(kwargs['dependencies'], kwargs['session'])
        else:
            return {'msg': "Token blocked"}

    return wrapper