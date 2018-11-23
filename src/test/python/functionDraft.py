#!/usr/bin/env python

import gphoto2 as gp

# ------------
# --- Constants
# -----------
CAPTURE_TARGET = 'capturetarget'
SHUTTER_SPEEP = 'shutterspeed'
ISO = 'iso'
APERTURE = 'aperture'

cameraConfiguration = {} 

def initCameraConfiguration(camera) :
    getAllChoiceFromParameter(camera, CAPTURE_TARGET)
    getAllChoiceFromParameter(camera, SHUTTER_SPEEP)
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
        
        cameraConfiguration[parameter][choice] = n 
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

def takePhoto(camera, speed = -1 ):
    if ( speed < 0 ) :
        speed = getIndexOfSelectedParameter(camera, SHUTTER_SPEEP)

    updateConfiguration(camera, speed)
    return 

def updateConfiguration(camera, speed):
    setPropertyTo(camera, SHUTTER_SPEEP, speed)
    return
