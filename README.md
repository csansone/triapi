# TriAPI

Not for use in production environment.

MVP service to meet requirements:

Implement a REST API service for sending and receiving text messages:

1. Submit a message to a defined recipient, identified with some identifier, e.g. email-address, phone-number, user name or similar.

2. Fetch previously not fetched messages. This implies that the service should be aware about what messages that has been previously fetched.

3. Delete one or more messages.

4. Fetch messages (including previously fetched) ordered by time, according to start and stop index.

This service uses [Django](https://www.djangoproject.com/start/overview/) and [Django Rest Framework](https://www.django-rest-framework.org/) as its starting point.

Django is a good choice as it:

 - Reduces development time
 - Is well documented 
 - Has a massive community and therefore good support availability
 - Scales to meet the traffic needs of giants such as Disqus, DoorDash, Eventbrite, and Pinterest


## Quickstart

- Set up a Python 3.6 virtual environment using your preferred method (pyenv, venv, virtualenv, etc.)

- Clone this repository with

```
git clone https://github.com/csansone/triapi.git
```

*Note that depending on your environment, you may need to replace the `pip` command with `pip3` and/or the `python` command with `python3`.*

- Install requirements from pip:


```
cd triapi
pip install -r requirements.txt
```

- Run the following commands to prepare the environment and database:

```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

The service should now be running on Django's test server using a default SQLite database.

GET endpoints for users and messages should be live and browseable at:

http://127.0.0.1:8000/api/v1/users/

http://127.0.0.1:8000/api/v1/messages/

These and other endpoints return JSON, except when accessed with a browser user-agent.

When called from a browser, you get an easy to read HTML rendering, which also allows for POST and other requests to be made to the various endpoints. 

### Create a user

We are going to need a user to send messages to, so let's create one by using CURL in a new shell to **POST** to the `users/` endpoint with the key value pair `username=sam`.

Usernames are stored in a case-sensitive way, but case is ignored when retrieving data later.

```
curl -d username=sam http://127.0.0.1:8000/api/v1/users/
```

### Send a message

Now that we have our user, let's **POST** a couple of welcome messages to `messages/sam/`.

```
curl -d content="Hey Sammy, what's up?" http://127.0.0.1:8000/api/v1/messages/sam/

curl -d content="Welcome to the show!" http://127.0.0.1:8000/api/v1/messages/sam/
```

### Get messages

Calling the `messages/username/` endpoint returns all messages sent to the particular user. 

This call with the URL parameter `unread` set to "true" returns only messages not marked as read.

To return messages limited to a certain id range, use either or both URL parameters `from_index` and `to_index` with values set as the inclusive starting and ending ids to be retrieved. These can be used on their own or in conjunction with the `unread` parameter.

```
curl http://127.0.0.1:8000/api/v1/messages/sam/?unread=true

# [{"id":1,"created_at":"2019-03-20T22:00:14.705436Z","content":"Hey Sammy, what's up","fetched":false,"to_user":1},{"id":2,"created_at":"2019-03-20T23:12:21.499363Z","content":"Welcome to the show!","fetched":false,"to_user":1}]
```

It would not be very RESTful to alter these records on the server while receiving them from a **GET** request.

In practice, once the client has successfully received the messages, it should then send an explicit request to mark them as such. This could be done automatically or upon some user action client side.

### Mark messages as read

The `messages/batch/` endpoint is used for making certain changes to groups of one or more messages via **PATCH** requests.

We have received messages above with ids of 1 and 2, so let's go ahead and mark those as read.

The key value pairs must be:
{
    "action": "mark_as_read",
    "message_ids": "<SOME_MESSAGE IDS>"
}

...where <SOME_MESSAGE_IDS> is a string containing comma separated id values matching the messages to be updated.

The CURL request is shown below with no spaces before or after the comma, but it is unimportant as the application will ignore spaces if present in the string and work as expected.

```
curl -X PATCH -d action=mark_as_read -d message_ids="1,2" http://127.0.0.1:8000/api/v1/messages/batch/

# {"detail":"2 messages marked as read."}
```

Note that the detail simply states the quantity of messages that were found, even if they were already marked as read.

### Delete messages

A **PATCH** request to the `messages/batch/` endpont is also used for deleting any number of messages.

This usage differs from marking as read by replacing the "action" value with "delete".

**Are you sure?**
Deleting is irreversible. If you have been following along and are ready to continue deleting the sample messages, here is the CURL command:

```
curl -X PATCH -d action=mark_as_read -d message_ids="1,2" http://127.0.0.1:8000/api/v1/messages/batch/
```

### View or delete single message

The endpoint for these actions is `messages/<MESSAGE_ID>/`.

Sending a **GET** request will return the data related to the message.

To delete the message, send a **DELETE** request

No body or URL parameters are used for this endpoint.


## Endpoint Summary


| Endpoint | Method | Body | URL Params | Operation |
| -------- | ------ | ---- | ---------- | ------- |
| api/v1/users/ | GET |   |  |  List all users
| api/v1/users/ | POST | {"userame": "\<USERNAME>"} | | Add new user |
| api/v1/messages/ | GET | | from_index=\<int><br>to_index=\<int> | List all messages |
| api/v1/messages/ | POST | {"content": "<MESSAGE_TEXT>"<br>"to_user": "<USER_ID">}| | Create new message |
| api/v1/messages/\<USERNAME>/ | GET || unread=["true"\|"false"]<br>from_index=\<int><br>to_index=\<int> | List user messages|
| api/v1/messages/\<USERNAME>/ | POST | {"content": "<MESSAGE_TEXT>"} |  | Create new message|
| api/v1/messages/\<ID>/ | GET | | | Get single message detail |
| api/v1/messages/\<ID>/ | DELETE | | | Delete single message |
| api/v1/messages/batch/ | PATCH | {"message_ids": "\<id> [, ..\<id>,\<id>]",<br>"action": "mark_as_read"}| | Mark multiple messages as read |
| api/v1/messages/batch/ | PATCH | {"message_ids": "\<id> [, ..\<id>,\<id>]",<br>"action": "delete"}| | Delete multiple messages |
