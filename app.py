from utils.plotter import Plotter

if __name__ == '__main__':
    rpi_plot = Plotter('pihole-FTL.db')
    rpi_plot.deploy(debug=True)
