#!pip install kramersmoyal

import pandas as pd
import numpy as np

from scipy.optimize import curve_fit
from scipy.ndimage.filters import gaussian_filter1d
from kramersmoyal import km


'''For calculations: use angular velocity omega = 2*pi*frequency '''



'''Necessary functions: De-trending, Estimation of KM-Coefficients, Calculation of Power mismatch, Calculation of c_2'''
'''Different models: 1: linear c_1 and epsilon, no c_2 and Delta_P
                     2: linear c_1,c_2 and epsilon,
                     3: cubic c_1(omega), state-dependent c_2 and epsilon
                     4: Calculation of c_2 from bivariate Fokker-Planck equation, linear c_1 and c_2, state-dependent noise   '''


'''Detrending of the time series:'''

def data_filter(data,sigma = 60):
  datafilter = gaussian_filter1d(data,sigma=sigma)
  return datafilter

#datafilter = data_filter(data,sigma = 60)
#data_detrended = data - datafilter

'''Integration of the angular velocity for calcualtion of theta (voltage angle)'''
'''Integrate the omegas by using a sum'''
def integrate_omega(data,time_res=1, start_value = 0):
  theta = np.zeros(data.size)
  theta[start_value] = data[start_value]
  for i in range(start_value + 1,data.size - start_value):
      theta[i] = theta[i-1] + time_res * data[i]
  '''scale values of theta by substracting the average'''
  theta = theta-np.mean(theta)
  return theta


'''1.Calculation the noise amplitude'''

'''here: Use angular velocity (omega) instead of frequency(f)'''
def KM_Coeff_2(data, dim = 1, time_res = 1, bandwidth=0.1, dist = 500, multiplicative_noise = True, start_value=0): 
  if dim == 1:
    powers = [0,1,2]
    bins = np.array([6000])
    '''dim signifies the usage of the univariate or the bivariate Fokker-Planck equation ''' 
    kmc,edges = km(data,powers = powers,bins = bins,bw=bandwidth)
    zero_frequency = np.argmin(edges[0]**2)
    if multiplicative_noise == False:
      epsilon = np.sqrt(2*np.mean(kmc[2,zero_frequency-dist:zero_frequency+dist]))
    elif multiplicative_noise == True:
      peak = zero_frequency-dist+np.argmin(kmc[2,zero_frequency-dist:zero_frequency+dist])
      np.argmin(kmc[2,zero_frequency-dist:zero_frequency+dist]**2),zero_frequency,zero_frequency-dist+np.argmin(kmc[2,zero_frequency-dist:zero_frequency+dist])
      d_2 = curve_fit(lambda t , a  : a*(t-0)**2 + kmc[2,zero_frequency],edges[ 0 ][zero_frequency-dist:zero_frequency+dist],kmc[2,peak-dist:peak+dist])[0]
      diff_zero=kmc[2,peak]
      d_0=diff_zero
      epsilon = (d_2,d_0)
    return epsilon
      
  elif dim == 2:
    '''Use dist as 2-dimensional array in this case: 1st entry: voltage angle, 2nd entry: angular velocity'''
    powers = np.array([[0,0],[1,0],[0,1],[1,1],[2,0],[0,2],[2,2]])
    bins = np.array([300,300])
    data = np.array([integrate_omega(data,time_res=time_res,start_value = start_value),data]) #use theta as integrated omega
    kmc, edges = km(data.transpose(),powers = powers,bins = bins,bw=bandwidth)
    '''Attention: use here as data the detrended data (doriginal data minus filter'''
    zero_angle = np.argmin(edges[0]**2)
    zero_frequency = np.argmin(edges[1]**2)
    if multiplicative_noise == False:
      epsilon = np.sqrt(2*np.mean(kmc[5,zero_angle-dist[0]:zero_angle+dist[0],zero_frequency-dist[1]:zero_frequency+dist[1]]/time_res))  
      #epsilon = np.sqrt(2*np.mean(kmc[5,zero_angle:zero_angle,zero_frequency:zero_frequency]/time_res)) #only use mean
      
    elif multiplicative_noise == True:
      def f_0_2(x, a, b):
          return a*(x[1])**2 + b   #!!!
   

      side_x = edges[0][zero_angle-dist[0]:zero_angle+dist[0]]
      side_y = edges[1][zero_frequency-dist[1]:zero_frequency+dist[1]]
      X1, X2 = np.meshgrid(side_x, side_y)
      size = X1.shape
      x1_1d = X1.reshape((1, np.prod(size)))
      x2_1d = X2.reshape((1, np.prod(size)))
      xdata = np.vstack((x1_1d, x2_1d))
      z=(np.array([[kmc[5,zero_angle-dist[0]+i,zero_frequency-dist[1]+j]/time_res for i in range(2*dist[0])] for j in range(2*dist[1])]))
      Z = z.reshape(( np.prod(size)))
      ydata = Z
      popt, pcov = curve_fit(f_0_2, xdata, ydata)
      epsilon = popt
  return epsilon
     
'''2. Estimation of the drift (primary control)'''
def KM_Coeff_1(data,dim= 1,time_res = 1,bandwidth=0.1,dist = 500, order = 1, start_value=0):
    if dim == 1:
        powers = [0,1,2]
        bins = np.array([6000])
        kmc,edges = km(data,powers = powers,bins = bins,bw=bandwidth)
        '''dimension signifies the usage of the univariate or the bivariate Fokker-Planck equation''' 
        
        zero_frequency = np.argmin(edges[0]**2)
        '''old model: constant c_1'''
        c = np.polyfit(edges[ 0 ][zero_frequency-dist:zero_frequency+dist] , kmc[1][ zero_frequency - dist: zero_frequency + dist] ,order)
        c = c[::2]

        #c = [c[-1-2*i:-1] for i in range((c.size)//2)]
        '''Not sure yet if this is right'''
        #c_1 = curve_fit(lambda t,a,b: a - b*t , xdata = space[ 0 ][mid_point-D_lin:mid_point+D_lin] ,ydata = kmc[1][ mid_point - D_lin: mid_point + D_lin] , p0 = ( 0.0002 ,0.0005 ) ,maxfev=10000)[ 0 ][ 1 ]
        #p_3,p_2,p_1,p_0=np.polyfit(space[ 0 ][mid_point-D:mid_point+D] , kmc[1][ mid_point - D: mid_point + D] ,3)
    elif dim == 2:
        powers = np.array([[0,0],[1,0],[0,1],[1,1],[2,0],[0,2],[2,2]])
        bins = np.array([300,300])
        data = np.array([integrate_omega(data,time_res=time_res,start_value = start_value),data]) #use theta as integrated omega
        #theta = integrate_omega(data,time_res=time_res,start_value = start_value)
        #data = np.array([data,integrate_omega(data,time_res=time_res,start_value = start_value)]) #use theta as integrated omega
        kmc,edges = km(data.transpose(),powers = powers,bins = bins,bw=bandwidth)
        def f_0_1(x,p_1,c_2):
          return p_1*x[1] + c_2 *x[0]  
        '''Define start and end'''
        #s1,e1,s2,e2 = 120,-120,5,-5
        zero_angle = np.argmin(edges[0]**2)
        zero_frequency = np.argmin(edges[1]**2)
        side_x = edges[0][zero_angle-dist[0]:zero_angle+dist[0]]
        side_y = edges[1][zero_frequency-dist[1]:zero_frequency+dist[1]]
        X1, X2 = np.meshgrid(side_x, side_y)
        size = X1.shape
        x1_1d = X1.reshape((1, np.prod(size)))
        x2_1d = X2.reshape((1, np.prod(size)))
        xdata = np.vstack((x1_1d, x2_1d))
        z=(np.array([[kmc[2,zero_angle-dist[0]+i,zero_frequency-dist[1]+j]/time_res for i in range(2*dist[0])] for j in range(2*dist[1])]))
        Z = z.reshape(( np.prod(size)))
        ydata = Z
        popt, pcov = curve_fit(f_0_1, xdata, ydata)
        c = popt
    return c




'''Calculate daily profiles:'''   #take averge value at every full second for one day (3600*24 data points)
def daily_profile(data,time_res = 1):
    '''time_res represents the time resolution of the data'''
    daily_profile=np.zeros(int(24*3600))
    day_number = data.size//(int(24*3600/time_res))
    for i in range(daily_profile.size):
      daily_profile[i] = np.mean([data[int(int(i/time_res)+int(3600*24/time_res)*j)//(int(1/time_res))]for j in range(day_number)])
    return daily_profile
         
def daily_profile_pointwise(i,data,time_res=1,delta_t = 1):
    day = daily_profile(data=data,time_res = time_res)
    d = day[(i%(int(3600*24/delta_t)))//(int(1/delta_t))]
    return d
         

'''3. Calculation of the power mismatch'''
'''Calculate the power mismatch as the derivative of the trajectories around times of power dispatches:'''

'''Delta_P: Find ROCOF in (5-minutes-interval around full hours (resp. power injections)!)'''

def power_mismatch(data,avg_for_each_hour = True, time_res = 1,dispatch=1,start_minute=0,end_minute=7,length_seconds_of_interval=5):
    '''Attention: Use the data that you want to use for the power mismatch (for ex. for Ireland we take 5-second filtered data because of hourly and 60-seconds-junks)'''
    data_range = data.size//(3600*24)
    s,e,l = 0-start_minute,end_minute-0,length_seconds_of_interval
    end = 2*length_seconds_of_interval -1
    steps = end +1
    #m = np.zeros((24*change,data_range))
    argm = np.zeros((24*dispatch,data_range))
    Delta_P_slopes = np.zeros((24*dispatch,data_range))
    for i in range(24*dispatch):
        for j in range(1,data_range):
            #argm[i,j] = np.argmax(np.abs([curve_fit( lambda t , a , b : a + b*t , np.linspace( 0 , end , steps ) , data[ i*int(3600/dispatch)+ 3600 * 24 * j  -s*60 + k*l -l : i*int(3600/dispatch)+ 3600 * 24 * j -s*60 + k*l + l] , p0 = ( 0.0 , 0.0 ) ,maxfev=10000)[ 0 ][ 1 ] for k in range(1,int((s+e)*60/l))]))
            argm[i,j] = np.argmax(np.abs([curve_fit ( lambda t , a , b : a + b*t , np.linspace( 0 , end , steps ) , data[ i*int(3600/dispatch)+ 3600 * 24 * j  -s*60 + k*l -l : i*int(3600/dispatch)+ 3600 * 24 * j -s*60 + k*l + l] , p0 = ( 0.0 , 0.0 ) ,maxfev=10000)[ 0 ][ 1 ] for k in range(1,int((s+e)*60/l))]))
            Delta_P_slopes[i,j] =  (curve_fit( lambda t , a , b : a + b*t , np.linspace( 0 , end , steps ) , data[ i*int(3600/dispatch)+ 3600 * 24 * j  -s*60 + int(argm[i,j]+1)*l -l : i*int(3600/dispatch)+ 3600 * 24 * j -s*60 +  int(argm[i,j]+1)*l + l] , p0 = ( 0.0 , 0.0 ) ,maxfev=10000)[ 0 ][ 1 ] )
    sign = np.zeros(int(dispatch*24))
    day = daily_profile(data,time_res = time_res)
    daily_prof_25 = np.zeros(25*3600*time_res)   #add 1st hour of daily profile to the daily prile to calculate the average sign of the slope at each power dispatch
    daily_prof_25[0:24*3600*time_res] = day
    daily_prof_25[24*3600*time_res:] = day[0:1*3600*time_res]
    for i in range(sign.size):
        if np.mean(np.diff(daily_prof_25[(i+1)*(int(4/dispatch))*900 -int(s*60) : (i+1)*(int(4/dispatch))*900 + int(e*60)])) > 0:
            sign[(i+1)%(24*dispatch)]=1
        else:
            sign[(i+1)%(24*dispatch)]=-1
    P_arr = np.zeros(24*dispatch)
    for i in range(24*dispatch):
        P_arr[i] = np.mean(np.abs(Delta_P_slopes[i,:]))
    if avg_for_each_hour == True:
        Delta_P = sign*P_arr
    else:
        Delta_P = np.mean(np.abs(Delta_P_slopes[i,:]))
    return Delta_P
  
  
  

         
'''Calculation of c_2 from the exponential decay after changes of th epower dispatches at full hours'''
'''4. STATE-DEPENDENT Secondary control c_2 /( EXPERIMENTATION)!!!'''
def exp_decay(data,time_res=1,size = 899):
    #gap   =0
    size  = 899
    steps = size+1
    window = 3600
    data_range = data.size // window
    c_2_decays = np.zeros(data_range)

    for j in range(1,data_range):
        # if the frequency trajectory increases positively
        if np.sum(( np.diff( data[ 3600 *( j ) : 3600 * ( j ) +10]) ) ) > 0 :
            c_2_decays[j] = curve_fit(lambda t , a , b :#,  c : 
            a*np.exp(-b*t ) ,#* (1-np.exp(-c * t+2*b* t ) ) ,
            np.linspace( 0 , size ,steps ) , data[ 3600 * ( j ) : 3600 * ( j ) + steps] ,
            p0 = ( 0.08 , 0.00455 
                 ),#, 0.035  ) , 
            maxfev=10000)[ 0 ][ 1 ]
        elif np.sum(( np.diff( data[ 3600 *( j ) : 3600 * ( j ) +10]) ) ) <= 0 :
            c_2_decays[j] = curve_fit(lambda t , a , b :#,,  c : 
            (-a)*np.exp(-b*t ) ,#* (1-np.exp(-c * t+2*b* t ) ) ,
            np.linspace( 0 , size ,steps ) , data[ 3600 * ( j ) : 3600 * ( j ) + steps] ,
            p0 = ( 0.08 , 0.00455 
                 ),#, 0.035  ) , 
            maxfev=10000)[ 0 ][ 1 ]
    '''Cut off statistical outliers by cutting off 1/5 of the highest values of the power decay'''
    temp_c_2_decays = c_2_decays[np.argsort(c_2_decays)][: - c_2_decays.size // 5]
    return np.mean(temp_c_2_decays )
    # c_2_linear = np.mean(temp_c_2_decays ) * (c_1)
    #omega_arr = np.linspace(-0.5,0.5,101)
    #c_2_arr = np.mean(temp_c_2_decays)*(3*(-p_3)*omega_arr**2 - p_1)




'''Euler-Maruyama'''

def Euler_Maruyama(data,c_1,c_2_decay,Delta_P,epsilon,time_res = 1,dispatch = 1,delta_t=0.1,t_final=5,model=3,factor_daily_profile=0,prim_control_lim = 0.15*2*np.pi,prim_weight = 1):
    t_steps = int(t_final*3600*24/delta_t)
    time = np.linspace(0.0, t_final, t_steps)
  
    omega = np.zeros([time.size]) 
    theta = np.zeros([time.size])
    # Give some small random initial conditions
    theta[0]=np.random.normal(size = 1) / 10    
    omega[0]=np.random.normal(size = 1) / 10
    # Generate a Wiener process with a scale of np.sqrt(delta_t)
    dW = np.random.normal(loc = 0, scale = np.sqrt(delta_t), size = [time.size,1])
    
    if model == 1:
        for i in range(1,time.size):
            theta[i] = theta[i-1] + delta_t * omega[i-1]
            omega[i] = omega[i-1] + delta_t * c_1*omega[i-1]   + 1*epsilon *dW[i]
    elif model == 2:
        P = np.ones(time.size)
        sign_P = np.zeros(time.size)
        for i in range(1,time.size):
            if dispatch != 0:
                if i % (12*3600/delta_t)  < 6*3600/delta_t:    #greater or equal is important here!!!
                    sign_P[i]=1
                else:
                    sign_P[i]=-1
                if i % (60*60/delta_t)  < (4/dispatch)*15*60/delta_t:
                    P[i] = 1  #*q1_mean_half #0.5
                else:
                    P[i] = 1/3     #heuristic choice as the change of the power dispatch at the begin of an hour is normally higher than at other times
            
            theta[i] = theta[i-1] + delta_t * omega[i-1]
            omega[i] = omega[i-1] + delta_t * (   c_1 *omega[i-1] + c_2_decay *c_1  * theta[i-1] + 1*Delta_P*P[i]*sign_P[i] )  + epsilon*dW[i]
        
    elif model == 3:
        P_slow = np.ones(time.size)
        Delta_P_model_3 = np.zeros(time.size)
        c_2 = np.zeros(time.size)
        c_1_weight = np.ones(time.size)
        epsilon_model_3 = np.zeros(time.size)
        for i in range(1,time.size):
            if dispatch != 0:
                if i%(900*1/delta_t*int(4/dispatch)) <60:   #TAKE 60 seconds!!!
                    P_slow[i] = i%(900/delta_t*int(4/dispatch))/60
                if np.abs(omega[i-1]) > prim_control_lim:
                    c_1_weight[i] = prim_weight            
                #Delta_P_model_3[i] = 1* P_slow[i] * Delta_P[int((i//(int(4/dispatch)*900/delta_t))%(dispatch*24))]  +(1-P_slow[i])*  Delta_P[int(((i//(int(4/dispatch)*900/delta_t))-1)%(dispatch*24))]    
                Delta_P_model_3[i] = Delta_P[int((i//(int(4/dispatch)*900/delta_t))%(dispatch*24))]  
            c_2[i] = c_2_decay*(3*(c_1[0])*(omega[i-1] )**2 + c_1[1])
            epsilon_model_3[i] = np.sqrt(2*(epsilon[0]*omega[i-1]**2 + epsilon[1])) 
            theta[i] = theta[i-1] + delta_t * omega[i-1]
            omega[i] = omega[i-1] + delta_t * ( c_1_weight[i]* ( c_1[0] * (omega[i-1])**3 + c_1[1]* omega[i-1] ) + c_2[i]* theta[i-1] + 1*Delta_P_model_3[i] )  + 1*epsilon_model_3[i]*dW[i]
    elif model == 4:
         c_2 = c_2_decay
         epsilon_model_4 = np.zeros(time.size)
         c_1_weight = np.ones(time.size)
         trend_daily = np.zeros(time.size)
         day = daily_profile(data=data_filter(data),time_res = time_res)
         
         for i in range(1,time.size):
             if np.abs(omega[i-1]) > prim_control_lim:
                 c_1_weight[i] = prim_weight
             epsilon_model_4[i] = np.sqrt(2*(epsilon[0]*omega[i-1]**2 + epsilon[1])) 
             trend_daily[i] = day[(i%(int(3600*24/delta_t)))//(int(1/delta_t))]
             
             theta[i] = theta[i-1] + delta_t * omega[i-1]
             omega[i] = omega[i-1] + delta_t * (c_1_weight[i] * c_1 *omega[i-1]  + c_2 * theta[i-1] )  + epsilon_model_4[i]*dW[i]       
         omega = omega + factor_daily_profile * trend_daily#s+ factor_daily_profile * daily_profile_pointwise(i, data, time_res=time_res, delta_t = delta_t) #describe day_filter
    return omega
# =============================================================================
#     def c_1_fun(x):
#       if model == 4:
#         c_1_fun = c_1[0]*x
#       else:
#         if c_1.size ==2:
#           c_1_fun = c_1[0] * x**3 + c_1[1]*x
#         elif c_1.size ==1:
#           c_1_fun = c_1*x
#       return c_1_fun
#     
#     def c_2_fun(x):
#       if model == 1:
#         c_2_fun = 0
#       elif model == 4:
#         c_2_fun = c_2
#       else:
#         if c_1.size ==2:
#           c_2_fun = exp_decay(data,time_res,size = 899)*(3*(-c_1[0])*x**2 - c_1[1])
#           '''Attention: time_res in c_2 is original time resolution'''
#         elif c_1.size ==1:
#           c_2_fun = exp_decay(data,time_res,size = 899)*c_1
#           '''Attention: time_res in c_2 is original time resolution'''
#       return c_2_fun
#     
#     def epsilon_fun(x):
#         if epsilon.size ==2:
#             epsilon_fun = np.sqrt(2*(epsilon[0]*x**2 + epsilon[1]))
#         elif epsilon.size == 1:
#             epsilon_fun = epsilon
#         return epsilon_fun
#       
#            
#     def Delta_P_fun(i):
#       if model == 1:
#         Delta_P_fun = 0
#       elif model == 2:
#         P = np.ones(time.size)
#         sign_P = np.zeros(time.size)
#         if i % (12*3600/delta_t)  < 6*3600/delta_t:    #greater or equal is important here!!!
#           sign_P[i]=1
#         else:
#           sign_P[i]=-1
#         if i % (60*60/delta_t)  < (4/dispatch)*15*60/delta_t:
#           P[i] = 1  #*q1_mean_half #0.5
#         else:
#           P[i] = 1/3     #heuristic choice as the change of the power dispatch at the begin of an hour is normally higher than at other times
#         Delta_P_fun = P[i]*sign_P[i]*Delta_P
#       elif model == 3:
#           if i%(900*1/delta_t*int(4/dispatch)) <60:   #TAKE 60 seconds!!!
#               P_slow = i%(900/delta_t*int(4/dispatch))/60
#           else:
#               P_slow = 1
#               Delta_P_fun[i] = 1* P_slow * Delta_P[(i//(int(4/dispatch)*900/delta_t))%(dispatch*24)]  +(1-P_slow[i])*  Delta_P[((i//(int(4/dispatch)*900/delta_t))-1)%(dispatch*24)]
#       elif model == 4:
#           Delta_P_fun = Delta_P
#       return Delta_P_fun
#           
#     for i in range(1,time.size):
#       theta[i] = theta[i-1] + delta_t * omega[i-1]
#       omega[i] = omega[i-1] + delta_t * (  c_1_weight * c_1_fun(omega[i-1]) + 1 * c_2_fun(omega[i-1]) * theta[i-1] + 1*Delta_P_fun(i) )  + 1*epsilon_fun(omega[i-1])*dW[i]
#     if model == 4:
#       omega = omega + factor_daily_profile * daily_profile_pointwise(i, data, time_res=time_res, delta_t = delta_t) #describe day_filter
#     else:
#       omega = omega
#     return omega
# =============================================================================
             
'''Define Increments'''
def Increments(data,time_res = 1,step = 1):
  Inc = np.zeros(int(data.size*time_res/(step))-1)
  for i in range(Inc.size):
    Inc[i] = data[int((i+1)*step/time_res)] - data[int((i)*step/time_res)]
  return Inc
    
'''Define autocorrelation function'''
def autocor(data,count=6*90,steps=10,time_res = 1):
  data = pd.Series(data)
  AUTO_data= np.array([data.autocorr(lag=int(i*steps/time_res)) for i in range(count)])
  return AUTO_data
