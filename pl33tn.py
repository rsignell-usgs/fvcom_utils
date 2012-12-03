def pl33tn(x,dt=1,T=33):
    '''% PL33TN: pl33t with variable dt and T
    % xf=PL33TN(x,dt,T) computes low-passed series xf from x
    % using pl33 filter, with optional sample interval dt (hrs)
    % and filter half-amplitude period T (hrs) as input for
    % non-hourly series.
    %
    % INPUT:  x=time series
    %         dt=sample interval [hrs] (Default: dt=1)
    %         T=filter half-amplitude period [hrs] (Default: T=33)
    %
    % OUTPUT: xf=filtered series
    
    % The PL33 filter is described on p. 21, Rosenfeld (1983), WHOI
    % Technical Report 85-35. Filter half amplitude period = 33 hrs.,
    % half power period = 38 hrs. The time series x is folded over
    % and cosine tapered at each end to return a filtered time series
    % xf of the same length. Assumes length of x greater than 67.'''
    cutoff=T/dt
    fq=1/cutoff
    nw=T/dt
