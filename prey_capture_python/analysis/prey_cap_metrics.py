def preycap_metrics(cricket_xy, cricket_p, dist, mouse_spd, az, fr=200, oldmodel=True):
        '''
        function to calculate basic metrics of prey capture behavior
        decent first pass look at if there are differences between conditions

        INPUTS:
            cricket_xy: array; thresholded cricket xy coordinates
            cricket_p: array; cricket likelihoods
            dist: array; distance between mouse and cricket
            mouse_spd: array; mouse speed (not velocity)
            az: array; angle between mouse's head and cricket
            fr: int; framerate of videos, default=200
            oldmodel: boolean; flag to mark cricket likelihood is bad, default=True

        RETURNS:
            captureT: int; time to capture the cricket --indication of start and end need to be changed
            latency: int; time to the first approach
            freqapproach: int; frequency of initiating approaches
            p_intercept: int; probability of intercepting given an approach
            p_capture: int; probability of capturing given intercepting
        '''
        #calculate the time to capture, right now running with a new, higher threshold than other calculations
        #have if/else statement so that if new models in the future fix things but we don't want to re run old data
        newthresh=0.99
        movieT=len(cricket_p)/fr
        if oldmodel==True:
            start2end=np.where(cricket_p>newthresh)[0]
            captureT=(start2end[-1]-start2end[0])/fr
        else:
            captureT=(np.max(np.where(~np.isnan(cricket_xy)))-np.min(np.where(~np.isnan(cricket_xy))))/fr
        if captureT.size==0:
            captureT=movieT

        #calculate latency and frequency of initiating approaches
        approach = []
        paired = list(zip(az,mouse_spd))
        for pair in paired:
            if np.abs(pair[0]) < 30 and pair[1] > 5:
                approach.append(1)
            else:
                approach.append(0)

        approach = signal.medfilt(approach, 101) # 101 is hardcoded half a second based on framerate
        approach = np.asarray(approach)

        approachStarts = np.where(np.diff(approach)>0)
        approachEnds = np.where(np.diff(approach)<0)
        firstApproach = np.min(approachStarts)
        timetoapproach = firstApproach/fr # return this
        freqapproach=np.size(approachStarts) / movieT # return this

        #calculate probability of interception given approach, and probability of capture given interception
        intercept = []
        maybeIntercept = np.take(dist, approachEnds) # uses approachEnds to index dist
        maybeIntercept = maybeIntercept[0] # np.take returns tuple, first value are the ones you one
        maybeIntercept[-1] = 0 # assuming last approach is intercept/capture, makes things werk

        for i in maybeIntercept:
            if i < 5:
                intercept.append(1)
            else:
                intercept.append(0)

        # calculate probability of intercept given approach
        tot_approach = np.size(approachEnds)
        tot_intercept = sum(intercept)
        prob_inter = tot_intercept / tot_approach

        # calculate the probability of capture given contact - 1/number of intercepts
        if tot_intercept>0:
            prob_capture = 1 / tot_intercept
        else:
            print('no capture')

        return captureT, freqapproach, timetoapproach, prob_inter, prob_capture
