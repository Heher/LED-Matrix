#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import requests
import json

from PIL import Image
from io import BytesIO

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


class RunText(SampleBase):
    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("../../../fonts/matelight.bdf")
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

        yearBackground = graphics.Color(43, 149, 185)

        while True:
            offscreen_canvas.Clear()

            # graphics.DrawText(offscreen_canvas, font, 5, 9, textColor, olympiad)
            for x in range(0, 28):
              graphics.DrawLine(offscreen_canvas, x, 0, x, 11, yearBackground)

            graphics.DrawText(offscreen_canvas, font, 2, 9, textColor, olympiadYear)
            # graphics.DrawCircle(offscreen_canvas, 57, 7, 5, green)
            # graphics.DrawCircle(offscreen_canvas, 57, 7, 4, green)
            graphics.DrawText(offscreen_canvas, font, 71, 10, textColor, eventName)
            graphics.DrawCircle(offscreen_canvas, 63, 15, 3, circleColor)
            graphics.DrawCircle(offscreen_canvas, 63, 15, 2, circleColor)
            graphics.DrawCircle(offscreen_canvas, 63, 15, 1, circleColor)
            offscreen_canvas.SetPixel(62, 14, int(colorArray[0]), int(colorArray[1]), int(colorArray[2]))
            offscreen_canvas.SetPixel(64, 14, int(colorArray[0]), int(colorArray[1]), int(colorArray[2]))
            offscreen_canvas.SetPixel(63, 15, int(colorArray[0]), int(colorArray[1]), int(colorArray[2]))
            offscreen_canvas.SetPixel(62, 16, int(colorArray[0]), int(colorArray[1]), int(colorArray[2]))
            offscreen_canvas.SetPixel(64, 16, int(colorArray[0]), int(colorArray[1]), int(colorArray[2]))
            graphics.DrawText(offscreen_canvas, font, 71, 18, textColor, athlete)
            graphics.DrawText(offscreen_canvas, font, 74 + image.width, 26, textColor, countryName)
            offscreen_canvas.SetImage(image, 71, 19)

            # pos -= 1
            # if (pos + len < 0):
            #     pos = offscreen_canvas.width

            # time.sleep(0.05)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)


# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
