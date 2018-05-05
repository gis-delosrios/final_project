import settings
import os
import models
import datetime

if __name__ == '__main__':
    os.system(
        settings.armap_python + ' ' + os.path.join(os.getcwd(),
                                                   'arcpy_create_feature_class.py'))

