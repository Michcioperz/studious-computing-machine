#!/usr/bin/env python3
# encoding: utf-8
import random, re, gi, pyowm, tweepy, arrow, configparser, os
gi.require_version('Gtk','3.0')
from gi.repository import Gtk, Gdk, Pango
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "moetan.ini"))
HANDLERS = []

if "openweathermap" in config:
    owm = pyowm.OWM(config["openweathermap"]["api_key"])
    def weather(location):
        forecast = owm.three_hours_forecast(location).get_forecast().get(0)
        print(forecast.to_JSON())
        return """Here's the weather %s: %s, about %s Celsius degrees.""" % (arrow.Arrow.fromtimestamp(forecast.get_reference_time("unix")).humanize(), forecast.get_detailed_status(), forecast.get_temperature("celsius").get("temp", "no idea lol"))
    HANDLERS.append((r"^weather( (for|in|at))? (?P<location>.+)$", weather))

if "twitter" in config:
    twttrauth = tweepy.OAuthHandler(config["twitter"]["consumer_key"], config["twitter"]["consumer_secret"])
    twttrauth.set_access_token(config["twitter"]["access_token_key"], config["twitter"]["access_token_secret"])
    twttr = tweepy.API(twttrauth)
    def tweet(text):
        print(twttr.update_status(text))
        return "I sent it!"
    HANDLERS.append((r"^tweet (?P<text>.+)$", tweet))

HANDLERS.append((r"^shrug", lambda: "¯\_(ツ)_/¯"))

HANDLERS = [(re.compile(x[0]),x[1]) for x in HANDLERS]

class Question(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MOE-tan")
        self.set_default_size(500,100)
        self.connect("delete_event", Gtk.main_quit)
        self.header = Gtk.HeaderBar()
        self.header.set_has_subtitle(True)
        self.header.set_show_close_button(True)
        self.header.set_title("MOE-tan")
        self.header.modify_font(Pango.font_description_from_string("Lato 14"))
        self.header.set_subtitle("What do you need, senpai? "+random.choice(["(´• ω •`)","(*^‿^*)","(-‿‿-)"]))
        self.set_titlebar(self.header)
        self.entry = Gtk.Entry()
        self.entry.modify_font(Pango.font_description_from_string("Lato 27"))
        self.entry.connect("key-release-event", self.on_key_release)
        self.add(self.entry)
        self.entry.grab_focus()
        self.show_all()
    def on_key_release(self, widget, ev, data=None):
        if ev.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()
        if ev.keyval == Gdk.KEY_Return:
            self.entry.set_editable(False)
            self.header.set_subtitle("Let me see... "+random.choice(["(￣～￣;)","(￣.￣;)","(￣_￣)・・・","(-_-;)・・・","(ʃ⌣́,⌣́ƪ)","(ー_ーゞ","໒( ⊡ _ ⊡ )७"]))
            for h in HANDLERS:
                m = h[0].match(self.entry.get_text())
                if m:
                    dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "I've found the answer, senpai!!!")
                    dialog.format_secondary_text(h[1](**m.groupdict()))
                    dialog.modify_font(Pango.font_description_from_string("Lato 27"))
                    dialog.run()
                    dialog.destroy()
                    Gtk.main_quit()
                    return
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "I didn't understand you, senpai!!!")
            dialog.modify_font(Pango.font_description_from_string("Lato 27"))
            dialog.run()
            dialog.destroy()
            self.entry.set_editable(True)

if __name__ == "__main__":
    moe = Question()
    Gtk.main()
