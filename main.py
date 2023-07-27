import os
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import asyncio
import difflib
import logging
import sys
import validators
from math import ceil
import glob

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

TOKEN = 'TOKEN'

intents = discord.Intents.default()
intents.message_content = True

AUTHORIZED_USER_ID = #change this to your discord id to be able to use .clean

client = commands.Bot(command_prefix=".", intents=intents, help_command=None)


@client.event
async def on_message(message):
    print(message.author, message.content, message.channel.id)
    await client.process_commands(message)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    print(f'Rust Solutions is now Online!')


@client.command()
@has_permissions(administrator=True)
async def clean(ctx, llimit: int):
    await ctx.channel.purge(limit=llimit)
    await ctx.send('Cleared by <@{.author.id}>'.format(ctx))


@clean.error
async def clear_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send("You cant do that!")


@client.command()
async def commands(ctx):
    await ctx.send(f'".craft type amount" pure sulfur to craft a type of explosive, ex: ".craft c4/rocket 8"\n'
                   f'".wall level amount" calculates explosive types needed, avail: wood, stone, metal, hqm\n'
                   f'".door type amount" calculates explosive types needed, avail: wood, sheet, metal, garage, heww, hesw\n'
                   f'".raid string" example" ".raid 1 wood door, 1 sheet door, 1 garage door, 1 metal door, 1 wood wall, 1 stone wall, 1 metal wall, 1 hqm wall, 1 heww, 1 hesw"\n'
                   f'".raidex string" example: ".raidex 1 wood door, 1 sheet door, 1 garage door, 1 metal door, 1 wood wall, 1 stone wall, 1 metal wall, 1 hqm wall, 1 heww, 1 hesw"\n'
                   f'this modification of .raid calculates the cheapest pathway to raid any combination of objects. although, it may tell you 1 less explosive ammo than needed. but,\n'
                   f'there is a 5% leniency in the programming which should give the raider more than enough to complete the raid\n'
                   f'".quarry multiplier diesel" estimates the time and yield of any number of diesel for a quarry\n'
                   f'\n')


@client.command()
async def craft(ctx, type: str, amount: int):
    type = type.lower()
    type = difflib.get_close_matches(type, ['c4', 'rocket', 'explosive'], n=1)[0] if difflib.get_close_matches(type,
                                                                                                               ['c4',
                                                                                                                'rocket',
                                                                                                                'explosive'],
                                                                                                               n=1) else type
    if type == 'c4':
        gunpowder = 1000 * amount  
        sulfur = 200 * amount  
        metal_fragments = 200 * amount  
        low_grade_fuel = 60 * amount
        tech_trash = 2 * amount
        cloth = 3 * amount
        await ctx.send(f'For {amount} C4, you need {sulfur + gunpowder * 2} SULFUR or:\n'
                       f'{gunpowder} gunpowder\n'
                       f'{low_grade_fuel} fuel\n'
                       f'{sulfur} sulfur\n'
                       f'{metal_fragments} metal fragments\n'
                       f'{tech_trash} tech trash\n'
                       f'{cloth} cloth')

    elif type == 'rocket':
        gunpowder = 650 * amount  
        sulfur = 100 * amount  
        metal_fragments = 100 * amount  
        low_grade_fuel = 30 * amount
        pipes = 2 * amount
        await ctx.send(f'For {amount} rockets, you need {sulfur + gunpowder * 2} SULFUR or:\n'
                       f'{gunpowder} gunpowder\n'
                       f'{low_grade_fuel} fuel\n'
                       f'{sulfur} sulfur\n'
                       f'{metal_fragments} metal fragments\n'
                       f'{pipes} pipes')
    elif type == 'explosive':
        gunpowder = 20 * amount / 2
        sulfur = 10 * amount / 2
        metal = 10 * amount / 2
        await ctx.send(f'For {amount} explosive ammo, you need {sulfur + gunpowder * 2} SULFUR or:\n'
                       f'{gunpowder} gunpowder\n'
                       f'{sulfur} sulfur\n'
                       f'{metal} metal')


@client.command()
async def wall(ctx, level: str, amount: int = 1, send_message: bool = True):
    level = level.lower()
    level = difflib.get_close_matches(level, ['wood', 'stone', 'metal', 'hqm'], n=1)[0] if difflib.get_close_matches(
        level, ['wood', 'stone', 'metal', 'hqm'], n=1) else level

    materials = {
        'wood': 250,
        'stone': 500,
        'metal': 1000,
        'hqm': 2000
    }

    c4_damage = {
        'wood': 495,
        'stone': 275,
        'metal': 275,
        'hqm': 275
    }

    rocket_damage = {
        'wood': 247.6,
        'stone': 137.6,
        'metal': 137.6,
        'hqm': 137.6
    }

    sulfur_per_c4 = 2200
    sulfur_per_rocket = 1400

    if level in materials:
        c4_needed_total = 0
        rockets_needed_total = 0
        for _ in range(amount):
            total_health = materials[level]
            min_sulfur = float('inf')  
            for i in range(ceil(total_health / c4_damage[level]) + 1):  
                c4_needed = i
                remaining_health = total_health - c4_needed * c4_damage[level]
                rockets_needed = max(0, ceil(
                    remaining_health / rocket_damage[level]))  
                sulfur_cost = c4_needed * sulfur_per_c4 + rockets_needed * sulfur_per_rocket
                if sulfur_cost < min_sulfur:  
                    min_sulfur = sulfur_cost
                    c4_needed_total = c4_needed
                    rockets_needed_total = rockets_needed

        sulfur_for_c4 = c4_needed_total * sulfur_per_c4
        sulfur_for_rockets = rockets_needed_total * sulfur_per_rocket
        c4_only = ceil(materials[level] / c4_damage[level]) * amount
        rockets_only = ceil(materials[level] / rocket_damage[level]) * amount
        sulfur_needed = sulfur_for_c4 + sulfur_for_rockets

        if send_message:
            await ctx.send(f'For {amount} {level} level walls, you need:\n'
                           f'{c4_needed_total} C4 and {rockets_needed_total} rockets, total sulfur: {sulfur_for_c4 + sulfur_for_rockets}\n'
                           f'OR\n'
                           f'{c4_only} C4, sulfur: {c4_only * sulfur_per_c4}\n'
                           f'{rockets_only} rockets, sulfur: {rockets_only * sulfur_per_rocket}\n'
                           f'Optimal pathway is {ceil(100 * ((c4_only * sulfur_per_c4) / (sulfur_for_c4 + sulfur_for_rockets)))}% better than c4 and\n'
                           f'{ceil(100 * ((rockets_only * sulfur_per_rocket) / (sulfur_for_c4 + sulfur_for_rockets)))}% better than the rockets pathway')
            return c4_needed_total, rockets_needed_total, sulfur_needed, c4_only * sulfur_per_c4, rockets_only * sulfur_per_rocket
        else:
            return c4_needed_total, rockets_needed_total, sulfur_needed, c4_only * sulfur_per_c4, rockets_only * sulfur_per_rocket
    else:
        await ctx.send('Invalid level. Valid levels are wood, stone, metal, hqm.')


@client.command()
async def door(ctx, type: str, amount: int = 1, send_message: bool = True):
    type = type.lower()
    type = difflib.get_close_matches(type, ['wood', 'sheet', 'metal', 'garage', 'ladder', 'heww', 'hesw'], n=1)[0] \
        if difflib.get_close_matches(type, ['wood', 'sheet', 'metal', 'garage', 'ladder', 'heww', 'hesw'],
                                     n=1) else type

    door_health = {
        'wood': 200,
        'sheet': 250,
        'garage': 600,
        'metal': 1000,
        'ladder': 500,
        'heww': 500,
        'hesw': 500,
    }

    c4_damage = {
        'wood': 1100,
        'sheet': 440,
        'garage': 440,
        'metal': 440,
        'ladder': 440,
        'heww': 495,
        'hesw': 275,
    }

    rocket_damage = {
        'wood': 550.4,
        'sheet': 220.4,
        'garage': 220.4,
        'metal': 220.4,
        'ladder': 220.4,
        'heww': 247.6,
        'hesw': 137.6,
    }

    sulfur_per_c4 = 2200
    sulfur_per_rocket = 1400

    if type in door_health:
        c4_needed_total = 0
        rockets_needed_total = 0
        for _ in range(amount):
            total_health = door_health[type]
            min_sulfur = float('inf')  
            for i in range(ceil(total_health / c4_damage[type]) + 1):  
                c4_needed = i
                remaining_health = total_health - c4_needed * c4_damage[type]
                rockets_needed = max(0, ceil(
                    remaining_health / rocket_damage[type]))  
                sulfur_cost = c4_needed * sulfur_per_c4 + rockets_needed * sulfur_per_rocket
                if sulfur_cost < min_sulfur:  
                    min_sulfur = sulfur_cost
                    c4_needed_total = c4_needed
                    rockets_needed_total = rockets_needed

        sulfur_for_c4 = c4_needed_total * sulfur_per_c4
        sulfur_for_rockets = rockets_needed_total * sulfur_per_rocket
        c4_only = ceil(door_health[type] / c4_damage[type]) * amount
        rockets_only = ceil(door_health[type] / rocket_damage[type]) * amount
        sulfur_needed = sulfur_for_c4 + sulfur_for_rockets

        if send_message:
            await ctx.send(f'For {amount} {type} doors, you need:\n'
                           f'{c4_needed_total} C4 and {rockets_needed_total} rockets, total sulfur: {sulfur_for_c4 + sulfur_for_rockets}\n'
                           f'OR\n'
                           f'{c4_only} C4, sulfur: {c4_only * sulfur_per_c4}\n'
                           f'{rockets_only} rockets, sulfur: {rockets_only * sulfur_per_rocket}\n'
                           f'Optimal pathway is {ceil(100 * ((c4_only * sulfur_per_c4) / (sulfur_for_c4 + sulfur_for_rockets)))}% better than c4 and\n'
                           f'{ceil(100 * ((rockets_only * sulfur_per_rocket) / (sulfur_for_c4 + sulfur_for_rockets)))}% better than the rockets pathway')
            return c4_needed_total, rockets_needed_total, sulfur_needed, c4_only * sulfur_per_c4, rockets_only * sulfur_per_rocket
        else:
            return c4_needed_total, rockets_needed_total, sulfur_needed, c4_only * sulfur_per_c4, rockets_only * sulfur_per_rocket
    else:
        await ctx.send('Invalid door type. Valid types are wood, sheet, metal, garage, ladder, heww, hesw.')


@client.command()
async def raid(ctx, *, query: str):
    items = query.split(', ')
    sulfur_total = 0
    c4_total = 0
    rockets_total = 0
    sulfur_total_c4 = 0
    sulfur_total_rockets = 0
    message = ""
    for item in items:
        split_item = item.split(' ', 1)
        if len(split_item) == 2:
            amount, level = split_item
            amount = int(amount)  # ensure amount is an integer
        else:  # there was no amount given, default to 1
            amount = 1
            level = split_item[0]  # the item is the level
        if 'wall' in level:
            c4_needed, rockets_needed, sulfur_needed, sulfur_c4, sulfur_rockets = await wall(ctx, level.split(' ')[0],
                                                                                             amount, False)
        else:
            c4_needed, rockets_needed, sulfur_needed, sulfur_c4, sulfur_rockets = await door(ctx, level, amount, False)
        sulfur_total += sulfur_needed
        c4_total += c4_needed
        rockets_total += rockets_needed
        sulfur_total_c4 += sulfur_c4
        sulfur_total_rockets += sulfur_rockets
        message += f"For {amount} {level}: {sulfur_needed} sulfur"
        if c4_needed > 0 and rockets_needed > 0:
            message += f" ({c4_needed} C4 and {rockets_needed} rockets)\n"
        elif c4_needed > 0:
            message += f" ({c4_needed} C4)\n"
        elif rockets_needed > 0:
            message += f" ({rockets_needed} rockets)\n"
    message += f"Total sulfur needed for the raid: {sulfur_total}"
    if c4_total > 0:
        message += f" ({c4_total} C4"
    if rockets_total > 0:
        message += f" and {rockets_total} rockets)\n"
    if c4_total > 0:
        message += f"Sulfur needed for {c4_total} C4 only: {ceil(c4_total * 2200)}\n"
    if rockets_total > 0:
        message += f"Sulfur needed for {rockets_total} rockets only: {ceil(rockets_total * 1400)}"

    embed = Embed(title="Raid Information", description=message, color=0x3498db)
    await ctx.send(embed=embed)


async def raidex_wall(ctx, level: str, amount: int = 1, send_message: bool = True):
    level = level.lower()
    level = difflib.get_close_matches(level, ['wood', 'stone', 'metal', 'hqm'], n=1)[0] if difflib.get_close_matches(
        level, ['wood', 'stone', 'metal', 'hqm'], n=1) else level

    materials = {
        'wood': 250,
        'stone': 500,
        'metal': 1000,
        'hqm': 2000
    }

    c4_damage = {
        'wood': 495,
        'stone': 275,
        'metal': 275,
        'hqm': 275
    }

    rocket_damage = {
        'wood': 247.6,
        'stone': 137.6,
        'metal': 137.6,
        'hqm': 137.6
    }

    bullet_damage = {
        'wood': materials['wood'] / 49,
        'stone': materials['stone'] / 185,
        'metal': materials['metal'] / 400,
        'hqm': materials['hqm'] / 799
    }

    sulfur_per_c4 = 2200
    sulfur_per_rocket = 1400
    sulfur_per_bullet = 25

    if level in materials:
        c4_needed_total = 0
        rockets_needed_total = 0
        bullets_needed_total = 0
        sulfur_needed_total = 0  
        for _ in range(amount):
            total_health = materials[level]
            c4_needed = total_health // c4_damage[level]
            remaining_health = max(0, total_health % c4_damage[level])  
            rockets_needed = remaining_health // rocket_damage[level]
            remaining_health = max(0,
                                   remaining_health % rocket_damage[level])  
            bullets_needed = ceil(remaining_health / bullet_damage[level])
            c4_needed_total += c4_needed
            rockets_needed_total += rockets_needed
            bullets_needed_total += bullets_needed
          
            sulfur_for_c4 = c4_needed * sulfur_per_c4
            sulfur_for_rockets = rockets_needed * sulfur_per_rocket
            sulfur_for_bullets = bullets_needed * sulfur_per_bullet
            sulfur_needed = sulfur_for_c4 + sulfur_for_rockets + sulfur_for_bullets

            sulfur_needed_total += sulfur_needed  

        sulfur_for_c4 = c4_needed_total * sulfur_per_c4
        sulfur_for_rockets = rockets_needed_total * sulfur_per_rocket
        sulfur_for_bullets = bullets_needed_total * sulfur_per_bullet
        sulfur_needed = sulfur_for_c4 + sulfur_for_rockets + sulfur_for_bullets

        sulfur_for_c4_and_bullets = (c4_needed_total - 1) * sulfur_per_c4 + sulfur_for_bullets
        sulfur_for_c4_and_rockets_and_bullets = (
                                                            c4_needed_total - 2) * sulfur_per_c4 + sulfur_for_rockets + sulfur_for_bullets
        sulfur_for_c4_and_rockets = c4_needed_total * sulfur_per_c4 + sulfur_for_rockets

        min_sulfur = min(sulfur_needed, sulfur_for_c4_and_bullets, sulfur_for_c4_and_rockets_and_bullets,
                         sulfur_for_c4_and_rockets)

        if send_message:
            await ctx.send(f'For {amount} {level} level walls, you need:\n'
                           f'{c4_needed_total} C4, {rockets_needed_total} rockets, and {bullets_needed_total} bullets, total sulfur: {min_sulfur}\n')
            return c4_needed_total, rockets_needed_total, bullets_needed_total, min_sulfur, sulfur_for_c4, sulfur_for_rockets, sulfur_for_bullets
        else:
            return c4_needed_total, rockets_needed_total, bullets_needed_total, min_sulfur, sulfur_for_c4, sulfur_for_rockets, sulfur_for_bullets
    else:
        await ctx.send('Invalid level. Valid levels are wood, stone, metal, hqm.')


async def raidex_door(ctx, type: str, amount: int = 1, send_message: bool = True):
    type = type.lower()
    type = difflib.get_close_matches(type, ['wood', 'sheet', 'metal', 'garage', 'ladder', 'heww', 'hesw'], n=1)[0] \
        if difflib.get_close_matches(type, ['wood', 'sheet', 'metal', 'garage', 'ladder', 'heww', 'hesw'],
                                     n=1) else type

    door_health = {
        'wood': 200,
        'sheet': 250,
        'garage': 600,
        'metal': 1000,
        'ladder': 500,
        'heww': 500,
        'hesw': 500,
    }

    c4_damage = {
        'wood': 1100,
        'sheet': 440,
        'garage': 440,
        'metal': 440,
        'ladder': 440,
        'heww': 495,
        'hesw': 275,
    }

    rocket_damage = {
        'wood': 550.4,
        'sheet': 220.4,
        'garage': 220.4,
        'metal': 220.4,
        'ladder': 220.4,
        'heww': 247.6,
        'hesw': 137.6,
    }

    bullet_damage = {
        'wood': door_health['wood'] / 19,
        'sheet': door_health['sheet'] / 63,
        'garage': door_health['garage'] / 150,
        'metal': door_health['metal'] / 250,
        'ladder': door_health['ladder'] / 63,  
        'heww': door_health['heww'] / 98,
        'hesw': door_health['hesw'] / 185,
    }

    sulfur_per_c4 = 2200
    sulfur_per_rocket = 1400
    sulfur_per_bullet = 25

    if type in door_health:
        c4_needed_total = 0
        rockets_needed_total = 0
        bullets_needed_total = 0
        sulfur_needed_total = 0  
        for _ in range(amount):
            total_health = door_health[type]
            c4_needed = total_health // c4_damage[type]
            remaining_health = max(0, total_health % c4_damage[type]) 
            rockets_needed = remaining_health // rocket_damage[type]
            remaining_health = max(0, remaining_health % rocket_damage[type])  
            bullets_needed = ceil(remaining_health / bullet_damage[type])
            c4_needed_total += c4_needed
            rockets_needed_total += rockets_needed
            bullets_needed_total += bullets_needed

            sulfur_for_c4 = c4_needed * sulfur_per_c4
            sulfur_for_rockets = rockets_needed * sulfur_per_rocket
            sulfur_for_bullets = bullets_needed * sulfur_per_bullet
            sulfur_needed = sulfur_for_c4 + sulfur_for_rockets + sulfur_for_bullets

            sulfur_needed_total += sulfur_needed  

        sulfur_for_c4 = c4_needed_total * sulfur_per_c4
        sulfur_for_rockets = rockets_needed_total * sulfur_per_rocket
        sulfur_for_bullets = bullets_needed_total * sulfur_per_bullet
        sulfur_needed = sulfur_for_c4 + sulfur_for_rockets + sulfur_for_bullets

        sulfur_for_c4_and_bullets = (c4_needed_total - 1) * sulfur_per_c4 + sulfur_for_bullets
        sulfur_for_c4_and_rockets_and_bullets = (
                                                            c4_needed_total - 2) * sulfur_per_c4 + sulfur_for_rockets + sulfur_for_bullets
        sulfur_for_c4_and_rockets = c4_needed_total * sulfur_per_c4 + sulfur_for_rockets

        min_sulfur = min(sulfur_needed, sulfur_for_c4_and_bullets, sulfur_for_c4_and_rockets_and_bullets,
                         sulfur_for_c4_and_rockets)

        if send_message:
            await ctx.send(f'For {amount} {type} doors, you need:\n'
                           f'{c4_needed_total} C4, {rockets_needed_total} rockets, and {bullets_needed_total} bullets, total sulfur: {min_sulfur}\n')
            return c4_needed_total, rockets_needed_total, bullets_needed_total, min_sulfur, sulfur_for_c4, sulfur_for_rockets, sulfur_for_bullets
        else:
            return c4_needed_total, rockets_needed_total, bullets_needed_total, min_sulfur, sulfur_for_c4, sulfur_for_rockets, sulfur_for_bullets
    else:
        await ctx.send('Invalid door type. Valid types are wood, sheet, metal, garage, ladder, heww, hesw.')


@client.command()
async def raidex(ctx, *, query: str):
    items = query.split(', ')
    sulfur_total = 0
    c4_total = 0
    rockets_total = 0
    bullets_total = 0
    sulfur_total_c4 = 0
    sulfur_total_rockets = 0
    sulfur_total_bullets = 0
    message = ""
    for item in items:
        split_item = item.split(' ', 1)
        if len(split_item) == 2:
            amount, level = split_item
            amount = int(amount)  
        else:  
            amount = 1
            level = split_item[0]  
        if 'wall' in level:
            c4_needed, rockets_needed, bullets_needed, sulfur_needed, sulfur_c4, sulfur_rockets, sulfur_bullets = await raidex_wall(
                ctx, level.split(' ')[0], amount, False)
        else:
            c4_needed, rockets_needed, bullets_needed, sulfur_needed, sulfur_c4, sulfur_rockets, sulfur_bullets = await raidex_door(
                ctx, level, amount, False)
        sulfur_total += sulfur_needed
        c4_total += c4_needed
        rockets_total += rockets_needed
        bullets_total += bullets_needed
        sulfur_total_c4 += sulfur_c4
        sulfur_total_rockets += sulfur_rockets
        sulfur_total_bullets += sulfur_bullets
        item_message = f"For {amount} {level}: {int((c4_total * 2200) + (rockets_total * 1400) + (bullets_total * 25))} sulfur ("
        if c4_needed > 0:
            item_message += f"{c4_needed} c4, "
        if rockets_needed > 0:
            item_message += f"{int(rockets_needed)} rockets, "
        if bullets_needed > 0:
            item_message += f"{bullets_needed} explosivebullet"
        item_message += ")\n"
        message += item_message
    bullets_total_adjusted = ceil(bullets_total * 1.05)
    if bullets_total_adjusted % 2 != 0:  
        bullets_total_adjusted += 1  
    message += f"Total sulfur needed for the raid: {int((c4_total * 2200) + (rockets_total * 1400) + (int(bullets_total_adjusted) * 25))} ({c4_total} c4, {int(rockets_total)} rockets, and about {int(bullets_total_adjusted)} explosivebullet)\n"
    message += f"sulfur needed for {c4_total} <c4 only: {c4_total * 2200}\n"  
    message += f"sulfur needed for {int(rockets_total)} rockets only: {int(rockets_total * 1400)}\n"  
    message += f"sulfur needed for {int(bullets_total_adjusted)} explosivebullet only: {int(bullets_total_adjusted) * 25}"  

    embed = Embed(title="Raid Information", description=message, color=0x3498db)
    await ctx.send(embed=embed)


from discord import Embed, Color


@client.command()
async def quarry(ctx, multi: float = 3, diesel: int = 1):

    embed = Embed(title="Quarry and Excavator Results", color=Color.from_rgb(32, 101, 141))

    quarry_output = f"{diesel} dieselwill produce {ceil(1000 * diesel * multi)} sulfur "
    quarry_output += f"{ceil(50 * diesel * multi)} hqm or {ceil(1000 * diesel * multi)} metal and {ceil(5000 * diesel * multi)} stone at quarry"
    embed.add_field(name="Quarry Output", value=quarry_output, inline=False)

    quarry_runtime_seconds = int(2.17 * 60 * diesel) 
    quarry_hours, quarry_remainder = divmod(quarry_runtime_seconds, 3600)
    quarry_minutes, quarry_seconds = divmod(quarry_remainder, 60)
    quarry_runtime = f"{quarry_hours} hours {quarry_minutes} minutes {quarry_seconds} seconds"
    embed.add_field(name="Quarry Runtime", value=quarry_runtime, inline=False)

    excavator_output = f"{diesel} diesel will produce {ceil(2000 * diesel * multi)} sulfur "
    excavator_output += f"{ceil(100 * diesel * multi)} hqm {ceil(5000 * diesel * multi)} metal or {ceil(10000 * diesel * multi)} stone at excavator"
    embed.add_field(name="Excavator Output", value=excavator_output, inline=False)

    excavator_runtime_seconds = 2 * 60 * diesel  
    excavator_hours, excavator_remainder = divmod(excavator_runtime_seconds, 3600)
    excavator_minutes, excavator_seconds = divmod(excavator_remainder, 60)
    excavator_runtime = f"{excavator_hours} hours {excavator_minutes} minutes {excavator_seconds} seconds"
    embed.add_field(name="Excavator Runtime", value=excavator_runtime, inline=False)

    await ctx.send(embed=embed)
  
client.run(TOKEN, log_handler=handler)
