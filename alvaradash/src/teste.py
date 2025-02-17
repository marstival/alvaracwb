import os

# get the current working directory
current_working_directory = os.getcwd()

# print output to the console
print(current_working_directory)


cache_type = os.getenv('CACHE_TYPE','redis')
cache_dir = os.getenv('CACHE_DIR','redis://127.0.0.1:6379')
data_home = os.getenv('HOME_BUCKET', '../../dataset/')
if (data_home.endswith('/') == False):
        data_home = data_home+'/'

print ("ENVIRONMENT %s %s %s"%(cache_type,cache_dir,data_home))


mapbox_access_token=open("./alvaradash/src/.mapbox.token").read()

print(f"mabox:{mapbox_access_token}")