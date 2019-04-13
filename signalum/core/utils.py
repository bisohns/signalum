import datetime as dt
import matplotlib.animation as animation
import matplotlib.pyplot as plt


def db2dbm(quality):
    """
    Converts the Radio (Received) Signal Strength Indicator (in db) to a dBm
    value.  Please see http://stackoverflow.com/a/15798024/1013960
    """
    dbm = int((quality / 2) - 100)
    return min(max(dbm, -100), -50)


class RealTimePlot(object):
    """
    Creates a matplotlib handler for plotting animated graphs
    This graph handler plots values on the y axis against live updated events
    """
    def __init__(self, func, func_args, plt_style="seaborn", fig=None):
        """
            Args:
                func: (function) function to be call by animation
                The function must accept arguments as follows func(i, ax, *args) where ax is the matplotlib axis being passed to it
                func_args: (tuple) variables to pass to the function
                plt_style: (str): string of available style to use for plot, check by using `print(matplotlib.pyplot.style.available)`
                fig: (matplotlib.pyplot.figure) optional figure to add if you want to plot on an exiting figure, defaults to None
        """
        self.animate_this = func
        self.animate_this_args = func_args
        self.plt = plt
        self.plt_style = plt_style
        if not fig:
            self.fig = plt.figure("Signalum Graph")
        else:
            self.fig = fig
        # change background style
        self.plt.style.use(self.plt_style)                
        self.ax = self.fig.add_subplot(1, 1, 1)        

    def animate(self, interval=100):
        """
        run the animate_this function

        Args:
            interval: (int) number of milliseconds to call the function providing the real time data, defaults to 100
        Run Procedure:
            - Passes the necessary args to the animate function
            - `ax` arg is used to pass x and y variables to be plotted
            - `plt` arg is used to set axis labels, limits, e.t.c
        """
        ani = animation.FuncAnimation(self.fig, self.animate_this, fargs=(self.ax, self.plt, *self.animate_this_args), interval=interval)
        self.plt.show()
