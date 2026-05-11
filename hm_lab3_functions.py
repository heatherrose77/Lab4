
#We put in an arcpy import here just in case we are 
# using this in a situation where it hasn't been imported, 
#  but for our lab it should already be imported from the script
#  level. 

import arcpy
import os
import numpy as np



# A function to copy a .tif from a source directory
#   into the current ArcPy workspace
#  NOTE that this will copy into that ArcPy workspace, 
#   where ever that is!  You need to set that first


def copy_lab_raster(source_dir, tif_image_filename):
    
    # We'll start a habit here of keeping track of whether things
    #  work in our code using a variable that indicates whether
    #  things are "okay". We return this variable along with whatever
    #  else is necessary from our function out to the caller

    okay = True   # assume things are okay to start with 

    # Now we're going to be working with files and filenames -- a
    #    classic case where there can be errors. So we'll wrap this
    #    all inside a try/except block

    try:
        #  Then use the OS package to put them together
        input_filename = os.path.join(source_dir, tif_image_filename)
        #  when we move this raster into our Arc database, it will be
        #  transmogrified into an Arc format raster, not a tif, with
        #  no file extension.  So, we need to lop off the end of the file
        #  name to remove the .tif
        # use the "replace" function to swap out .tif with an empty string
        output_filename = tif_image_filename.replace(".tif", "")
       
        
        # use arc's command to copy from the source into our current 
        # workspace.  But first we make sure that the file does not
        #  already exist
        
        if not arcpy.Exists(output_filename):
            arcpy.management.CopyRaster(input_filename, output_filename)
            return okay, output_filename  # this returns a tuple 
                            # with the status at [0] and the filename second
 
 
        # If the file exists, we return with a different set of messages
        else:
            okay = False
            error_msg = f"file {output_filename} already exists."
            return okay, error_msg
 
    # And if there was some more general problem, report back on it
    except Exception as e:
        okay = False
        error_msg = e
        return okay, error_msg
    

#----------------------------------------------------
# For Block 4 of the script, I ask you to make
#  a function called "identify_aspects_by_range"

#  Here's the pseudocode to help you make it
# You can uncomment any parts of this you want
#  to use, or you can add your own code as you
# prefer. 

from arcpy.sa import * 
# define the function
def identify_aspects_by_range(aspect_raster, aspect_min, aspect_max): # create a new function, with input variables
#
# set up an indicator variable to catch if things go wrong

    okay = True

# Confirm the aspect_raster exists, and if not, return to the sender
#    with a message. 

# Your code
    if not arcpy.Exists(aspect_raster): # if the raster aspect_raster does not exist
        okay = False # then things are wrong, and return the following statement
        return okay, "Aspect raster does not exist."


# first confirm that the aspect ranges have the correct bounds -
#  i.e. that neither of them is below 0 or greater than 360 degrees. 
#  If they are not valid, return with a complaint

# Your code
    if (aspect_min < 0 or aspect_min > 360  # first see if the minimum values are in the range
        aspect_max < 0 or aspect_max > 360): # then check to see if the maximum values are within the range
        okay = False # if the return is false, and aspect raster is not within this range
        return okay, "Aspect values are not between 0 and 360." # return this error message if values are not in the range 
    
# Within a try/except block, use arcpy commands
#  to create an image that has value 0 for 
#  areas that are not in the desired range, and
#  that have value 1 for areas that are in the desired
#  range
 # IMportantly:  we need to handle the special case where the range 
#   of aspects wraps around the 0/360 disjunction
#  Case 1:   aspect_min < aspect_max -- the "normal case".  This would
#         be for example for the case where the min is 180 and max is 270
#        or the min is 45 and the max is 135, etc. 

# Your code:
    try:
        # check to see if the aspect range does not fall in our boundary
        if aspect_min < aspect_max:
            # Case 1: Normal Case
            # Create a mask where aspect values fall within our range 
            # 0 is those that are not in the range and 1 are those that are 
            aspect_mask = Con(
                (aspect_raster >= aspect_min) & (aspect_raster <= aspect_max),
                1, 0
            )
        else:
            # Case 2: wrap around case
            # If values are not in the range, use the OR condition to capture these above the
            # min or below the max 
            aspect_mask = Con(
                (aspect_raster >= aspect_min) | (aspect_raster <= aspect_max),
                1, 0
            )

        return okay, aspect_mask # make sure that this mask sompleted successfully 
    # If anything went wrong during this code, this will let us know the issue 
    except Exception as e:
        okay = False
        return okay, e
    

#  Case 2:   aspect_min > aspect_max -- where we want to 
#                    include due north in the range.   This would be for
#              the case where the min might be 350 and the max 10. 
#

# Your code
# written above in try/except block 


# return the pointer to the raster object
#   we have created.  Do not save it here --
#     just pass it back, along with the "okay", as a tuple
#     something like okay, val

# Your code
# written above

# End of block 4 functions
#######


#------------------------------------------------------
# Block 5 functions
# Here we are interested in calculating the NDVI
# of a landsat image. I'll give you pseudocode and parts of
#  code, and you can do the rest


def ndvi(image_name, band4_name, band3_name):
    # set up an indicator about whether things work for later
     
    okay = True

    #embed everything in a try/except block

    try: 
        if arcpy.Exists(image_name):  # check to see if the image_name is there!
            
            # load just the NIR band into a raster object
            nir = arcpy.Raster(image_name+"\\"+band4_name)

            # load just the red band into a raster object
            
            # Your code:
            
            
            # My code:
            red = arcpy.Raster(image_name+"\\"+band3_name)
            # end my code


            # In the case of the image I provided you
            #  the NIR band is "Band_4" and the
            #  red band is "Band_3"
        else:   # in this case, the image does not exist
            okay = False
            returnval = r"{image_name} does not appear to exist in the workspace: {arcpy.env.workspace}"
            return okay, returnval
        
    except Exception as e:  # this is some problem reading the image
        okay = False
        returnval = e
        return okay, returnval
    

    # Now we have the two bands.  Use your AI bot or your own
    #   exploration of band math with Arc rasters to 
    #   calculate (NIR-Red)/(NIR+red), which is the formula for
    #   NDVI.  Then return the pointer to the NDVI object
    #   you have calculated. Make sure to embed this in a try/except block

    # Your code: 
    # Calculate NDVI 
    try:
        ndvi = (nir-red)/(nir+red) #NDVI calculation 
        return okay, ndvi # worked successfully!
    except Exception as e: # if anything went wrong, return the error
        okay = False
        return okay, e


#------------------------------------------
# Block 6 function
#  Here, we want to calculate the
#  mean value of pixels in one image (the NDVI)
#  only for areas indicated with the value
#  1 in a mask image (where we have selected
#    for certain aspects)

# here, we assume that both arguments are 
#   arcpy objects, and that the mask
#   image has areas of interest with value
#    1 and areas to ignore with value 0
# I'm going to just give you this whole function
#   so you can see how this works. 

def get_mean_masked(continuous_raster, mask_raster):
    
    # set up our standard indicator
    okay = True

    try: 
        # turn both of the arc rasters into numpy arrays
        val_array = arcpy.RasterToNumPyArray(continuous_raster)
        mask_array = arcpy.RasterToNumPyArray(mask_raster)

        # Use Numpy's numpy.ma module
        #  Note that we have set up our 
        #  mask image to have 1's indicate where
        #  we are interested in summarizing. 
        #  But the numpy.ma module indicates
        #  areas to mask out with True, which is
        #  is equivalent to 1.  So, we have to be explicit
        #  about how we want this. 
        # Create masked array where mask == 0
        val_array_masked = np.ma.array(val_array, mask=(mask_array == 0))

        #  Now we can simply call the "mean()" function
        #  on the masked array to get only the values
        #  of interest

        mean_val = val_array_masked.mean()

        returnval = mean_val
        return okay, returnval
    

    except Exception as e:
        okay = False
        returnval = e
        return okay, returnval
    


# Block 7 function:  selecting by land cover
#  Here, we ingest the filename for an NLCD land cover image
#    and the code of the landcover that we want
#    and return a mask where 1's indicate pixels in the
#    landcover of interest, and 0's indicate those that are
#    not. 
# I'll give you pseudocode here to build from

def select_landcover_class(nlcd_image_filename, landcover_code):

#     # Your code

#     # set up an indicator variable to catch if things go wrong
    okay = True

#     # Confirm the raster er exists, and if not, return to the sender
#     #    with a message. 
    if not arcpy.Exists(nlcd_image_filename):
        okay = False
        return okay, "NLCD image does not exist."
#     # Make a mask but keep it embedded in a try/except block
#     #  use the Con conditional to identify places where the 
#     #   raster == the landcover code. 
#     #  Return the raster object

    try:
        nlcd = arcpy.Raster(nlcd_image_filename) # create a raster from the given filename
        nlcd_mask = Con(nlcd == landcover_code, 1, 0) # perform mask where raster is equal to the land cover type

        return okay, nlcd_mask # success! Mask made

    except Exception as e: # any issues? this code will give you the error:
        okay = False
        return okay, e
    











    

   
