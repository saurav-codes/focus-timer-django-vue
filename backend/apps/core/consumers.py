from channels.generic.websocket import SyncConsumer


class TasksConsumer(SyncConsumer):
    def websocket_connect(self, event):
        user = self.scope.get("user")
        print(
            f"WebSocket connected by user: {user.username if user.is_authenticated else 'Anonymous'}"
        )
        # Accept the WebSocket connection
        self.send({"type": "websocket.accept"})
        # Send a test message to verify connection
        self.send(
            {"type": "websocket.send", "text": "WebSocket connection established"}
        )

    def websocket_receive(self, event):
        # Handle incoming messages
        message = event.get("text", "")
        print(f"Received message: {message}")
        # You can process the message and send a response if needed

    def websocket_disconnect(self, event):
        print("WebSocket disconnected")
        # Handle disconnection logic if necessary
