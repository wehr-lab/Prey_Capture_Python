##plot success and failure rate using a function

##needs input dfs to be converted in to the correct arrays/ dfs and then segmented and plotted

##input df : all data
##split into mice of interest
##create observations dfs and separate into conditions

def success_failure(df,mouse_list):
    ## read in whole df and segment to what you would want in terms of conditions, removing too long trials etc
    ## for now run this with conds_keep already generated, this would mean it relies on something else, but things are cleaned up

    ##separate out into different mouse specific dfs and make successrate plots
    for i in mouse_list:
        mousedf=df[df['filename'].str.contains('{}'.format(i))]
        
        observations=cdc(mousedf)
        observations=observations[['filename', 'condition', 'laser_value','dist','cricket_spd', 'mouse_spd', 'az', 'captureframe','cricketdrop','interceptframe', 'capduration']]
        observations['absoluteintercept']=observations['cricketdrop']+observations['interceptframe']
        
        cond1=observations.iloc[np.where(observations['condition']=='1')]
        cond1_laser=cond1.iloc[np.where(cond1['laser_value']==1)]
        cond1_nolaser=cond1.iloc[np.where(cond1['laser_value']==0)]

        cond2=observations.iloc[np.where(observations['condition']=='2')]
        cond2_laser=cond2.iloc[np.where(cond2['laser_value']==1)]
        cond2_nolaser=cond2.iloc[np.where(cond2['laser_value']==0)]
        
        
        total_c1l=len(cond1_laser['capduration'])
        failures_c1l=cond1_laser['capduration'].isna().sum()
        successes_c1l=cond1_laser['capduration'].notna().sum()

        total_c1nl=len(cond1_nolaser['capduration'])
        failures_c1nl=cond1_nolaser['capduration'].isna().sum()
        successes_c1nl=cond1_nolaser['capduration'].notna().sum()

        total_c2l=len(cond2_laser['capduration'])
        failures_c2l=cond2_laser['capduration'].isna().sum()
        successes_c2l=cond2_laser['capduration'].notna().sum()

        total_c2nl=len(cond2_nolaser['capduration'])
        failures_c2nl=cond2_nolaser['capduration'].isna().sum()
        successes_c2nl=cond2_nolaser['capduration'].notna().sum()

        successrate_c1l=(successes_c1l/total_c1l)*100
        successrate_c1l=np.asarray(successrate_c1l)
        print(successrate_c1l)
        successrate_c1nl=(successes_c1nl/total_c1nl)*100
        successrate_c1nl=np.asarray(successrate_c1nl)
        print(successrate_c1nl)
        successrate_c2l=(successes_c2l/total_c2l)*100
        successrate_c2l=np.asarray(successrate_c2l)
        print(successrate_c2l)
        successrate_c2nl=(successes_c2nl/total_c2nl)*100
        successrate_c2nl=np.asarray(successrate_c2nl)
        print(successrate_c2nl)
        
        successes=[successrate_c1l,successrate_c1nl,successrate_c2l,successrate_c2nl]
        print(successes
        np.save('/Users/mollyshallow/Desktop/successes_mouse{}.npy'.format(i), successes)
        plt.figure()
        sns.barplot(data=successes)
        plt.title('Success Rate {}'.format(i))
        plt.xticks([0,1,2,3],['Light, Laser','Light, No Laser', 'Dark, Laser', 'Dark, No Laser'])
        sns.despine()



        failurerate_c1l=(failures_c1l/total_c1l)*100
        failurerate_c1l=np.asarray(failurerate_c1l)
        
        failurerate_c1nl=(failures_c1nl/total_c1nl)*100
        failurerate_c1nl=np.asarray(failurerate_c1nl)
        
        failurerate_c2l=(failures_c2l/total_c2l)*100
        failurerate_c2l=np.asarray(failurerate_c2l)
        
        failurerate_c2nl=(failures_c2nl/total_c2nl)*100
        failurerate_c2nl=np.asarray(failurerate_c2nl)
        
        failures=[failurerate_c1l,failurerate_c1nl,failurerate_c2l,failurerate_c2nl]
        np.save('/Users/mollyshallow/Desktop/failures_mouse{}.npy'.format(i), failures)
        plt.figure()
        sns.barplot(data=failures)
        plt.title('Failure Rate {}'.format(i))
        plt.xticks([0,1,2,3],['Light, Laser','Light, No Laser', 'Dark, Laser', 'Dark, No Laser'])
        sns.despine()


        