import discord
import os
import firebase_admin
from firebase_admin import firestore
import json


client = discord.Client()

cred = firebase_admin.credentials.Certificate("serviceAccountKey.json")  # the 'password' for the database, stored in separate file
firebase_admin.initialize_app(cred)
db = firebase_admin.firestore.client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content
    if msg == 'hello':
        await message.channel.send('Hello')
    elif msg.startswith('$ADD'):
        json_list = msg[5:]
        str_list = json.loads(json_list)
        for course_item in str_list:
            result = db.collection('Fall2021').document(course_item['course']).get()
            if not result.exists:
                db.collection('Fall2021').document(course_item['course']).set({
                    "item": [{"name": course_item["name"], "date": course_item["date"]}]
                })
            else:
                db.collection('Fall2021').document(course_item['course']).update({
                    "item": firestore.ArrayUnion([{"name": course_item["name"], "date": course_item["date"]}])
                })
    elif msg == 'deadlines':
        course_list = []
        docs = db.collection('Fall2021').get()
        for doc in docs:
            course_dict = doc.to_dict()
            course_list.append(course_dict)
        print(course_list)
        string_of_deadlines = f"""Deadlines:"""
        for course in course_list:
            assignments_list = course['item']
            for assignment in assignments_list:
                string_of_deadlines += f"\t\n{assignment['name']} ----- {assignment['date']}"
        await message.channel.send(string_of_deadlines)



client.run('token goes here')  # put a token!
