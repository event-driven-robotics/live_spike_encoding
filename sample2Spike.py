from collections import deque
import matplotlib.pyplot as plt
import numpy as np

class Sample2SpikeConverter:

    def __init__(self, threshold, visualize=True):
        self.threshold = threshold
        self.last_val = None
        self.last_time = None
        self.first_time = None
        self.visualize = visualize

    def Sample2Spike(self, sample, timestamp):
        ON_events = []
        OFF_events = []
        if self.last_val is None:
            self.last_val = sample
            self.last_time = timestamp
            self.first_time = timestamp
            return ON_events, OFF_events

        if not hasattr(sample, '__len__'):
            sample = [sample]
        for i, (s, last) in enumerate(zip(sample, self.last_val)):
            if abs(s - last) >= self.threshold:
                # sanity check here? (self.threshold != 0, self.threshold >! 0)
                # On events
                if s - last > 0:
                    number_of_events = int((s - last) / self.threshold)  # calc nbr of events
                    val_at_event = np.arange(1, number_of_events + 1) * self.threshold + last  # calc val at event time
                    steepness = (s - last) / (timestamp - self.last_time)  # calc steepness within two ss
                    ON_events.append(((val_at_event - last) / steepness) + self.last_time)  # place events

                    self.last_val[i] = last + len(ON_events[-1]) * self.threshold  # set new last value

                    OFF_events.append([])
                else:
                    number_of_events = int((last - s) / self.threshold)  # calc nbr of events
                    val_at_event = np.arange(1, number_of_events + 1) * self.threshold + last  # calc val at event time
                    steepness = (last - s) / (timestamp - self.last_time)  # calc steepness within two ss
                    OFF_events.append(((val_at_event - last) / steepness) + self.last_time)  # place events
                    self.last_val[i] = last - len(OFF_events[-1]) * self.threshold  # set new last value
                    ON_events.append([])
            else:
                ON_events.append([])
                OFF_events.append([])
        self.last_time = timestamp

        if self.visualize:
            if not hasattr(self, 'toPlot'):
                self.toPlot = [deque([], maxlen=2000) for x in range(len(sample) * 2)]

                self.fig = plt.figure()
                self.ax = self.fig.add_subplot(111)
                plt.show(block=False)
            for i in range(len(ON_events)):
                for x in ON_events[i]:
                    self.toPlot[i * 2].append(x - self.first_time)
                for x in OFF_events[i]:
                    self.toPlot[i * 2 + 1].append(x - self.first_time)

            self.ax.clear()

            self.ax.eventplot(self.toPlot, colors=['red', 'green'] * len(sample))
            self.ax.set_xlim(self.last_time - self.first_time - 10, self.last_time - self.first_time)

            plt.draw()
            plt.pause(0.001)

        return ON_events, OFF_events
