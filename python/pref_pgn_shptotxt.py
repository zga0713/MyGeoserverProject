# coding=utf-8
import os
os.environ['PROJ_LIB'] = r'D:\Python\Lib\site-packages\osgeo\data\proj'
try:
    from osgeo import gdal
    from osgeo import ogr
except ImportError:
    import gdal
    import ogr
# pathStr,shp文件的全路径
def ReadVectorFile(pathStr):

    # 返回结果是一个list
    result=[]
    # 支持中文路径
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # 属性表字段支持中文
    gdal.SetConfigOption("SHAPE_ENCODING", "")
    strVectorFile = pathStr
    # 注册所有的驱动
    ogr.RegisterAll()
    # 打开数据
    ds = ogr.Open(strVectorFile, 0)
    # 获取该数据源中的图层个数，一般shp数据图层只有一个，如果是mdb、dxf等图层就会有多个
    iLayerCount = ds.GetLayerCount()
    # 获取第一个图层
    oLayer = ds.GetLayerByIndex(0)
    # 对图层进行初始化
    oLayer.ResetReading()
    # 获取图层中的属性表表头并输出,可以定义建表语句
    print("属性表结构信息：")
    oDefn = oLayer.GetLayerDefn()
    iFieldCount = oDefn.GetFieldCount()
    for iAttr in range(iFieldCount):
        oField = oDefn.GetFieldDefn(iAttr)
        print("%s: %s(%d.%d)" % ( \
     \
            oField.GetNameRef(), \
     \
            oField.GetFieldTypeName(oField.GetType()), \
     \
            oField.GetWidth(), \
     \
            oField.GetPrecision()))
    # 输出图层中的要素个数
    print("要素个数 = ", oLayer.GetFeatureCount(0))
    oFeature = oLayer.GetNextFeature()
    # 下面开始遍历图层中的要素，将对象都作为string输出
    while oFeature is not None:
        # 获取要素中的属性表内容
        lineStr=[]
        for iField in range(iFieldCount):
            lineStr.append(oFeature.GetFieldAsString(iField))
    # 获取要素中的几何体
        oGeometry = oFeature.GetGeometryRef()
        lineStr.append(str(oGeometry))
        # print(lineStr)
        result.append(lineStr)
        # 循环
        oFeature = oLayer.GetNextFeature()
    print("数据集关闭！")
    return result

if __name__ == '__main__':
    result=ReadVectorFile(r'c:\Users\zhou0\Desktop\MyGeoserverProject\data\V6 Time Series Prefecture Polygons\v6_time_pref_pgn_utf_wgs84\v6_time_pref_pgn_utf_wgs84.shp')
    f_new=open(r'c:\Users\zhou0\Desktop\MyGeoserverProject\data\V6 Time Series Prefecture Polygons\v6_time_pref_pgn_utf_wgs84\v6_time_pref_pgn_utf_wgs84.txt','a',encoding='utf-8')
    for r in result:
        for p in r:
            f_new.write(p+'\t')
        f_new.write('\n')
    f_new.close()