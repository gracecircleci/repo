import json, os.path
import pandas as pd
import numpy as np
from pandas import json_normalize

# Legacy Data 
class DataUtil():
    FIRST_ROW_VID = 92
    RECORD_PATH = ['Frame', 'Data', 'Items', 'Frame','Data','SummaryItems']
    REQUIRED_COLUMNS = [
        'Frame.Expires', 'Frame.Data.Title','Frame.Data.SubTitles', 
        'Frame.Data.ImageHandles',
        'Frame.Data.BigScreenPlayInfo.NAME_SPACE',
        'Frame.Data.BigScreenPlayInfo.MESSAGE',
        'Frame.Data.BigScreenPlayInfo.APP_ID',
        'Frame.Data.BigScreenPlayInfo.IMAGE_HANDLE.VibeHandle.Sid',
        'Frame.Data.BigScreenPlayInfo.IMAGE_HANDLE.VibeHandle.Iid',
        'Frame.Data.BigScreenPlayInfo.IMAGE_HANDLE.VibeHandle._tid',
        'Frame.Data.BigScreenPlayInfo.IMAGE_HANDLE._tid',
        'Frame.Data.BigScreenPlayInfo.PivotDataLinkId',
        'Frame.Data.BigScreenPlayInfo.SuppressImagePivot',
        'Frame.Data.Pivot.Expand', 
        'Frame.Data.Pivot.Href',
        'Frame.Data.Pivot.Vibe.Sid', 
        'Frame.Data.Pivot.Vibe.Iid',
        'Frame.Data.Pivot.Vibe._tid',
        'Frame.Data.Pivot.Vid',
        'Frame.Data.Pivot._tid', 
        'Frame.Data.PivotDataLinkId',
        ]
    NOT_NULL_FIELDS = [
        'Frame.Data.Title', 'Frame.Data.SubTitles',
        'Frame.Data.BigScreenPlayInfo.NAME_SPACE',
        'Frame.Data.BigScreenPlayInfo.MESSAGE',
        'Frame.Data.BigScreenPlayInfo.APP_ID',
        'Frame.Data.BigScreenPlayInfo.IMAGE_HANDLE.VibeHandle.Sid',
        'Frame.Data.BigScreenPlayInfo.IMAGE_HANDLE.VibeHandle.Iid',
        'Frame.Data.BigScreenPlayInfo.IMAGE_HANDLE.VibeHandle._tid',
        'Frame.Data.BigScreenPlayInfo.IMAGE_HANDLE._tid',
        'Frame.Data.BigScreenPlayInfo.PivotDataLinkId',
        'Frame.Data.BigScreenPlayInfo.SuppressImagePivot',
    ]

    @staticmethod
    def writeDataColumnNamesToFile(df, outfile='output/home_columns.txt'):
        assert df is not None
        # get the output filepath, create the directory if not exist
        fpath, fname = os.path.split(outfile)
        if (not os.path.exists(fpath)) and (fpath !=''):
            os.makedirs(fpath)

        # get data columns and write to the output file
        str_axes = '\n'.join(str(x) for x in df.axes)
        with open(outfile, 'w+') as fo:
            fo.writelines(str_axes)  

    @staticmethod
    def allColumnsExist(df, required_columns):
        assert df is not None
        assert required_columns != []

        # verify the reqired_columns is a subset of the data columns
        df_columns_set = set(list(df.columns))
        required_columns_set = set(required_columns)
        required_columns_set.difference(df_columns_set)
        exist = True if set(required_columns_set).issubset(df_columns_set) else False
        return exist

    @staticmethod
    def checkRequiredFieldsNotNull(df):
        df = df.loc[ df['Vid']== DataUtil().FIRST_ROW_VID ]
        df = df.reindex(columns= DataUtil().NOT_NULL_FIELDS)
        json_str = df.to_json(orient='index')
        jsonobj = json.loads(json_str)
        with open('output/home_tab_required_fields.json', 'w+') as fo:
             json.dump(jsonobj, fo, separators=(',',':'), sort_keys=True, indent=4)

        total_nulls = df.isnull().sum().sum()
        # print the columns that are null (they should not be null)
        if total_nulls !=0:
            print(df.isnull().sum())
        return total_nulls


        
