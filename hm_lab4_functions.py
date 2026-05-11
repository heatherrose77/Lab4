import arcpy
import pandas as pd
import math
import matplotlib.pyplot as plt
arcpy.CheckOutExtension("Spatial") 
from arcpy.sa import Raster 


class SmartRaster(arcpy.Raster):

    def __init__(self, raster_path):
        super().__init__(raster_path)
        self.raster_path = raster_path
        self.metadata = self._extract_metadata()

    def _extract_metadata(self):
        desc = arcpy.Describe(self.raster_path)
        extent = desc.extent
        
        bounds = [[extent.XMin, extent.YMax],
                  [extent.XMax, extent.YMin]]

        y_dim = self.height
        x_dim = self.width
        n_bands = self.bandCount
        pixelType = self.pixelType

        return {
            "bounds":bounds, 
            "x_dim": x_dim, 
            "y_dim": y_dim, 
            "n_bands": n_bands, 
            "pixelType": pixelType
        }

    # add a method to the SmartRaster class to calcuate NDVI
    def calculate_ndvi(self, band4_index=4, band3_index=3):
        """Calculate NDVI using the NIR (Band 4) and Red (Band 3) bands."""

        okay = True

        try:
            if arcpy.Exists(self.raster_path):

                # Build proper band paths using ArcGIS naming convention
                nir_path = f"{self.raster_path}\\Band_{band4_index}"
                red_path = f"{self.raster_path}\\Band_{band3_index}"

                # Load bands as raster objects
                nir = arcpy.Raster(nir_path)
                red = arcpy.Raster(red_path)

            else:
                okay = False
                returnval = f"{self.raster_path} does not appear to exist in the workspace: {arcpy.env.workspace}"
                return okay, returnval

        except Exception as e:
            okay = False
            return okay, e

        # NDVI calculation
        try:
            ndvi = (nir - red) / (nir + red)
            return okay, ndvi

        except Exception as e:
            okay = False
            return okay, e

       

# Potential smart vector layer

# class SmartVectorLayer:
#     def __init__(self, feature_class_path):
#         """Initialize with a path to a vector feature class"""
#         self.feature_class = feature_class_path
        
#         # Check if it exists
#         if not arcpy.Exists(self.feature_class):
#             raise FileNotFoundError(f"{self.feature_class} does not exist.")
#     def summarize_field(self, field):
#         # set up a tracking variable to track if things work
#         okay = True

#         #check if the field is in the legit list
#         try: 
#             existing_fields = [f.name for f in arcpy.ListFields(self.feature_class)]
#             if field not in existing_fields:
#                 okay = False
#                 print(f"The field {field} is not in list of possible fields")
#                 return False, None
#         except Exception as e:
#             print(f"Problem checking the fields: {e}")

#         # now go through and get the mean value
#         try: 
#             with arcpy.da.SearchCursor(self.feature_class, [field]) as cursor:
#                 vals = [row[0] for row in cursor if row[0] is not None and not math.isnan(row[0])]
#             mean = sum(vals)/len(vals)
#             return okay, mean
#         except Exception as e:
#             print(f"Problem calculating mean: {e}")
#             okay = False
#             return okay, None

    
class SmartVectorLayer:
    def __init__(self, feature_class_path):
        """Initialize with a path to a vector feature class"""
        self.feature_class = feature_class_path

        # set up zone field (needed for zonal stats join)
        self.zone_field = arcpy.Describe(self.feature_class).OIDFieldName

        # Check if it exists
        if not arcpy.Exists(self.feature_class):
            raise FileNotFoundError(f"{self.feature_class} does not exist.")


    def summarize_field(self, field):
        # set up a tracking variable to track if things work
        okay = True

        #check if the field is in the legit list
        try: 
            existing_fields = [f.name for f in arcpy.ListFields(self.feature_class)]
            if field not in existing_fields:
                okay = False
                print(f"The field {field} is not in list of possible fields")
                return False, None
        except Exception as e:
            print(f"Problem checking the fields: {e}")
            return False, None

        # now go through and get the mean value
        try: 
            with arcpy.da.SearchCursor(self.feature_class, [field]) as cursor:
                vals = [
                    row[0] for row in cursor
                    if row[0] is not None and not math.isnan(row[0])
                ]
            mean = sum(vals) / len(vals)
            return okay, mean
        except Exception as e:
            print(f"Problem calculating mean: {e}")
            return False, None


    def zonal_stats_to_field(self, raster_path, statistic_type="MEAN", output_field="ZonalStat"):
        """
        For each feature in the vector layer, calculates the zonal statistic from the raster
        and writes it to a new field.

        Parameters:
        - raster_path: path to the raster
        - statistic_type: type of statistic ("MEAN", "SUM", etc.)
        - output_field: name of the field to create to store results
        """

        # set up a tracking variable to track if things work
        okay = True

        # Add a field to store the zonal stats result.
        #  If the field already exists, however, return to the user
        #  to let them know that it exists. 

        #Your code
        try:
            field_names = [f.name for f in arcpy.ListFields(self.feature_class)]

            if output_field in field_names:
                return False, f"Field '{output_field}' already exists in the layer."

            arcpy.management.AddField(self.feature_class, output_field, "DOUBLE")

        except Exception as e:
            return False, f"Field creation failed: {e}"


        # Create a temporary table to hold zonal statistics
        temp_table = r"in_memory\temp_zonal_stats"

        if arcpy.Exists(temp_table):
            arcpy.management.Delete(temp_table)

        # Use an arcpy.sa command to calculate the 
        #   zonal stats.  Embed in a try/except block

        #  Your code
        try:
            from arcpy.sa import ZonalStatisticsAsTable

            ZonalStatisticsAsTable(
                in_zone_data=self.feature_class,
                zone_field=self.zone_field,
                in_value_raster=raster_path,
                out_table=temp_table,
                ignore_nodata="DATA",
                statistics_type=statistic_type
            )

        except Exception as e:
            return False, f"Zonal statistics failed: {e}"


        # Now join the results back and update the field
        zonal_results = {}

        # First, read through the Zonal stats table we just created. 

        try:
            table_count = 0

            # NOTE:  the "OBJECTID_1" is needed because when Arc builds 
            #   the temporary zonal stats file, it adds its own new OBJECTID
            #   that ascends in incremental order. But the unique ID from the
            #   original attribute table is what we want to focus on -- its 
            #    name gets adjusted with an _1 at the end so the original value is kept
            #    but to keep it unique from the OBJECTID that Arc builds for the
            #    zonal table.  Kind of annoying. 

            with arcpy.da.SearchCursor(temp_table, ["OBJECTID_1", statistic_type]) as cursor:
                for row in cursor:
                    zonal_results[row[0]] = row[1]
                    table_count += 1

            print(f"Processed {table_count} zonal stats")

        except Exception as e:
            print(f"Problem reading the zonal results table: {e}")
            return False


        #Then Update the feature class with the zonal_results
        #  Use the Object ID to find the right 
        #    zonal stats number from the zonal_results dictionary
        #    as you go through the attribute table of the feature class
        print("Joining zonal stats back to Object ID")

        # Your code
        try:
            oid_field = arcpy.Describe(self.feature_class).OIDFieldName

            with arcpy.da.UpdateCursor(self.feature_class, [oid_field, output_field]) as cursor:
                for row in cursor:
                    oid = row[0]

                    if oid in zonal_results:
                        row[1] = zonal_results[oid]
                        cursor.updateRow(row)

        except Exception as e:
            print(f"Problem updating feature class: {e}")
            return False, e


        # Clean up
        arcpy.management.Delete(temp_table)

        print(f"Zonal stats '{statistic_type}' added to field '{output_field}'.")
        return okay


    def save_as(self, output_path):
        """Save the current vector layer to a new feature class"""
        arcpy.management.CopyFeatures(self.feature_class, output_path)
        print(f"Saved to {output_path}")

    # Take our vector object and turn it into a pandas dataframe

    def extract_to_pandas_df(self, fields=None):
        # set up tracker variable
        okay = True

        #First, get the list of fields to extract if the user did 
        #  not pass them

        if fields is None: # If the user did not pass anything
            # List all field names (excluding geometry)
            fields = [f.name for f in arcpy.ListFields(self.feature_class) if f.type not in ('Geometry', 'OID')]
        else: 
            #check to make sure that the fields given are actually in the table, 
            #   and make sure to exclue the geometry and oid.

            true_fields = [f.name for f in arcpy.ListFields(self.feature_class) if f.type not in ('Geometry', 'OID')]

            #accumulate the ones that do not match
            disallowed = [user_f for user_f in fields if user_f not in true_fields]

            # if the list is not empty, let the user know
            if len(disallowed) != 0:
                print("Fields given by user are not valid for this table")
                print(disallowed)
                okay = False
                return okay, None
        
        # Step 2: Create a search cursor and extract rows
        #    to a "rows" list variable.  This is a very short 
        #    command -- should be old hat by now!  

        # vvvvvvvvvvvvvvv
        # Your code: 
        rows = [] # create an empty list to later store extract rows
        with arcpy.da.SearchCursor(self.feature_class,fields) as cursor:
            for row in cursor:
                rows.append(row)

        # Step 3: Convert to pandas DataFrame
        df = pd.DataFrame(rows, columns=fields)
                
        return okay, df


# Uncomment this when you get to the appropriate block in the scripts
#  file and re-load the functions

class smartPanda(pd.DataFrame):

    # This next bit is advanced -- don't worry about it unless you're 
    # curious.  It has to do with the pandas dataframe
    # being a complicated thing that could be created from a variety
    #   of types, and also that it creates a new dataframe
    #   when it does operations.  The use of @property is called
    #   a "decorator".  The _constructor(self) is a specific 
    #   expectation of Pandas when it does operations.  This just
    #   tells it that when it does an operation, make the new thing
    #   into a special smartPanda type, not an original dataframe. 

    @property
    def _constructor(self):
        return smartPanda
    
    # here, just set up a method to plot and to allow
    #   the user to define the min and max of the plot. 


    def scatterplot(self, x_field, y_field, title=None, 
                    x_min=None, x_max=None, 
                    y_min=None, y_max=None):
        """Make a scatterplot of two columns, with validation."""

        # Validate
        for field in [x_field, y_field]:
            if field not in self.columns:
                raise ValueError(f"Field '{field}' not found in DataFrame columns.")

        # filter the range
        df_to_plot = self
        if x_min is not None:
            df_to_plot = df_to_plot[df_to_plot[x_field] >= x_min]
        if x_max is not None:
            df_to_plot = df_to_plot[df_to_plot[x_field] <= x_max]
        if y_min is not None:
            df_to_plot = df_to_plot[df_to_plot[y_field] >= y_min]
        if y_max is not None:
            df_to_plot = df_to_plot[df_to_plot[y_field] <= y_max]



        # Proceed to plot
        plt.figure(figsize=(8,6))
        plt.scatter(df_to_plot[x_field], df_to_plot[y_field])
        plt.xlabel(x_field)
        plt.ylabel(y_field)
        plt.title(title if title else f"{y_field} vs {x_field}")
        plt.grid(True)
        plt.show()


    def mean_field(self, field):
        """Get mean of a field, ignoring NaN."""
        return self[field].mean(skipna=True)

    def save_scatterplot(self, x_field, y_field, outfile, title=None, 
                    x_min=None, x_max=None, 
                    y_min=None, y_max=None):
        """Make a scatterplot of two columns, with validation."""

        # Validate
        for field in [x_field, y_field]:
            if field not in self.columns:
                raise ValueError(f"Field '{field}' not found in DataFrame columns.")

        # filter the range
        df_to_plot = self
        if x_min is not None:
            df_to_plot = df_to_plot[df_to_plot[x_field] >= x_min]
        if x_max is not None:
            df_to_plot = df_to_plot[df_to_plot[x_field] <= x_max]
        if y_min is not None:
            df_to_plot = df_to_plot[df_to_plot[y_field] >= y_min]
        if y_max is not None:
            df_to_plot = df_to_plot[df_to_plot[y_field] <= y_max]



        # Proceed to plot
        plt.figure(figsize=(8,6))
        plt.scatter(df_to_plot[x_field], df_to_plot[y_field])
        plt.xlabel(x_field)
        plt.ylabel(y_field)
        plt.title(title if title else f"{y_field} vs {x_field}")
        plt.grid(True)
        plt.savefig(outfile)
        plt.close()

    def plot_from_file(self, csv_control_file_path):
        #  This reads the file at csv_control_file_path
        #   and uses it to make a plot, and then save
        #   it.  

        #  First, use the pandas functionality to read the
        #    .csv file.  The file should have two columns:
        #   param and value
        #  the param is the name of the item of interest, for 
        #    example "in_file", and the value is the value 
        #    of that param. 
        #  The required params are:
        #     param   -> value type
        #     --------------------
        #     x_field -> string
        #     y_field -> string
        #     outfile -> string path to graphics file output
        #  Optional:
        #     x_min -> numeric
        #     x_max -> numeric
        #     y_min -> numeric
        #     y_max -> numeric
             

        try: 
            params = pd.read_csv(csv_control_file_path)
        except Exception as e:
            print(f"Problem reading the {csv_control_file_path}")
            return False
        
        # Then we'll turn it into a dictionary
        #  To do this, we'll use a new functionality that you'll
        #  see in Python a lot -- "zip".   Look it up!  
        # Also, you can see I'm doing a trick with the 
        #  definition of the dictionary -- 
        
        try:
            param_dict ={k.strip(): v for k,v in zip(params['Param'], params['Value'])}

        except Exception as e:
            print(f"Problem setting up dictionary: {e}")

        # Then check that the required params are present
        # required params
        required_params = ["x_field", "y_field", "outfile"]

        #  Use a list comprehension and the .keys() to test 
        #   if the required ones are in the dictionary

        missing = [m for m in required_params if m not in param_dict.keys()]
        if missing:
            print("The param file needs to have these additional parameters")
            print(missing)
            return False


        #  Now add in "None" vals for the 
        #    optional params if the user does not set them


        optional_params = ["x_min", "x_max", "y_min", "y_max"]
        # go through the optional params, and if one is 
        #   is not in the param_dict, add it but give it the 
        #   value of "None" so the plotter won't set it. 

       
        for p in optional_params:
            if p not in param_dict.keys():
                param_dict[p] = None
        # convert numeric parameters from strings to floats
        for p in ["x_min", "x_max", "y_min", "y_max"]:
            if param_dict[p] is not None:
                param_dict[p] = float(param_dict[p])
                
        # Finally, do the plot! 
        try:
            self.save_scatterplot(param_dict['x_field'], 
                               param_dict['y_field'], 
                               param_dict['outfile'], 
                               x_min = param_dict['x_min'], 
                               x_max = param_dict['x_max'],
                               y_min = param_dict['y_min'],
                               y_max = param_dict['y_max'])
            print(f"wrote to {params}")
            return True   # report back success
        except Exception as e:
            print(f"Problem saving the scatterplot: {e}")

        
            
        
        








