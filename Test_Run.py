import discord
import openpyxl
import datetime
import random
import os
from dotenv import load_dotenv
import pandas as pd

client = discord.Client()

encouragements = [
    "No time like the present",
    "You can do it!",
    "I believe in you!",
    "It will be easy",
]

# use builtin function to find the date on your own computer
current_date = datetime.datetime.now()
# convert the date to a readable format with only relevant information
printable_date = current_date.strftime("%m-%d")

# location of the excel file
file = 'DiscordExcel.xlsx'

# Open the workbook
wb = openpyxl.load_workbook(file)
sheet = wb.active


@client.event
async def on_ready():
    # message to show that the bot is logged in (connected properly)
    print('We have logged in as {0.user}'.format(client))


# Messageable.send has to be awaited while using discord
# function has to be asynchronous to use await
async def date_comparison(message):
    for rows in range(2, sheet.max_row + 1):
        # just reading the date here
        for columns in range(4, 5):
            print((sheet.cell(rows, 4).value[1:3]))
            cell_value = sheet.cell(row=rows, column=columns)
            # iteration starts at 1 with openpyxl, we are comparing the same indices(month)
            # if due-month > current month or due-day > current-day given the same month
            if int(cell_value.value[1:3]) > int(printable_date[0:2]) or int(cell_value.value[1:3]) == \
                    int(printable_date[0:2] and int(cell_value.value[4:6]) > int(printable_date[3:5])):
                await message.channel.send(f"{sheet.cell(rows, 1).value} {sheet.cell(rows, 2).value} "
                                           f"{sheet.cell(rows, 3).value}  Difficulty: {sheet.cell(rows, 5).value}")
                # excel auto formats to non-numerical date without 1 space, so I'm stripping the space
                # could git rid of the strip() if someone knows how to properly format excel dates without auto-conversion
                await message.channel.send(f'Due: {cell_value.value.strip()}')


@client.event
async def on_message(message):
    # # what does this do? is it necessary?
    # if message.author == client.user:
    #     return
    if message.content.lower() == "deadlines" or message.content.lower() == "due".lower():
        await date_comparison(message)
        # for rows in range(2, sheet.max_row + 1):
        #     # just reading the date here
        #     for columns in range(4, 5):
        #         cell_value = sheet.cell(row=rows, column=columns)
        #         # iteration starts at 1 with openpyxl, we are comparing the same indices(month)
        #         # if due-month > current month or due-day > current-day given the same month
        #         if int(cell_value.value[1:3]) > int(printable_date[0:2]) or int(cell_value.value[1:3]) == \
        #                 int(printable_date[0:2] and int(cell_value.value[4:6]) > int(printable_date[3:5])):
        #             await message.channel.send(f"{sheet.cell(rows, 1).value} {sheet.cell(rows, 2).value} "
        #                                        f"{sheet.cell(rows, 3).value}  Difficulty: {sheet.cell(rows, 5).value}")
        #             # excel auto formats to non-numerical date without 1 space, so I'm stripping the space
        #             # could git rid of the strip() if someone knows how to properly format excel dates without auto-conversion
        #             await message.channel.send(f'Due: {cell_value.value.strip()}')
        await message.channel.send(random.choice(encouragements))

    # AttributeError: 'builtin_function_or_method' object has no attribute 'lower'
    # second part of conditional checks for a specific course
    elif message.content.startswith("deadlines") and len(message.content) == 14:
        for rows in range(2, sheet.max_row + 1):
            for columns in range(2, 3):
                cell_value = sheet.cell(row=rows, column=columns)
                if str(cell_value.value) == (message.content[10:]):
                    # this is a datechecker again, can probably be universally broken down into a helper somehow
                    if int(sheet.cell(rows, 4).value[1:3]) > int(printable_date[0:2]) or \
                            int(sheet.cell(rows, 4).value[1:3]) == int(printable_date[0:2]) and \
                            int(sheet.cell(rows, 4).value[4:6]) > int(printable_date[3:5]):
                        # await message.channel.send(f"{sheet.cell(rows, 1).value} {sheet.cell(rows, 2).value} "
                        #                            f"{sheet.cell(rows, 3).value}  Difficulty: {sheet.cell(rows, 5).value}")
                        # await message.channel.send(f'Due: {sheet.cell(rows, 4).value.strip()}')
                        # create dictionary of relevant values to use for dataframe
                        course_details = ({
                            "Name": [sheet.cell(rows, 1).value],
                            "#": [sheet.cell(rows, 2).value],
                            "Assignment": [sheet.cell(rows, 3).value],
                            "Difficulty": [sheet.cell(rows, 5).value],
                        })
                        # initialize dataframe to use with pandas to create a table
                        # all the keys are scalar values, so we must start with an index. Tried to use something non-intrusive
                        dataframe = pd.DataFrame(course_details, columns=["Name", "#", "Assignment", "Difficulty"], index=["course"])
                        # this is for discord formatting, as otherwise the spacing is off after conversion. Ticks don't
                        # look the best, but I'm not sure what else to use
                        await message.channel.send('\```' + dataframe.to_string() + '')
        await message.channel.send(random.choice(encouragements))

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client.run(TOKEN)
# client.run("OTI2NjU4NTM4NDcyODk4NjUw.Yc-4BA.z2nuqeDzh7TerQp0MNx6VZoIJ80")

