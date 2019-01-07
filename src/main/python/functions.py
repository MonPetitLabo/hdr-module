#!/usr/bin/env python

import gphoto2 as gp
import time

# ------------
# --- Constants
# -----------
CAPTURE_TARGET = 'capturetarget'
SHUTTER_SPEED = 'shutterspeed'
ISO = 'iso'
APERTURE = 'aperture'

cameraConfiguration = {} 
cameraTechnicalConfiguration = {}

def initCameraConfiguration(camera) :
    getAllChoiceFromParameter(camera, CAPTURE_TARGET)
    getAllChoiceFromParameter(camera, SHUTTER_SPEED)
    getAllChoiceFromParameter(camera, ISO)
    getAllChoiceFromParameter(camera, APERTURE)
    

def getCamera() :
    camera = gp.check_result(gp.gp_camera_new())
    gp.check_result(gp.gp_camera_init(camera))
    return camera

def releaseCamera(camera) : 
    gp.check_result(gp.gp_camera_exit(camera))


def getConfigurationOf(camera) :
    return gp.check_result(gp.gp_camera_get_config(camera))

def getPropertyIn(config, param) : 
    return gp.check_result(gp.gp_widget_get_child_by_name(config, param))

def getCaptureTarget(camera) :
    config = getConfigurationOf(camera)
    capture_target = getPropertyIn(config, 'capturetarget') 
    return gp.check_result(gp.gp_widget_get_value(capture_target))

def getAttributeObject(camera, name) :
    config = getConfigurationOf(camera)
    return getPropertyIn(config, name) 

def getAllChoiceFromParameter(camera, parameter):
    config = getConfigurationOf(camera)
    capture_target = getPropertyIn(config, parameter)
    for n in range(gp.check_result(gp.gp_widget_count_choices(capture_target))) :
        choice = gp.check_result(gp.gp_widget_get_choice(capture_target, n))
    
        if not (cameraConfiguration.has_key(parameter)) :
            cameraConfiguration[parameter] = {} 
        
        if not (cameraTechnicalConfiguration.has_key(parameter)) :
            cameraTechnicalConfiguration[parameter] = {} 

        cameraConfiguration[parameter][choice] = n 
        cameraTechnicalConfiguration[parameter][n] = choice
    return 
    

def setPropertyTo(camera, parameter, index) :
    config = getConfigurationOf(camera)
    capture_target = gp.check_result(gp.gp_widget_get_child_by_name(config, parameter))
    value = gp.check_result(gp.gp_widget_get_choice(capture_target, index))
    gp.check_result(gp.gp_widget_set_value(capture_target, value))
    gp.check_result(gp.gp_camera_set_config(camera, config))
    return 

def getValueOfSelectedParameter(camera, parameter) :
    config = getConfigurationOf(camera)
    capture_target = getPropertyIn(config, parameter) 
    return gp.check_result(gp.gp_widget_get_value(capture_target))

def getIndexOfSelectedParameter(camera, parameter) : 
    return cameraConfiguration[parameter][getValueOfSelectedParameter(camera, parameter)]

def takePhoto(camera, speed = -1, aperture = -1, iso = -1 ):
    if ( speed < 0 ) :
        speed = getIndexOfSelectedParameter(camera, SHUTTER_SPEED)
    if ( aperture < 0 ) :
        aperture = getIndexOfSelectedParameter(camera, APERTURE)
    if ( iso < 0 ) : 
        iso = getIndexOfSelectedParameter(camera, ISO)

    updateConfiguration(camera, speed, aperture, iso)

    camera.capture(gp.GP_CAPTURE_IMAGE)

    return 

def takePhotoHdr(camera, nbPicture, evRequire) :
    speed = getIndexOfSelectedParameter(camera, SHUTTER_SPEED)
    sequence = buildSpeedSequence(speed, nbPicture, evRequire)
    for speedIndex in sequence : 
        takePhoto(camera, speedIndex)
        time.sleep(0.03)

    # reset default configuration 
    setPropertyTo(camera, SHUTTER_SPEED, speed)

def takeLongPhoto(camera) :
    return

def updateConfiguration(camera, speed, aperture, iso):
    setPropertyTo(camera, SHUTTER_SPEED, speed)
    setPropertyTo(camera, APERTURE, aperture)
    setPropertyTo(camera, ISO, iso)
    return


def buildSpeedSequence(baseSpeedIndex, nbPicture, evRequire): 
    sequence = [baseSpeedIndex] 
    for i in range(0, (nbPicture - 1) / 2) :
        minusSpeedIndex = baseSpeedIndex - evRequire*(i+1)
        if (cameraTechnicalConfiguration[SHUTTER_SPEED].has_key(minusSpeedIndex)) :
            sequence.append(minusSpeedIndex)

        maxSpeed = baseSpeedIndex + evRequire*(i+1)
        if (cameraTechnicalConfiguration[SHUTTER_SPEED].has_key(maxSpeed)) : 
            sequence.append(maxSpeed)


    return sequence

