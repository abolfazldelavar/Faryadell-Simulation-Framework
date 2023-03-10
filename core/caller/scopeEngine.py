
## // --------------------------------------------------------------
#    ***FARYADELL SIMULATION FRAMEWORK***
#    Creator:   Abolfazl Delavar
#    Web:       http://abolfazldelavar.com
## // --------------------------------------------------------------

# Import initial classes
from core.lib.pyRequirment import *
from core.lib.coreLib  import plotToolLib
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

class scope():
    ## --------------------------------------------------------------------------------
    # Author: A. Delavar, http://abolfazldelavar.com
    #  --------------------------------------------------------------------------
    # This class is a kind of scope that can save your signals which can be
    # used for after running progress.
    # INSTRUCTION:
    # 1) Use the below code in 'initialization.py', into the 'vectors', to set initial options
    #    signals.x = scope(signals.tLine, The number of signals, initial=1)
    # 2) Use the below piece of code in 'simulation.py' to save each step
    #    signals.x.getdata(Input signal at step k, noise=0)
    # ---------------------------------------------------------------------------------
    
    def __init__(self, tLine, nSignals, **kwargs):
        # Time line, The number of signals, initial signal value

        initialcondition = np.array([0])
        # Extracting the arbitraty value of properties
        for key, val in kwargs.items():
            # The initial condition
            if key == 'initial': initialcondition = np.array(val)

        self.timeLine    = np.reshape(tLine, [1, np.size(tLine)])   # Time line vector
        self.timeLine    = np.array(self.timeLine)
        self.sampleTime  = np.mean(self.timeLine[0, 1:-1] - self.timeLine[0, 0:-2])
        self.numSignals  = nSignals                                 # The number of signals
        self.currentStep = 0                                        # The current step of simulation
        self.n           = np.size(self.timeLine)                   # The number of time steps
        self.signals     = np.zeros([self.numSignals, self.n])      # Signal matrix

        # If the initial input does not exist, set it zero
        # Else, put the initial condition in the state matrix
        iniSh = initialcondition.shape
        if sum(iniSh) == self.numSignals or sum(iniSh) == self.numSignals + 1:
            # If the imported initial value is not a column vector, do this:
            initialcondition = np.reshape(initialcondition, [np.size(initialcondition), 1])
            self.signals += 1
            self.signals  = initialcondition*self.signals
        elif sum(iniSh) != 1 and sum(iniSh) != 2:
            if iniSh == (self.numSignals, self.n):
                self.signals = initialcondition
            else:
                raise ValueError("The dimensional of initial value that inserted is wrong. Check it please.")

        
    # The 'getdata' function can receive value and save it.
    # To use this function, refer to the top INSTRUCTION part
    def getdata(self, insData, **kwargs):
        # Inserted data, additive noise Variance
        
        addNoiseVar = 0
        # Extracting the arbitraty value of properties
        for key, val in kwargs.items():
            # The noise variance
            if key == 'noise': addNoiseVar = val
        # If the noise signals do not exist, consider them zero.
        noiseSig = np.random.normal(0, addNoiseVar, [self.numSignals, 1])
        
        # Update internal signals which later can be used for plotting
        # and programming for other parts of the code
        self.signals[:, self.currentStep] = insData.flatten() + noiseSig.flatten()
        self.currentStep += 1
        
    # This function can make a jump in the step number variable
    # If no arguments are available, jump 1 step
    def goahead(self, i = 1):
        self.currentStep += i
        
    # Reset Block by changing the current step to zero
    def reset(self):
        self.currentStep = 0

    # The below function is used to plot the internal signals
    def show(self, params, **kwargs):

        # Get the input arguments
        select = -1
        derive = [[0]]
        notime = [[0]]
        save   = 0
        xlabel = '$x$'
        ylabel = '$y$'
        zlabel = '$z$'
        title  = ''
        legend = -1
        lineWidth = 0.5
        grid   = 0
        ncol   = 3

        for key, val in kwargs.items():
            # 'select' can choose signals arbitrary
            if key == 'select': select = val
            # 'derive' is used to get derivatives of the signals
            if key == 'derive': derive = val
            # 'notime' is related to plot while time is hidden
            if key == 'notime': notime = val
            # 'save' can export the figure into files
            if key == 'save': save = val
            # 'xlabel' is the figure xlabel
            if key == 'xlabel': xlabel = val
            # 'ylabel' is the figure ylabel
            if key == 'ylabel': ylabel = val
            # 'zlabel' is the figure zlabel
            if key == 'zlabel': zlabel = val
            # 'title' is the figure title
            if key == 'title': title = val
            # 'legend' can control the figure legend
            if key == 'legend': legend = val
            # 'linewidth' is the line width of the pen
            if key == 'lineWidth': lineWidth = val
            # 'grid' refers to the grid net of the figure
            if key == 'grid': grid  = val
            # The number of legend columns
            if key == 'legCol': ncol = val

        
        # Initialize
        plib = plotToolLib()

        # Extracting the arbitraty values of properties
        if select == -1: select = range(0, self.numSignals)
        notime = np.array(notime)
        if notime.shape == (len(notime),):
            notime = np.reshape(notime, [1, len(notime)])
        derive = np.array(derive)

        if np.size(notime, 1) == 1:
            # Plot time axis signals

            # Starting to create and plot
            h  = plt.figure(tight_layout=True)
            ax = h.subplots()

            # Pre-processing on data
            SIGNAL = self.signals[select,0:-2]
            # If all derivatives are requested, make them here
            if derive.any():
                if derive.all():
                    SIGNAL = SIGNAL - np.roll(SIGNAL, +1, axis=1)
                else:
                    indi = (derive>0).flatten()
                    SIGNAL = SIGNAL - np.diag(indi).dot(np.roll(SIGNAL, +1, axis=1))
                SIGNAL[:,0]  = SIGNAL[:,1]
                SIGNAL[:,-1] = SIGNAL[:,-2]
            
            # General time line plot
            for i in range(0, SIGNAL.shape[0]):
                makeLabel = '[' + str(select[i]) + ']'
                ax.plot(self.timeLine[0, 0:-2].flatten(), SIGNAL[i,:], lw = lineWidth, label = makeLabel)
            ax.set_xlabel(r'Time (s)')
            if xlabel != '$x$': plt.xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_xlim([self.timeLine[0, 0], self.timeLine[0, -1]])
        
        elif np.size(notime, 1) == 2:
            # 2D signal line plot

            # Starting to create and plot
            h  = plt.figure(tight_layout=True)
            ax = h.subplots()

            for i in range(0, notime.shape[0]):
                # Pre-processing on data
                SIGNAL = self.signals[notime[i,:], 0:-2]
                xlabel2 = xlabel
                ylabel2 = ylabel
                # Affect derivatives
                if derive.any():
                    # If all derivatives are requested, make them here
                    if derive.all():
                        SIGNAL = SIGNAL - np.roll(SIGNAL, +1, axis=1)
                        xlabel2 = 'd$x/$d$t$'
                        ylabel2 = 'd$y/$d$t$'
                    else:
                        indi = (derive>0).flatten()
                        SIGNAL = SIGNAL - np.diag(indi).dot(np.roll(SIGNAL, +1, axis=1))
                        if derive[0] != 0: xlabel2 = 'd$x/$d$t$'
                        if derive[1] != 0: ylabel2 = 'd$y/$d$t$'
                    SIGNAL[:,0]  = SIGNAL[:,1]
                    SIGNAL[:,-1] = SIGNAL[:,-2]
                # Plotting
                makeLabel = '[' + str(notime[i, 0]) + ', ' + str(notime[i, 1]) + ']'
                ax.plot(SIGNAL[0,:], SIGNAL[1,:], lw = lineWidth, label =  makeLabel)
            # The end of the for loop
            ax.set_xlabel(xlabel2)
            ax.set_ylabel(ylabel2)

            # Legend options
            # 'frameon' can hide the background and the border of the legend
            # 'fontsize' changes the font. The value must be True or False
            # 'bbox_to_anchor' can change the position of the legend arbitrary
            # 'ncol' indicated the number of columns that components are arranged.
            # 'mode' implies the mode of legend whcih can be 'expand' or ?
            ax.legend(loc='upper right', frameon=False, fontsize=14, bbox_to_anchor=(0,1,1,0), ncol=ncol)

        elif np.size(notime, 1) == 3:
            # 3D signal line plot

            # Starting to create and plot
            h  = plt.figure(tight_layout=True)
            # This order can prepare the are for 3D curve plotting
            ax = h.add_subplot(projection='3d')

            for i in range(0, notime.shape[0]):
                # Pre-processing on data
                SIGNAL = self.signals[notime[i,:], 0:-2]
                xlabel2 = xlabel
                ylabel2 = ylabel
                zlabel2 = zlabel
                # If all derivatives are requested, make them here
                if derive.any():
                    if derive.all():
                        SIGNAL = SIGNAL - np.roll(SIGNAL, +1, axis=1)
                        xlabel2 = 'd$x/$d$t$'
                        ylabel2 = 'd$y/$d$t$'
                        zlabel2 = 'd$z/$d$t$'
                    else:
                        indi = (derive>0).flatten()
                        SIGNAL = SIGNAL - np.diag(indi).dot(np.roll(SIGNAL, +1, axis=1))
                        if derive[0] != 0: xlabel2 = 'd$x/$d$t$'
                        if derive[1] != 0: ylabel2 = 'd$y/$d$t$'
                        if derive[2] != 0: zlabel2 = 'd$z/$d$t$'
                    SIGNAL[:,0]  = SIGNAL[:,1]
                    SIGNAL[:,-1] = SIGNAL[:,-2]
                # Plotting
                makeLabel = '[' + str(notime[i, 0]) + ', ' + str(notime[i, 1]) + ', ' + str(notime[i, 2]) + ']'
                ax.plot(SIGNAL[0, 1:-2], SIGNAL[1, 1:-2], SIGNAL[2, 1:-2], lw = lineWidth, label = makeLabel)
            # The end of the for loop
            ax.set_xlabel(xlabel2)
            ax.set_ylabel(ylabel2)
            ax.set_zlabel(zlabel2)

            # Legend options
            # 'frameon' can hide the background and the border of the legend
            # 'fontsize' changes the font. The value must be True or False
            # 'bbox_to_anchor' can change the position of the legend arbitrary
            # 'ncol' indicated the number of columns that components are arranged.
            # 'mode' implies the mode of legend whcih can be 'expand' or ?
            ax.legend(loc='upper right', frameon=False, fontsize=14, bbox_to_anchor=(0,1,1,0), ncol=ncol, mode='expand')
        # The end of the if and elif
        
        if xlabel != '$x$': ax.set_xlabel(xlabel)
        if ylabel != '$y$': ax.set_ylabel(ylabel)
        if zlabel != '$z$': ax.set_zlabel(zlabel)
        if title  != '':    ax.set_title(title)
        
        # Set the legend if it is required
        if legend == -1:
            pass
        elif legend == 0:
            ax.legend().remove()
        elif legend == 1:
            ax.legend(loc='best', frameon=False, fontsize=14, bbox_to_anchor=(0,1,1,0), ncol=ncol)
        else:
            ax.legend(legend, loc='upper right', frameon=False, fontsize=14, bbox_to_anchor=(0,1,1,0), ncol=ncol)
        
        # Draw a grid net
        if grid != 0: ax.grid(True)

        # Make it pretty + saving engine
        plib.isi(params, h, save=save)
    # The end of the function

    # The below function is used to plot a raster plot
    def raster(self, params, **kwargs):
        # To set your opyions you must use the below codes:
        #  'select'     -> 1:3
        #  'ylabel'     -> 'Voltage (v)'
        #  'colorLimit' -> [0, 1]
        #  'gradient'   -> Gradient variable that made by gradient func.
        
        # Get the input arguments
        select = np.arange(0, self.numSignals)
        derive = False
        save   = False
        xlabel = 'Time (s)'
        ylabel = 'Signal index'
        title  = False
        colorBar = True
        colorlimit = False
        hwRatio = 0.68
        interp = 'none'
        rasterize = True
        switcher1 = 1
        switcher2 = 1
        colorlimit = [0, 0]
        gradient = mpl.cm.RdGy

        for key, val in kwargs.items():
            # 'select' can choose signals arbitrary
            if key == 'select': select = val
            # 'derive' is used to get derivatives of the signals
            if key == 'derive': derive = val
            # 'save' can export the figure into files
            if key == 'save': save = val
            # 'xlabel' is the figure xlabel
            if key == 'xlabel': xlabel = val
            # 'ylabel' is the figure ylabel
            if key == 'ylabel': ylabel = val
            # 'title' is the figure title
            if key == 'title': title = val
            # 'colorBar' can enable the color bar
            if key == 'colorBar': colorBar = val
            # The color limt
            if key == 'colorLimit':
                colorlimit = val
                switcher1 = 0
            if key == 'barTicks':
                barTicks = val
                switcher2 = 0
            # The gradient
            if key == 'cmap': gradient = val
            # hwRatio denotes the height to width
            if key == 'hwRatio': hwRatio = val
            # Interpolation of the illustration
            if key == 'interpolation': interp = val
            # Rasterization
            if key == 'rasterized': rasterize = val

        # Get data
        PANELL = self.signals[select,0:-2]

        # If the derivatives are requested, make them here
        if derive == True:
            PANELL = PANELL - np.roll(PANELL, +1, axis=1)
            PANELL[:,0]  = PANELL[:,1]
            PANELL[:,-1] = PANELL[:,-2]

        ## Plot part
        # Initialize
        plib = plotToolLib()
        
        #  Starting to create and plot
        h  = plt.figure(tight_layout=True)
        ax = h.subplots()

        # Plot the images
        imWidth  = self.timeLine[0,-1]
        imHeight = hwRatio*imWidth
        vmin     = PANELL.min()*switcher1 + (1-switcher1)*colorlimit[0]
        vmax     = PANELL.max()*switcher1 + (1-switcher1)*colorlimit[1]

        im = ax.imshow(PANELL,
                interpolation = interp, # nearest, bilinear, bicubic
                cmap   = gradient,      # RdYlGn
                origin = 'lower',       # This can reverse the Y axis
                extent = [0, imWidth, 0, imHeight],
                vmax   = vmax,          # The maximum value
                vmin   = vmin,
                rasterized = rasterize) # The mimimum value

        axins = inset_axes(
            ax,
            width="3%",  # width: 5% of parent_bbox width
            height="100%",  # height: 50%
            loc="lower left",
            bbox_to_anchor=(1.02, 0., 1, 1),
            bbox_transform=ax.transAxes,
            borderpad=0,
        )
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if title != False: ax.set_title(title)

        # Change the appearance to LaTeX form
        plib.isi(params, h)
        # Color Bar
        if switcher2 == 1:
            barTICK = [vmin, vmax]
        elif switcher2 == 0:
            barTICK = barTicks
        if colorBar == True:
            h.colorbar(im, cax=axins, ticks=barTICK)
        # Modify the Y ticks
        ax.set_yticks([0, imHeight], [str(select[0]), str(select[-1])])
        # Save the figure
        plib.figureSaveCore(params, save=save, fig=h, dpi=500)
# The end of the class

