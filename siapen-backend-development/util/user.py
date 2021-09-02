

def get_user(self, user=None):
        if self.request and hasattr(self.request, "user"):
            user = self.request.user
        return user