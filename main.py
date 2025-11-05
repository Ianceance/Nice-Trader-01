
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
import os

# keep window size reasonable for desktop testing (ignored on mobile)
Window.size = (360, 640)

Builder.load_file('nice.kv')

class WelcomeScreen(Screen):
    def check_pin(self):
        app = App.get_running_app()
        if app.has_pin():
            if app.remember_pin and app.unlocked:
                app.root.current = 'menu'
            else:
                app.root.current = 'pin_unlock'
        else:
            app.root.current = 'pin_setup'

class PinSetupScreen(Screen):
    def set_pin(self, pin, confirm):
        app = App.get_running_app()
        if not pin or len(pin) < 4 or len(pin) > 6:
            return
        if pin != confirm:
            return
        app.store.put('security', pin=pin, remember=True)
        app.pin = pin
        app.remember_pin = True
        app.unlocked = True
        app.root.current = 'menu'

class PinUnlockScreen(Screen):
    def unlock(self, entered):
        app = App.get_running_app()
        stored = None
        try:
            stored = app.store.get('security')['pin']
        except Exception:
            stored = None
        if stored and entered == stored:
            app.unlocked = True
            app.pin = stored
            app.root.current = 'menu'
        else:
            self.ids.unlock_msg.text = 'Wrong PIN. Try again.'

class MenuScreen(Screen):
    pass

class DashboardScreen(Screen):
    pass

class TradingNotesScreen(Screen):
    pass

class MyTradesScreen(Screen):
    pass

class SettingsScreen(Screen):
    def get_remember_default(self):
        app = App.get_running_app()
        try:
            return app.store.get('security').get('remember', True)
        except Exception:
            return True
    def change_pin(self, newpin):
        app = App.get_running_app()
        if not newpin or len(newpin) < 4 or len(newpin) > 6:
            return
        app.store.put('security', pin=newpin, remember=app.remember_pin)
        app.pin = newpin
    def save_remember(self, val):
        app = App.get_running_app()
        app.remember_pin = val
        try:
            data = app.store.get('security')
            app.store.put('security', pin=data.get('pin',''), remember=val)
        except Exception:
            pass

class NiceTraderApp(App):
    def build(self):
        ud = self.user_data_dir
        if not os.path.exists(ud):
            os.makedirs(ud)
        self.store = JsonStore(os.path.join(ud, 'storage.json'))
        self.pin = None
        self.remember_pin = True
        self.unlocked = False
        try:
            sec = self.store.get('security')
            self.pin = sec.get('pin')
            self.remember_pin = sec.get('remember', True)
        except Exception:
            pass
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(PinSetupScreen(name='pin_setup'))
        sm.add_widget(PinUnlockScreen(name='pin_unlock'))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(TradingNotesScreen(name='trading_notes'))
        sm.add_widget(MyTradesScreen(name='my_trades'))
        sm.add_widget(SettingsScreen(name='settings'))
        if self.pin and self.remember_pin:
            self.unlocked = True
            sm.current = 'menu'
        else:
            sm.current = 'welcome'
        return sm

    def has_pin(self):
        return bool(self.pin)

if __name__ == '__main__':
    NiceTraderApp().run()
