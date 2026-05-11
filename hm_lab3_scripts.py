#  Block 0: IMporting modules


import arcpy  # We need to explicitly import arcpy now that we are 
             # working outside of Arc. 

# This is a key new step -- we want to import the 
#   file that we set up with our functions as a module
# We assume that the lab3_functions.py file is in the 
#   same directory as this scripts.py file, so we can just
#   import it without needing to specify a path. 

import hm_lab3_functions as l3  # use a shortcut to call functions.
# once we've done this, we can access the functions in that
# module using l3.<name of function>()

# NOTE: every time you update the 
#   the lab3_functions file in the course of this
#   lab, you're going to force Python to re-load
#   the file to catch the new functions.  To do that, 
#   you'll use the "importlib.reload()" function. 
#   We'll just hard code that now, since we know
#   we're going to be adapting the functions

import importlib
importlib.reload(l3)

# Now to get to it!

# Block 1:   Copying raster files to your ArcPro project database
# 
# Rationale: 
#    We want to work with raster files this week.  In ArcPro, the
#    goal is to have all operative files within you .gdb for your
#    project.  Thus, we need to move the raster files I've got in the 
#    data directory into the .gdb associated with your Arc project, 
#    and we need to let Arc know that the   

# WHAT TO DO:

#   In this block, you'll just need to 
# 1) switch the paths to your
#       workspace and (if necessary) for the directory of the file
#          I want you to copy.  
# 2) Select this block of code (from "Block 0" above 
# #     down to "end of Block 0" below), then right-click 
#       and run it within VSCode using the 
#       option "Run Python / Run selection/line in Python Terminal"

# set up your workspace. 
# NOTE: SWITCH THIS TO YOUR OWN PROJECT DIRECTORY FOR LAB 3!

arcpy.env.workspace = r"R:\2026\Spring\GEOG562\Students\maranh\Lab3\lab3_arcproject_hm\lab3_arcproject_hm.gdb"  #switch this!!! 

#identify source directory to copy shapefiles from
#  Unless you're working somewhere offcampus, this should remain as is. 
#  You're going to copy files from this directory to 
# your own. 

sourcedir = r"R:\2026\Spring\GEOG562\Data\Lab3_2025"
          #only change if your path name is different

# Now identify the file name of the file to copy.  
#   This is JUST the filename, not the path 

tif_image_filename = "corv_DEM_stateplane.tif"  #NOTE:  we need .tif at the end

# Now call the copy raster function. This is in the 
#   lab3_functions.py file. Note that the function itself
#   returns a tuple with the first item 
#   an indicator variable that tells if something
#   broke inside the function


ok, msg = l3.copy_lab_raster(sourcedir, tif_image_filename)
if ok: 
    print(r"File {msg} was copied")
else:
    print("Problem in copy_lab_raster")
    print(msg)

# End of block 1
# --------------------------------------------------

# Questions for block 1
#  Block 1 Q1:  Where and why did I use the "os" package?
# 
# The os package is used in the functions.py code for joining files and filenames, which we will use in order
# to easily identify filepaths based on specific files we are interested in in a specific file directory. 
# In our scripts.py code, we define what our source directory is, and our tif image filename, and we use the 
# copy_lab_raster function to comine the image filename to the source directory so that we can easily work with it. 


# Block 1 Q2: Describe the format of the arguments returned
#    from the copy_lab_raster function. Why do I 
#    have two variables -- ok and msg -- to catch 
#    the outputs from the function? 
#
# The two variables are meant to communicate the outputs from the fuction, one for the output ok
# and the other msg to give you some sort of message of how that function ran. Basically, if the filepath 
# is correct and the filename exists in the directory you gave it above, the variable "ok" is meant to 
# tell you that this worked, and now we are going to use the variable msg to create a print statement telling you
# that this worked. If there was some sort of error along the way, the ok boolean will be False, and you will
# get a print statement of the exact error that it encountered. 



#------------------------------------------------------------------
#  Block 2:
#   This is YOU!  
#   Please use the same function to copy 
#    two more files into your ARc project
#   database: 
#      corv_area_NLCD_small.tif
#      Landsat_image_corv.tif

#  Your code: 

# First, make a list with the two file names
filename_list = ["corv_area_NLCD_small.tif", "Landsat_image_corv.tif"] # one list containing 2 filenames 

# Then iterate through the list and call the 
#   function
for name in filename_list: # we are going to look at each file name in the list
    ok, msg = l3.copy_lab_raster(sourcedir, name) # for each file in the list, run it through the copy_lab_raster function 
    if ok: # if the file name is in our defined source directory, then copy it into our gdb 
     print(r"File {msg} was copied") # confirm this was copied over 
    else: # if it cannot find the file name in the directory
     print("Problem in copy_lab_raster") # lets us know that the file name is not in the directory
    print(msg)
# Select the text and run it in a Python terminal. 



#------------------------------------------------------------------
#  Block 3:
#   We now have three files:
#   - A DEM
#   - A map of land cover class
#   - A Landsat image with original spectral bands
#  For the rest of the lab, let's figure out how
#    we can understand whether greenness -- as
#    measured by the Landsat image -- is different
#    for different land cover classes on
#    different topographic aspects. 

#  In this block, we'll just create an 
#     aspect image using Arc's tools.  Note 
#     that you'll need to add some code of 
#     your own, and then run just this chunk
#     of code in the Python terminal window. 
# 


# Aspect is a tool in the Spatial Analyst 
#    extension in arc. So, first, we need 
#    to get the spatial analyst 
#   extension 
arcpy.CheckOutExtension("Spatial")
# Now we are going to import Aspect from the arcpy Spatial Analyst toolbox
from arcpy.sa import Aspect 

# Then set up a raster object pointing to the
#  DEM
dem_filename = "corv_DEM_stateplane"
try: 
    dem = arcpy.Raster(dem_filename)
except Exception as e:
    print(e)

# Calculate the aspect image and name 
# appropriately

# YOUR CODE 
# Create the raster object
dem_aspect = Aspect(dem) # use the Aspect arcpy.sa tool to create an aspect raster from the dem 
# Then save it to your database
#  NOTE: -- save this just as an arc raster
#    NOT as a geotiff.  Geotiffs are useful
#    for transferring image data outside of
#    Arc, but for working within our project
#    we can use the default ESRI Raster type. 
dem_aspect.save("Aspect_corv_DEM_stateplane") # save to gdb and rename to whatever you want 

# Look at the image -- does it look like it worked?
# Yep! And there's pretty colors. 

# End of block 3
# --------------------------------------------------

# Questions for block 3
#  Block 3 Q1: Why did we need to explicitly
#     save the aspect to a file?
#
# Your answer:
#
# If we did not save the aspect to a file, then it would not be saved into our Arc gdb, and we would
# not be able to visualize it in our ArcGIS project. 


# Block 3 Q2: How does the resultant image
#    look when loaded onto your map?

# Your answer:
# The image looks as I would expect, it created an aspect map within the same bounds of our DEM raster.
# In the legend of the Aspect raster, we have values which tell us the direction that the slope of that
# area is facing. Upon some qualitative inspection, it seems to have performed correctly! 




#------------------------------------------------------------------
#  Block 4:
#    Let's make a function that makes a 
#    mask of pixels within one aspect range
#    that we specify. 
#   In the lab3_functions.py file, use the 
#   pseudocode clues I leave you to make this 
#   function.  
#   then, use the importlib.reload(l3) to 
#   reload your function and run the function
#   Finally, examine it on the image to make
#    sure that it worked. 


#  Go to the lab3_functions.py and build
#   identify_aspects_by_range(aspect_raster, aspect_min, aspect_max)
#  Then run this code by selecting it
#    and running it in the Python 
# 
importlib.reload(l3)

# if we had to restart our session, we will have lost the 
#    the reference to the aspect image.  So, let's just
#    reload it. 

try: 
    out_aspect_file = "corv_ASP"
    aspect_raster = arcpy.Raster(out_aspect_file)
except Exception as e:
    print(e)


aspect_min = 202
aspect_max = 247

okay, val = l3.identify_aspects_by_range(
    aspect_raster, 
    aspect_min,
    aspect_max
)

if not(okay):
    print("Problem running identify_aspects_by_range")
    print(val)  # show what happened

# set the 
aspect_mask = val
aspect_mask.save("corv_ASP")

# Questions for block 4
#  Block 4 Q1: Load the image and compare this mask
#    with the aspect image from the prior step.  How does it 
#    look? 
#
# Your answer:
# It successfully created a binary classified raster of 0/1, with values of 1 being in our selected
# range of values and those that are 0 are not within our range. 





#------------------------------------------------------------------
#  Block 5: Let's work with our Landsat image to create a
#    greenness indicator -- we'll use the normalized difference
#    vegetation index (NDVI).  The NDVI leverages the contrast
#    in reflectance of plants between the Near Infrared wavelength
#    and the red wavelength.  

# First, load the Landsat image you copied in Block 1
#   as a raster object
importlib.reload(l3)
landsat_file_name = "Landsat_image_corv"
NIR_name = "Band_4"
red_name = "Band_3"

# You will need to add some code to the function below
#  to get it to work. 

okay, val = l3.ndvi(landsat_file_name, NIR_name, red_name)

if not(okay):
    print("Problem running identify_aspects_by_range")
    print(val)  # show what happened

ndvi_raster = val   # assign it here to make it easier to remember the name
ndvi_raster.save("landsat_NDVI")
#------------------------------------------------------------------
#  Block 6: Finally, we'll get the mean value of the NDVI
#   for the aspect mask we created in Block 4. 

#  We'll explore how numpy can make this work easily.  
#  You don't need to make any new code -- just use
#  mine.  But run it to make sure you can get this to
#  work. 

importlib.reload(l3)

# For ease of reading and re-use of the
#  function, we'll re-assign these to 
#  a simpler naming convention
# Note that you'll need to have run 
#  Blocks 4 and 5 to make these raster objects
#  before you can assign them here.
mask_image_object = aspect_mask
continuous_variable_image_object = ndvi_raster

#  Now call a function that uses numpy. 

okay, val = l3.get_mean_masked(continuous_variable_image_object,
                            mask_image_object)

if not(okay):
    print(val)

print(f"The mean value is {val}")


#  Questions for block 6
#  Block 6 Q1: What is the numpy.ma module?
#
#  Your answer:
# The numpy.ma module refers to a masked array which indicates areas that we want to mask out. In our function,
# we used numpy.ma.array to create a masked array where the mask is not equal to 0. With this mask, we can then
# perform calculations, like getting the mean value, on JUST the masked values instead of the whole NDVI raster.
# Source: https://numpy.org/doc/stable/reference/maskedarray.generic.html


#  Block 6 Q2:  When an element of the numpy.ma mask is True, 
#    does that mean the value is valid or invalid?
#    How did I handle this in the masking part of the
#    function? 
#
# Your answer:
# When an element of the numpy.ma mask is True, that means that the value is actually INVALID, which is not
# intuiative. When an element of the mask is False, that is actually an element in the array that is valid and
# unmasked. You handled this in the masking part of the function by creating a masked array where the mask
# is equal to 0, essentially creating a binary masking condition that relates to our 0/1 raster we created. Basically,
# 0 means we want to mask out aka it is "True", and 1 is what we want to keep, aka it's element of the mask is "False"
# Source: https://numpy.org/doc/stable/reference/maskedarray.generic.html

#------------------------------------------------------------------
#  Block 7: But we know that the greenness might be affected
#    by the land cover type.  So, for this block I would 
#    like you to go to the lab3_functions.py and  
#    make a function to select just a landcover code
#    of interest from the NLCD image. 
#    Test it using the land cover class for evergreen
#      forest -- this is NLCD class code 
#   See:  https://www.mrlc.gov/data/legends/national-land-cover-database-class-legend-and-description

# Go to lab3_functions.py and make a function called
#    select_landcover_class(nlcd_image_filename, landcover_code)
#  It should return a raster object like the one from Block 4, except
#    the 1's will indicate pixels of the land cover type of interest. 


importlib.reload(l3)

# if we had to restart our session, we will have lost the 
#    the reference to the aspect image.  So, let's just
#    reload it. 

landcover_file = "corv_area_NLCD_small"
landcover_code_of_interest = 42   #  this is evergreen forest, as per the link above

# Again, you need to build this next function! 
okay, val = l3.select_landcover_class(landcover_file, landcover_code_of_interest)
   
if not(okay):
    print("Problem running select_landcover_class")
    print(val)  # show what happened

# set the landcover_mask to the returned value
landcover_mask = val
landcover_mask.save("landcover_mask_42") # save to GIS gdb 

#------------------------------------------------------------------
#  Block 8: Put it all together:  
#       Let's look at the mean NDVI for forest areas
#       on SW Aspects
#  I'll give you some pseudocode here, and you can do the rest

#  Multiply the landcover_mask by the aspect_mask
#   Because the areas of interest are 1's and the uninteresting
#   areas are 0, multiplying them retains only the 
#   pixels that have 1's in both layers
importlib.reload(l3)
# Your code: 
forest_sw_slope = landcover_mask*aspect_mask

#  Then, take the mask you just made and call the function
#   you did in Block 6 to get the mean value of forests
#   on SW slopes

# Your code
mean_forest_sw_slopes = l3.get_mean_masked(ndvi_raster, forest_sw_slope)
print(f"The mean value is {mean_forest_sw_slopes}")



#  Questions for block 8
#  Block 8 Q1: It was a little odd to have our area of interest
#      in the mask set to 1 when we were using numpy.ma earlier. 
#      Now that we're multiplying them together, describe
#      why I wanted the values of interest to have value 1
#
#  Your answer:
# Now that we are multiplying the two rasters together, it makes sense why we wanted the values of interest to have 
# the value of one. This is because when we multiply the two rasters together (which are binary classified rasters,
# where 1 is the values we want and 0 are those we don't want) this removes the 0 values, and we are left with
# just 1. If we wanted the values of interest to have a value of 0, then we would be left with the values we don't
# want, because this is a raster calculation, so we would be left with the values from both rasters that are 1.


# Block 8 Q2:  In this example, we examined just the mean value
#     of the forest class on a single aspect class.  Describe how 
#     you might look across a range of aspect classes and land 
#     cover classes.

#  Your answer:
# If we wanted to look across a range of aspect classes and land cover classes,  we could iterate over multiple types of land cover
# classes using a for loop. Instead of just assigning one land cover class with a variable, we could make a dictionary of all of the
# different land cover classess, with their numbers and names), and iterate through that list to go through each land cover class and 
# extract the mean values using our function that we created. We then can do the same thing for the aspect clasess, create different
# min and max values to see different aspects like north, east, south, and west, and compute mean NDVI for each. 















