from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id
        
    @staticmethod
    def get(user_id):
        # This is a simple implementation. In a real application,
        # you would typically load the user from a database
        if user_id == 1:
            return User(1)
        return None 