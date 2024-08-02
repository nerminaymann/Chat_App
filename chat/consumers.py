import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(WebsocketConsumer):

    def fetch_10_recent_messages(self,data):
        # print('fetch')
        messages = Message.last_10_messages()
        content = {
            'messages':self.messages_to_json(messages)
        }
        self.send_chat_message(content)


    def new_message(self,data):
        author = data['from']
        author_user = User.objects.filter(username=author)[0]
        message=Message.objects.create(author=author_user,content=data['message'])
        content={
            "command":"new_message",
            "message":self.message_to_json(message)
        }
        return self.send_chat_message(content)


    def messages_to_json(self,messages):
        result=[]
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self,message):
        return {
            'author':Message.author.username,
            'content':Message.content,
            'timestamp':str(Message.timestamp)
        }

    commands = {
        'fetch_messages':fetch_10_recent_messages,
        'new_message':new_message
    }

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        #grabbing the data
        data = json.loads(text_data)

        #grabbing commands from dict
        self.commands[data['command']](self,data)


        #grabbing the command key from dic

    def send_chat_message(self,message):
        # message = data["message"]
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    def send_message(self,message):
        self.send(text_data=json.dumps(message))


    # Receive message from room group
    def chat_message(self, event):
        #grabbing the msg from the event
        message = event["message"]

        # Send message to WebSocket
        # self.send(text_data=json.dumps({"message": message}))
        self.send(text_data=json.dumps(message))