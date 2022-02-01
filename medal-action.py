#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import requests
import json

from PIL import Image
from io import BytesIO

from easing_functions import *

# For a duration 10 you will get the relevant output from start to end
a = CubicEaseInOut(start=0.008, end = 0.01, duration = 120)
# k = a.ease(4) # 4 is a number between 0 and the duration you specified
# print(k)
# #k is the returned value from start to end (0 to 3)
# k2 = a(4) # the ease object can also be called directly, like a function

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

yearBackground = graphics.Color(43, 149, 185)

def drawBackground(canvas, backgroundWidth):
  for x in range(0, backgroundWidth):
    graphics.DrawLine(canvas, x, 0, x, canvas.height, yearBackground)


class RunText(SampleBase):
    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("../../../fonts/haxor.bdf")
        textColor = graphics.Color(255, 255, 255)
        pos = offscreen_canvas.width
        my_text = "Beijing 2022"

        link = "https://www.heher.io/olympics/api/graphql"
        headers = { 'Content-Type': 'application/json' }
        query = """query {
          randomMedal {
            medalClass
            athlete {
              usedName
            }
            country {
              id
              name
              nocs
            }
            olympiadEvent {
              event {
                name
                sport {
                  name
                }
              }
              olympiad {
                dates {
                  start {
                    value
                  }
                  end {
                    value
                  }
                }
                city {
                  name
                  country {
                    name
                  }
                }
                year
              }
            }
          }
        }"""

        r = requests.post(link, json={'query': query})
        json_data = json.loads(r.text)
        print(json_data)
        # print(json_data['data']['randomMedal']['country']['name'])
        athlete = json_data['data']['randomMedal']['athlete']['usedName']
        countryName = json_data['data']['randomMedal']['country']['nocs'][0]
        olympiad = json_data['data']['randomMedal']['olympiadEvent']['olympiad']['city']['name']
        olympiadYear = str(json_data['data']['randomMedal']['olympiadEvent']['olympiad']['year'])
        eventName = str(json_data['data']['randomMedal']['olympiadEvent']['event']['name'])

        countryId = json_data['data']['randomMedal']['country']['id']
        startDate = json_data['data']['randomMedal']['olympiadEvent']['olympiad']['dates']['start']['value']
        endDate = json_data['data']['randomMedal']['olympiadEvent']['olympiad']['dates']['end']['value']

        # TODO get country flag
        flagQuery = """
          query {
            countryFlagsByTimestamp(
              countryId: "%s",
              olympiadDates: {
                start: {
                  value: "%s",
                  inclusive: true
                },
                end: {
                  value: "%s",
                  inclusive: true
                }
              }
            ) {
              png
            }
          }
        """%(countryId, startDate, endDate)

        # print(flagQuery)

        flagR = requests.post(link, json={'query': flagQuery})
        # print(flagR.text)
        flag_json_data = json.loads(flagR.text)

        flagUrl = flag_json_data['data']['countryFlagsByTimestamp']['png']

        flagImg = requests.get(flagUrl)

        image = Image.open(BytesIO(flagImg.content)).convert('RGB')

        # print(image)
        image.thumbnail((offscreen_canvas.width, 7), Image.ANTIALIAS)

        medalColor = medalColors[str(json_data['data']['randomMedal']['medalClass'])]['background']

        colorArray = medalColor.split(', ')

        circleColor = graphics.Color(int(colorArray[0]), int(colorArray[1]), int(colorArray[2]))

        backgroundWidth = 1
        pos = -80
        direction = 'forward'

        while True:
            offscreen_canvas.Clear()

            # graphics.DrawText(offscreen_canvas, font, 5, 9, textColor, olympiad)
            drawBackground(offscreen_canvas, backgroundWidth)

            if backgroundWidth == offscreen_canvas.width:
              len = graphics.DrawText(offscreen_canvas, font, pos, 13, textColor, olympiad)
              graphics.DrawText(offscreen_canvas, font, pos, 26, textColor, olympiadYear)

              if pos > 80:
                direction = 'backward'
              elif pos < -80:
                direction = 'forward'

              if direction == 'forward':
                pos += 1
              else:
                pos -= 1
            
            # if (pos > offscreen_canvas.width):
            #     pos = -40

              time.sleep(a.ease(pos + 40))

            else:
              backgroundWidth += 1
              time.sleep(0.0001)
            # if pos > 0 and pos < 80:
            #   # if pos < 65:
            #   #   time.sleep(0.005)
            #   # elif pos < 70:
            #   #   time.sleep(0.002)
            #   # else:
            #   #   time.sleep(0.01)
            #   time.sleep(a.ease(pos))
            # else:
            #   time.sleep(0.008)

            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)


# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
