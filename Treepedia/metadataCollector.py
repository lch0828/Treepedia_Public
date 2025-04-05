
# This function is used to collect the metadata of the GSV panoramas based on the sample point shapefile

# Copyright(C) Xiaojiang Li, Ian Seiferling, Marwa Abdulhai, Senseable City Lab, MIT 

def GSVpanoMetadataCollector(samplesFeatureClass,num,ouputTextFolder):
    '''
    This function is used to call the Google API url to collect the metadata of
    Google Street View Panoramas. The input of the function is the shpfile of the create sample site, the output
    is the generate panoinfo matrics stored in the text file
    
    Parameters: 
        samplesFeatureClass: the shapefile of the create sample sites
        num: the number of sites proced every time
        ouputTextFolder: the output folder for the panoinfo
        
    '''
    
    import urllib,urllib3
    import xmltodict
    import json
    import io
    from osgeo import ogr, osr
    import time
    import os,os.path
    
    if not os.path.exists(ouputTextFolder):
        os.makedirs(ouputTextFolder)
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    
    # change the projection of shapefile to the WGS84
    dataset = driver.Open(samplesFeatureClass)
    layer = dataset.GetLayer()
    
    sourceProj = layer.GetSpatialRef()
    targetProj = osr.SpatialReference()
    targetProj.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(sourceProj, targetProj)
    
    # loop all the features in the featureclass
    feature = layer.GetNextFeature()
    featureNum = layer.GetFeatureCount()
    batch = featureNum//num +1
    
    for b in range(batch):
        # for each batch process num GSV site
        start = b*num
        end = (b+1)*num
        if end > featureNum:
            end = featureNum
        
        ouputTextFile = 'Pnt_start%s_end%s.txt'%(start,end)
        ouputGSVinfoFile = os.path.join(ouputTextFolder,ouputTextFile)
        
        # skip over those existing txt files
        if os.path.exists(ouputGSVinfoFile):
            continue
        
        time.sleep(1)
        
        with open(ouputGSVinfoFile, 'w') as panoInfoText:
            # process num feature each time
            for i in range(start, end):
                feature = layer.GetFeature(i)        
                geom = feature.GetGeometryRef()
                
                # trasform the current projection of input shapefile to WGS84
                #WGS84 is Earth centered, earth fixed terrestrial ref system
                geom.Transform(transform)
                lat = geom.GetX()
                lon = geom.GetY()
                key = r'' #Input Your Key here 
                
                # get the meta data of panoramas 
                urlAddress = r'https://maps.googleapis.com/maps/api/streetview/metadata?location={},{}&key=AIzaSyDqOgEWmqig04CypCMucACGE9T5mT6bT-I'.format(lat,lon)
                print(urlAddress)
                
                time.sleep(0.05)
                # the output result of the meta data is a xml object
                metaDataxml = urllib.request.urlopen(urlAddress)
                metaData = metaDataxml.read().decode('utf-8')

                # print("Raw response (first 500 characters):", metaData[:500])  
                
                data = json.loads(metaData)
                
                # in case there is not panorama in the site, therefore, continue
                if data['status']!='OK':
                    continue
                else:                                        
                    # get the meta data of the panorama
                    panoDate = data['date']
                    panoId = data['pano_id']
                    panoLat = data['location']['lat']
                    panoLon = data['location']['lng']
                    
                    print(f"The coordinate ({panoLon},{panoLat}), panoId is: {panoId}, panoDate is: {panoDate}")
                    lineTxt = f"panoID: {panoId} panoDate: {panoDate} longitude: {panoLon} latitude: {panoLat}\n"
                    panoInfoText.write(lineTxt)
                    
        panoInfoText.close()


# ------------Main Function -------------------    
if __name__ == "__main__":
    import os, os.path
    
    root = 'MYPATH/spatial-data'
    inputShp = os.path.join(root,'Cambridge20m.shp')
    outputTxt = root
    
    GSVpanoMetadataCollector(inputShp,1000,outputTxt)

