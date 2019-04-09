import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation

RANGE = (-200, 0)

# Create figure for plotting
fig = plt.figure("Real time bluetooth strength readings")
ax = fig.add_subplot(1, 1, 1)
xs = []
ya = []
yb = []
# This function is called periodically from FuncAnimation
def animate(i, xs, ya, yb):
    
    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    ya.append(np.random.uniform(RANGE[0], RANGE[1]))
    yb.append(np.random.uniform(RANGE[0], RANGE[1]))

    # Limit x and y lists to 20 items
    xs = xs[-20:]
    ya = ya[-20:]
    yb = yb[-20:]
    

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ya, color='g', label='Device 1')
    ax.plot(xs, yb, color='r', label='Device 2')
    ax.legend()
    
    # Format plot
    plt.xticks([])
    plt.subplots_adjust(bottom=0.30)
    plt.title('Simulation RSSI over time')
    plt.ylabel('DBMS')

# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ya, yb), interval=1000)
plt.show()
