from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Message(models.Model):
    author = models.ForeignKey(User,related_name='author_name',on_delete=models.CASCADE)
    content = models.TextField(max_length=400)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username

    #for paginating msgs and return the most recent 10 msgs in msg room
    def last_10_messages(self):
        return Message.objects.order_by('-timestamp').all()[:10]