#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import requests
import json
import queue
# import os
from os.path import abspath

from PIL import Image
from io import BytesIO

import datetime
import pytz

# from datetime import datetime, timedelta
from dateutil import parser

from easing_functions import *

sameDayColors = {
  0: '255, 255, 255',
  1: '242, 248, 251',
  2: '229, 241, 247',
  3: '216, 234, 243',
  4: '203, 227, 239',
  5: '190, 220, 235',
  6: '177, 213, 231',
  7: '164, 206, 227',
  8: '151, 199, 223',
  9: '138, 192, 219',
  10: '125, 185, 215',
  11: '112, 178, 211',
  12: '99, 171, 207',
  13: '86, 164, 203',
  14: '73, 157, 199',
  15: '43, 149, 185',
  16: '60, 150, 195',
  17: '73, 157, 199',
  18: '86, 164, 203',
  19: '99, 171, 207',
  20: '112, 178, 211',
  21: '125, 185, 215',
  22: '138, 192, 219',
  23: '151, 199, 223',
  24: '164, 206, 227',
  25: '177, 213, 231',
  26: '190, 220, 235',
  27: '203, 227, 239',
  28: '216, 234, 243',
  29: '229, 241, 247',
  30: '242, 248, 251',
  31: '255, 255, 255'
}

medalColors = {
    '1': {
      'background': '232, 185, 35',
      'color': '46, 36, 5'
    },
    '2': {
      'background': '202, 200, 196',
      'color': '72, 72, 72'
    },
    '3': {
      'background': '156, 82, 33',
      'color': '214, 214, 214'
    }
  }

textColor = graphics.Color(255, 255, 255)
yearBackground = graphics.Color(43, 149, 185)

font = graphics.Font()
font.LoadFont('/home/pi/rpi-rgb-led-matrix/fonts/matelight.bdf')

dateFont = graphics.Font()
dateFont.LoadFont('/home/pi/rpi-rgb-led-matrix/fonts/haxor-square.bdf')
timeFont = graphics.Font()
timeFont.LoadFont('/home/pi/rpi-rgb-led-matrix/fonts/boxxy.bdf')

central = pytz.timezone("US/Central")

def getEvents():
  link = "https://www.heher.io/olympics/api/graphql"
  headers = { 'Content-Type': 'application/json' }
  query = """query {
    olympiadBySlug(slug: "beijing-2022") {
      id
      upcomingEvents {
        nodes {
          id
          datetime
          event {
            id
            name
            team
            sport {
              id
              name
            }
          }
        }
      }
    }
  }"""

  r = requests.post(link, json={'query': query})
  json_data = json.loads(r.text)

  return json_data['data']['olympiadBySlug']['upcomingEvents']['nodes']

def renderEvents(events, canvas, font, movingPos, sameDay):
  now = datetime.datetime.now(central)
  verticalPos = 7

  for index, olympiadEvent in enumerate(events):
    timeDiff = olympiadEvent['formattedDate'] - now
    days = timeDiff.days

    hours = timeDiff.seconds//3600

    formattedHour = f"0{olympiadEvent['formattedDate'].hour}" if olympiadEvent['formattedDate'].hour < 10 else olympiadEvent['formattedDate'].hour
    formattedMinute = f"0{olympiadEvent['formattedDate'].minute}" if olympiadEvent['formattedDate'].minute < 10 else olympiadEvent['formattedDate'].minute

    dayPos = verticalPos + 4 if sameDay else verticalPos + 4 - movingPos

    graphics.DrawText(canvas, dateFont, 8, dayPos, textColor, f"{olympiadEvent['formattedDate'].month}/{olympiadEvent['formattedDate'].day}")

    if sameDay:
      newTextColor = sameDayColors[movingPos]
      colorArray = newTextColor.split(', ')
      # print(colorArray)
      newTextColor = graphics.Color(int(colorArray[0]), int(colorArray[1]), int(colorArray[2]))
      if (movingPos < 16 and index == 0):
        graphics.DrawText(canvas, timeFont, 4, verticalPos + 20, newTextColor, f"{formattedHour}:{formattedMinute}")
      elif (movingPos >= 16 and index == 1):
        graphics.DrawText(canvas, timeFont, 4, 27, newTextColor, f"{formattedHour}:{formattedMinute}")
    else:
      graphics.DrawText(canvas, timeFont, 4, verticalPos + 20 - movingPos, textColor, f"{formattedHour}:{formattedMinute}")

    graphics.DrawText(canvas, font, 45, verticalPos + 2 - movingPos, textColor, olympiadEvent['event']['name'])
    graphics.DrawText(canvas, font, 45, verticalPos + 12 - movingPos, textColor, olympiadEvent['event']['sport']['name'])
    graphics.DrawText(canvas, font, 45, verticalPos + 22 - movingPos, textColor, f"{days} days, {hours} hours")
    verticalPos += 32


class RunText(SampleBase):
    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        pos = offscreen_canvas.width

        totalEvents = getEvents()

        eventQueue = queue.Queue()

        for event in totalEvents:
          eventQueue.put(event)

        sameDay = False

        event1 = eventQueue.get()
        event2 = eventQueue.get()

        event1['formattedDate'] = parser.isoparse(event1['datetime'])
        event2['formattedDate'] = parser.isoparse(event2['datetime'])

        if (event1['formattedDate'].month == event2['formattedDate'].month and event1['formattedDate'].day == event2['formattedDate'].day):
          sameDay = True

        movingPos = 0

        startingEvent = 0

        totalEventLength = len(totalEvents)

        while True:
            offscreen_canvas.Clear()

            if (movingPos != 0 and movingPos % 32 == 0):
              event1 = {**event2, 'formattedDate': parser.isoparse(event2['datetime'])}

              event2 = eventQueue.get()
              event2['formattedDate'] = parser.isoparse(event2['datetime'])

              if (event1['formattedDate'].month == event2['formattedDate'].month and event1['formattedDate'].day == event2['formattedDate'].day):
                sameDay = True
              else:
                sameDay = False
              
              movingPos = 0

              if eventQueue.qsize() < 3:
                nextEvents = getEvents()

                for event in totalEvents:
                  eventQueue.put(event)


            # print(eventQueue.qsize())

            for x in range(0, 38):
              graphics.DrawLine(offscreen_canvas, x, 0, x, 32, yearBackground)

            renderEvents([event1, event2], offscreen_canvas, font, movingPos, sameDay)

            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

            if (movingPos % 32 == 0):
              # if (movingPos != 0):
              #   startingEvent += 1
              # print(startingEvent)
              time.sleep(6)
              # movingPos = 0
            else:
              time.sleep(0.05)

            movingPos += 1

            # if (movingPos >= totalEventLength * 32):
            #   movingPos = 0



# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
