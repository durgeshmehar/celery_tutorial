from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .tasks import send_email_thread
from django.contrib.auth.decorators import user_passes_test



import threading
from .models import *
from .forms import *

@login_required
def messageboard_view(request):
    messageboard = get_object_or_404(MessageBoard, id=1)
    print("message:" ,messageboard)
    form = MessageCreateForm()
    
    if request.method == 'POST':
        if request.user in messageboard.subscribers.all():
            form = MessageCreateForm(request.POST)
            if form.is_valid:
                try:
                    message = form.save(commit=False)
                    message.author = request.user
                    message.messageboard = messageboard
                    message.save()
                    send_email(message)
                except Exception as e:
                    print(f"Email sending failed: {e}")
                    messages.warning(request, f"Email sending failed: {e}")
            else:
                messages.warning(request, f'Invalid Form : {form.errors}')
        else:
            messages.warning(request, 'You need to be Subscribed!')
        return redirect('messageboard')
    
    context = {
        'messageboard' : messageboard,
        'form' : form
    }
    return render(request, 'a_messageboard/index.html', context)


@login_required
def subscribe(request):
    messageboard = get_object_or_404(MessageBoard, id=1)
    
    if request.user not in messageboard.subscribers.all():
        messageboard.subscribers.add(request.user)
    else:
        messageboard.subscribers.remove(request.user)
        
    return redirect('messageboard')

def send_email(message):
    messageboard = message.messageboard 
    subscribers = messageboard.subscribers.all()
    
    for subscriber in subscribers: 
        subject = f'Django Celery Message from {message.author.profile.name}'
        body = f'{message.author.profile.name}: {message.body}\n\nRegards from\nMy Message Board'

        send_email_thread.delay(subject, body, subscriber.email)

#         email_thread = threading.Thread(target=send_email_thread, args=(subject, body, subscriber))
#         email_thread.start()
        
        
# def send_email_thread(subject, body, subscriber):        
#     email = EmailMessage(subject, body, to=[subscriber.email])
#     email.send()

# newsletter
def isStaff(user):
    return user.is_staff

@user_passes_test(isStaff)
def newsletter(request):
    return render(request, 'a_messageboard/newsletter.html')
