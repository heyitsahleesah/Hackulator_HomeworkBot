import discord
import openpyxl
import datetime
import random

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
print(printable_date)

# location of the excel file
file = 'DiscordExcel.xlsx'

# Open the workbook
wb = openpyxl.load_workbook(file)
sheet = wb.active


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    # # what does this do? is it necessary?
    # if message.author == client.user:
    #     return

    if message.content == "deadlines" or message.content == "due":
        for rows in range(2, sheet.max_row + 1):
            # just reading the date here
            for columns in range(4, 5):
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
        await message.channel.send(random.choice(encouragements))


client.run("OTI2NjU4NTM4NDcyODk4NjUw.Yc-4BA.z2nuqeDzh7TerQp0MNx6VZoIJ80")
