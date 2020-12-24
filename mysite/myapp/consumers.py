#adapted from https://channels.readthedocs.io/en/stable/tutorial/index.html
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from . import models

class DocConsumer(WebsocketConsumer):
    def connect(self):
        self.doc_id = self.scope['url_route']['kwargs']['doc_id']
        self.group_doc_id = 'doc_%s' % self.doc_id
        self.user = self.scope['user']

        # Join doc group
        async_to_sync(self.channel_layer.group_add)(
            self.group_doc_id,
            self.channel_name
        )

        try:
            document = models.DocumentModel.objects.get(id=self.doc_id)
        except models.DocumentModel.DoesNotExist:
            document = None

        if document:
            if document.editors.filter(username=self.user) or document.public==True:
                self.accept()
                self.send(text_data=json.dumps({
                    'message': document.body
                }))

        
    def disconnect(self, close_code):
        # Leave doc group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_doc_id,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        document = models.DocumentModel.objects.get(id=self.doc_id)
        if document.editors.filter(username=self.user) or document.public==True:
            document.body = message
            document.save()

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.group_doc_id,
            {
                'type': 'message',
                'message': message
            }
        )

    # Receive message from room group
    def message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))