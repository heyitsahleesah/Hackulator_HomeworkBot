import discord
import firebase_admin
from firebase_admin import firestore
import json
from datetime import date

client = discord.Client()

cred = firebase_admin.credentials.Certificate("serviceAccountKey.json")  # the 'password' for the database
firebase_admin.initialize_app(cred)
db = firebase_admin.firestore.client()


@client.event
async def on_ready():
    # Get the channel ID of a text channel in the server
    text_channel_list = []
    for guild in client.guilds:
        for channel in guild.text_channels:
            text_channel_list.append(channel)
    print(text_channel_list)
    # Send a starting message, when the bot is loaded / restarted
    welcome_message = "To get started, type:  $help"
    print('We have logged in as {0.user}'.format(client))
    channel = client.get_channel(926969232518959107)  # the selected channel ID goes in here
    await channel.send(welcome_message)  # send a message to the selected channel


@client.event
async def on_message(message):  # the main command handling function
    if message.author == client.user:  # bot ignores all of its own messages
        return

    msg = message.content  # discord message as a string
    if msg == 'hello':
        await message.channel.send('Hello!')

    elif msg == '$help':
        add_command = '$ADD [{"course": "COMP1510", "name": "lab 12", "date": "2022-01-19"}, {"course": "COMP1537", "name": "Assignment 17", "date": "2021-11-19"}]'
        help_message = " - To check all assignments, type: deadlines \n\n" \
                       " - To add assignments refer to this example command: \n\n\t\t" \
                       + add_command + "\n\n\t\tJust replace the values of each key-value pair. The command must be in this format and include all these keys\n\n" \
                                       " - To remove old dates, type: $UPDATE"
        await message.channel.send(help_message)

    elif msg.startswith('$ADD'):  # adding new assignments
        # example message: $ADD [{"course": "CP1100", "name": "Journal 11", "date": "2021-01-23"}, {"course": "CP1537", "name": "Final Exam", "date": "2022-04-19"}]
        try:
            str_list = msg[5:]  # take only the list part after $ADD
            json_list = json.loads(str_list)  # parse JSON
            for course_item in json_list:
                result = db.collection('Fall2021').document(course_item['course']).get()  # doc id's are set to course id's
                if not result.exists:  # if there isn't a doc already, create and add the courses
                    db.collection('Fall2021').document(course_item['course']).set({
                        "courseID": course_item['course'],
                        "items": [{"name": course_item["name"], "date": course_item["date"]}]
                    })
                else:  # if there is a doc, add to the assignments list (firestore array)
                    db.collection('Fall2021').document(course_item['course']).update({
                        "items": firestore.ArrayUnion([{"name": course_item["name"], "date": course_item["date"]}])
                    })
            await message.channel.send('Courses added successfully!')
        except (KeyError, json.decoder.JSONDecodeError, ValueError):
            print("Incorrect format!")
            await message.channel.send("Incorrect format! For more information, please type:  $help")

    elif msg == 'deadlines' or msg == '$DEADLINES':  # this will output all the assignments in the database
        course_list = []
        docs = db.collection('Fall2021').get()
        for doc in docs:  # go through each course and convert them to dictionaries so we can manipulate with python
            course_dict = doc.to_dict()
            course_list.append(course_dict)
        print(course_list)
        # using the course list, create a string to output in a message to user
        string_of_deadlines = f"""Deadlines:"""
        for course in course_list:
            string_of_deadlines += \
                f"""
                {course['courseID']}
                """
            assignments_list = course['items']
            for assignment in assignments_list:
                string_of_deadlines += \
                    f"""
                    {assignment['name']} ----- {assignment['date']}
                    """
        await message.channel.send(string_of_deadlines)

    elif msg == '$UPDATE':  # get rid of assignments with past due dates
        present = date.today()  # right now, only supports days (no smaller units of time)
        docs = db.collection('Fall2021').get()
        for doc in docs:
            key = doc.id
            assignments = db.collection('Fall2021').document(key).get(field_paths={'items'}).to_dict()  # only get the assignments key-value pair for each doc/class
            # print(assignments)
            for assignment in assignments['items']:  # assignments['items'] is an array of all class assignments
                print(assignment)
                due_date = date.fromisoformat(assignment['date'])  # dates in firebase are stored as eg. 'YYYY-MM-DD'. Convert to python date format for comparison of other dates
                if due_date < present:
                    db.collection('Fall2021').document(key).update({
                        "items": firestore.ArrayRemove([assignment])
                    })
        print('update successful')
        await message.channel.send('Due dates updated successfully!')


client.run('token goes here')  # put a token!
