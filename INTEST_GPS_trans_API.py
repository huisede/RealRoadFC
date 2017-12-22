import math as Math

x_PI = 3.14159265358979324 * 3000.0 / 180.0
PI = 3.1415926535897932384626
a = 6378245.0
ee = 0.00669342162296594323


def GPS_FIX_WGS84(lgt, lat):
    lgt = int(lgt / 100) + (lgt / 100 - int(lgt / 100)) * 100 / 60
    lat = int(lat / 100) + (lat / 100 - int(lat / 100)) * 100 / 60
    return wgs84togcj02(lgt, lat)


def wgs84togcj02(lng, lat):
    if out_of_china(lng, lat):
        return [lng, lat]
    else:
        dlat = transformlat(lng - 105.0, lat - 35.0)
        dlng = transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * PI
        magic = Math.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = Math.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
        dlng = (dlng * 180.0) / (a / sqrtmagic * Math.cos(radlat) * PI)
        mglat = lat + dlat
        mglng = lng + dlng
        return [mglng, mglat]


def transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * Math.sqrt(abs(lng))
    ret = ret + (20.0 * Math.sin(6.0 * lng * PI) + 20.0 * Math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret = ret + (20.0 * Math.sin(lat * PI) + 40.0 * Math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret = ret + (160.0 * Math.sin(lat / 12.0 * PI) + 320 * Math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret


def transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * Math.sqrt(abs(lng))
    ret = ret + (20.0 * Math.sin(6.0 * lng * PI) + 20.0 * Math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret = ret + (20.0 * Math.sin(lng * PI) + 40.0 * Math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret = ret + (150.0 * Math.sin(lng / 12.0 * PI) + 300.0 * Math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    return (lng < 72.004 or lng > 137.8347) or ((lat < 0.8293 or lat > 55.8271) or False)
