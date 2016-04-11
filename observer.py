class Observer():
    _observers = []

    def __init__(self):
        self._observers.append(self)
        self._observables = {}

    def observe(self, event_name, callback):
        self._observables[event_name] = callback


class Event():
    
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.fire()

    def fire(self):
        for observer in Observer._observers:
            if self.name in observer._observables:
                observer._observables[self.name](self.data)