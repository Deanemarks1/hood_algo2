


master_dir = True






#System Setup: Mar 20 - V1 
###############################################################################################


"""if __name__ == "__main__": finally makes sense. 
#this will run if you are running from your local env, 
but allows you to not run inmaster so you can instantly run to test the function

#so need to make everything a function, 
then can import all of the files with os.list in the master directory


"""


import os


def crawl_dir_to_find_then_run_file(filename):
    d = os.getcwd()
    f = None

    while not f:
        for r, _, files in os.walk(d):
            if filename in files:
                f = os.path.join(r, filename)
                break
        if f or os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)

    if not f:
        raise FileNotFoundError(f"{filename} not found")

    exec(open(f).read(), globals())


# 🔥 MAIN ENTRY POINT

try:
    master_dir
except NameError:
    master_dir = False



#Child Dir System Setup -- Use for Testing
if not master_dir:


    # engines you want to inject here
    crawl_dir_to_find_then_run_file("mysqlconnector.py")
    crawl_dir_to_find_then_run_file("deane_text_functions.py")
    crawl_dir_to_find_then_run_file("selenium_setup.py")

    
    # Define DB you are working on
    run_sql("use new_algo_db")



if master_dir == True: 
    # engines you want to inject here
    crawl_dir_to_find_then_run_file("mysqlconnector.py")
    crawl_dir_to_find_then_run_file("deane_text_functions.py")
    crawl_dir_to_find_then_run_file("selenium_setup.py")

    
    # Define DB you are working on
    run_sql("use new_algo_db")


    
###############################################################################################






import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


