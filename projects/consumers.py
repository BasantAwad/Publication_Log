import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser, User
from .models import Message, MessageRequest, Notification, UserProfile
from django.utils import timezone
from datetime import timedelta
from django.db import models

class MessagingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Join user's personal channel
        self.user_channel = f"user_{self.user.id}"
        await self.channel_layer.group_add(
            self.user_channel,
            self.channel_name
        )
        
        # Join online users group
            await self.channel_layer.group_add(
            'online_users',
                self.channel_name
            )
        
        # Mark user as online
        await self.mark_user_online(True)
        
            await self.accept()
        
        # Send online status to all connected users
        await self.channel_layer.group_send(
            'online_users',
            {
                'type': 'user_status',
                'user_id': self.user.id,
                'status': 'online'
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and not isinstance(self.user, AnonymousUser):
            # Mark user as offline
            await self.mark_user_online(False)
            
            # Send offline status to all connected users
            await self.channel_layer.group_send(
                'online_users',
                {
                    'type': 'user_status',
                    'user_id': self.user.id,
                    'status': 'offline'
                }
            )
            
            # Leave user's personal channel
            await self.channel_layer.group_discard(
                self.user_channel,
                self.channel_name
            )
            
            # Leave online users group
            await self.channel_layer.group_discard(
                'online_users',
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'send_message':
            await self.handle_send_message(data)
        elif message_type == 'mark_read':
            await self.handle_mark_read(data)
        elif message_type == 'send_request':
            await self.handle_send_request(data)
        elif message_type == 'approve_request':
            await self.handle_approve_request(data)
        elif message_type == 'reject_request':
            await self.handle_reject_request(data)
        elif message_type == 'typing':
            await self.handle_typing(data)

    async def handle_send_message(self, data):
        recipient_id = data.get('recipient_id')
        content = data.get('content')
        
        if not recipient_id or not content:
            return
        
        # Check if there's an approved request between users
        has_approved_request = await self.check_approved_request(recipient_id)
        if not has_approved_request:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'You need an approved message request to send messages'
            }))
            return
        
        # Create message
        message = await self.create_message(recipient_id, content)
        
        # Send to recipient if online
        await self.channel_layer.group_send(
            f"user_{recipient_id}",
            {
                'type': 'new_message',
                'message': {
                    'id': message.id,
                    'sender_id': self.user.id,
                    'sender_name': self.user.username,
                    'content': message.content,
                    'sent_at': message.sent_at.isoformat(),
                    'is_read': False
                }
            }
        )
        
        # Create notification
        await self.create_notification(recipient_id, 'message_received', message)

    async def handle_mark_read(self, data):
        message_id = data.get('message_id')
        if message_id:
            await self.mark_message_read(message_id)
            
            # Notify sender that message was read
            message = await self.get_message(message_id)
            if message and message.sender_id != self.user.id:
                await self.channel_layer.group_send(
                    f"user_{message.sender_id}",
                    {
                        'type': 'message_read',
                        'message_id': message_id
                    }
                )

    async def handle_send_request(self, data):
        recipient_id = data.get('recipient_id')
        message_text = data.get('message', '')
        
        if not recipient_id:
            return
        
        # Check if request already exists
        existing_request = await self.get_existing_request(recipient_id)
        if existing_request:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'A message request already exists with this user'
            }))
            return
        
        # Create message request
        request = await self.create_message_request(recipient_id, message_text)
        
        # Send notification to recipient
        await self.channel_layer.group_send(
            f"user_{recipient_id}",
            {
                'type': 'new_request',
                'request': {
                    'id': request.id,
                    'sender_id': self.user.id,
                    'sender_name': self.user.username,
                    'message': request.initial_message,
                    'sent_at': request.sent_at.isoformat()
                }
            }
        )
        
        # Create notification
        await self.create_notification(recipient_id, 'message_request', None, request)

    async def handle_approve_request(self, data):
        request_id = data.get('request_id')
        if request_id:
            request = await self.approve_message_request(request_id)
            if request:
                # Notify sender that request was approved
                await self.channel_layer.group_send(
                    f"user_{request.sender_id}",
                    {
                        'type': 'request_approved',
                        'request_id': request_id,
                        'recipient_name': self.user.username
                    }
                )
                
                # Create notification
                await self.create_notification(request.sender_id, 'request_approved', None, request)

    async def handle_reject_request(self, data):
        request_id = data.get('request_id')
        if request_id:
            request = await self.reject_message_request(request_id)
            if request:
                # Notify sender that request was rejected
                await self.channel_layer.group_send(
                    f"user_{request.sender_id}",
                    {
                        'type': 'request_rejected',
                        'request_id': request_id,
                        'recipient_name': self.user.username
                    }
                )

    async def handle_typing(self, data):
        recipient_id = data.get('recipient_id')
        is_typing = data.get('is_typing', False)
        
        if recipient_id:
            await self.channel_layer.group_send(
                f"user_{recipient_id}",
                {
                    'type': 'user_typing',
                    'user_id': self.user.id,
                    'user_name': self.user.username,
                    'is_typing': is_typing
                }
            )

    # WebSocket event handlers
    async def new_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message']
        }))

    async def message_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_read',
            'message_id': event['message_id']
        }))

    async def new_request(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_request',
            'request': event['request']
        }))

    async def request_approved(self, event):
        await self.send(text_data=json.dumps({
            'type': 'request_approved',
            'request_id': event['request_id'],
            'recipient_name': event['recipient_name']
        }))

    async def request_rejected(self, event):
        await self.send(text_data=json.dumps({
            'type': 'request_rejected',
            'request_id': event['request_id'],
            'recipient_name': event['recipient_name']
        }))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_typing',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'is_typing': event['is_typing']
        }))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': event['user_id'],
            'status': event['status']
        }))

    # Database operations
    @database_sync_to_async
    def mark_user_online(self, is_online):
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.is_online = is_online
        profile.save()

    @database_sync_to_async
    def create_message(self, recipient_id, content):
        recipient = User.objects.get(id=recipient_id)
        return Message.objects.create(
            sender=self.user,
            recipient=recipient,
            content=content
        )

    @database_sync_to_async
    def mark_message_read(self, message_id):
        try:
            message = Message.objects.get(id=message_id, recipient=self.user)
            message.mark_as_read()
            return message
        except Message.DoesNotExist:
            return None

    @database_sync_to_async
    def get_message(self, message_id):
        try:
            return Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return None

    @database_sync_to_async
    def create_message_request(self, recipient_id, message):
        recipient = User.objects.get(id=recipient_id)
        return MessageRequest.objects.create(
            sender=self.user,
            recipient=recipient,
            initial_message=message
        )

    @database_sync_to_async
    def approve_message_request(self, request_id):
        try:
            request = MessageRequest.objects.get(id=request_id, recipient=self.user)
            request.status = 'approved'
            request.save()
            return request
        except MessageRequest.DoesNotExist:
            return None

    @database_sync_to_async
    def reject_message_request(self, request_id):
        try:
            request = MessageRequest.objects.get(id=request_id, recipient=self.user)
            request.status = 'rejected'
            request.save()
            return request
        except MessageRequest.DoesNotExist:
            return None

    @database_sync_to_async
    def check_approved_request(self, recipient_id):
        try:
            # Check if there's an approved request in either direction
            return MessageRequest.objects.filter(
                ((models.Q(sender=self.user, recipient_id=recipient_id) |
                  models.Q(sender_id=recipient_id, recipient=self.user)) &
                 models.Q(status='approved'))
            ).exists()
        except:
            return False

    @database_sync_to_async
    def get_existing_request(self, recipient_id):
        try:
            return MessageRequest.objects.filter(
                models.Q(sender=self.user, recipient_id=recipient_id) |
                models.Q(sender_id=recipient_id, recipient=self.user)
            ).first()
        except:
            return None

    @database_sync_to_async
    def create_notification(self, user_id, notification_type, message=None, message_request=None):
        user = User.objects.get(id=user_id)
        
        if notification_type == 'message_received':
            title = f"New message from {self.user.username}"
            content = f"You received a new message from {self.user.username}"
        elif notification_type == 'message_request':
            title = f"Message request from {self.user.username}"
            content = f"{self.user.username} wants to start a conversation with you"
        elif notification_type == 'request_approved':
            title = f"Message request approved by {self.user.username}"
            content = f"{self.user.username} approved your message request"
        else:
            title = "Notification"
            content = "You have a new notification"
        
        notification = Notification.objects.create(
            user=user,
            message=message,
            message_request=message_request,
            notification_type=notification_type,
            title=title,
            content=content
        )
        
        # Send email if user is not online
        profile, created = UserProfile.objects.get_or_create(user=user)
        if not profile.is_online:
            self.send_email_notification_sync(user, notification)
        
        return notification

    def send_email_notification_sync(self, user, notification):
        from django.core.mail import send_mail
        from django.conf import settings
        
        try:
            send_mail(
                subject=notification.title,
                message=notification.content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
            notification.is_email_sent = True
            notification.save()
        except Exception as e:
            print(f"Failed to send email notification: {e}")

    @database_sync_to_async
    def send_email_notification(self, user, notification):
        from django.core.mail import send_mail
        from django.conf import settings
        
        try:
            send_mail(
                subject=notification.title,
                message=notification.content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
            notification.is_email_sent = True
            notification.save()
        except Exception as e:
            print(f"Failed to send email notification: {e}")