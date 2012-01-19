import random

class UserColor(object):

    def __init__(self):
        self.user_color = {}

    def get(self, user_id):
        return self.user_color.setdefault(user_id, self._get_color())

    def _get_color(self):

        darkest, lightest = 0, 150

        while True:
            i =random.randint(0, 0xFFFFFF)
            color = '%06x' % i
            y, s = self._convert_bw(color)

            if darkest < y < lightest and s > 60:
                break

        return color

    def _convert_bw(self, color):
        rgb_str = [ color[:2], color[2:4], color[4:] ]
        rgb = [int(c, 16) for c in rgb_str]

        y = rgb[0] * 0.29891 + rgb[1] * 0.58661 + rgb[2] * 0.11448

        sorted_rgb = sorted(rgb)
        s = sorted_rgb[-1] - sorted_rgb[0]

        return y, s
