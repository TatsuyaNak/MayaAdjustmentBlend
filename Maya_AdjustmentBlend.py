# AdjustmentBlend for Maya
# Copyright (C) 2025 Tatsuya Nakamura - All Rights Reserved
# You may use, distribute and modify this code under the
# terms of the LGPL 2.1 license.

'''
Adjustment Blending is a method for adjusting additive layer interpolation between keyframes,
 so that movement on the layer is shifted to areas where there is already movement on the base layer.

This helps to maintain the existing energy of the base layer motion, and
 helps to maintain contact points. For more information,
 see this talk from GDC 2016: https://youtu.be/eeWBlMJHR14?t=518

This script was originally written by Dan Lowe as part of the MobuCore package.
'''

import maya.cmds as cmds
import maya.mel as mel

BASE_LAYER = 'BaseAnimation'

# Class for a key on f-curve.
class AnimKey(object):
    def __init__(self, t=0.0, v=0.0):
        self.__Time = t
        self.__Value = v
    
    def __str__(self):
        return '[{}: {}]'.format(self.__Time, self.__Value)

    def getTime(self):
        return self.__Time

    def setTime(self, t):
        self.__Time = t

    Time = property(getTime, setTime)

    def getValue(self):
        return self.__Value

    def setValue(self, v):
        self.__Value = v
    
    Value = property(getValue, setValue)


# Groups pairs of keys from the layer fcurve, between which it will run an independent adjustment blend (allows adjustment blend to work with multiple key poses on the layer).
def GetKeyPairsFromFCurve(keys):
    keyPairsList = []
    for i in range(len(keys)-1):
        startKeyTime = keys[i].Time
        startKeyValue = keys[i].Value
        stopKeyTime = keys[i+1].Time
        stopKeyValue = keys[i+1].Value
        keyPairsList.append([startKeyTime, stopKeyTime, startKeyValue, stopKeyValue])
    return keyPairsList


# TODO: it should return the curves connected to the object.
def GetObjectFCurvesForLayer_Maya(obj, layerName):
    # TODO check if each attribute has a curve.
    return ['translateX', 'translateY', 'translateZ',
            'rotateX', 'rotateY', 'rotateZ']


# Reads the per frame values from an fcurve (doesn't require keys to be on those frames).
def EvaluateFCurveForKeyPairTimespan(obj, fcurve, startTime, stopTime, layerName=BASE_LAYER):
    keyPairSpanValues = []
    current = startTime
    SwitchLayer(layerName)
    while not current > stopTime:
        value = cmds.keyframe(obj+'.'+fcurve, query=True, eval=True, time=(current, current))
        if value:
            keyPairSpanValues.append([current, value[0]])
        current += 1.0
    SwitchLayer(BASE_LAYER)
    return keyPairSpanValues


# Finds the percentage of change that occured on the base layer curve, for the key pair.
def GetPercentageOfChangeValues(spanValues):
    changeValues = [0.0]
    for i in range(len(spanValues)-1):
        frameChangeValue = abs(spanValues[i+1][1] - spanValues[i][1])
        changeValues.append(frameChangeValue)
    totalBaseLayerChange = sum(changeValues)
    percentageValues = []
    for i in range(len(changeValues)):
        if totalBaseLayerChange != 0:
            percentageValues.append([spanValues[i][0], (100.0 / totalBaseLayerChange) * changeValues[i]])
    return percentageValues, totalBaseLayerChange


def SwitchLayer(layerName):
    """
    Utility function for switching animation layer
    """
    layers = cmds.ls(type='animLayer')
    for layer in layers:
        if layer == layerName:
            mel.eval('animLayerEditorOnSelect "'+layerName+'" 1;')
        else:
            mel.eval('animLayerEditorOnSelect "'+layer+'" 0;')


def GetKeys(obj, fcurve, animLayer=BASE_LAYER):
    """
    Utility function for getting keys on f-curve in a specified layer.
    """
    keys = list()
    SwitchLayer(animLayer)
    numKeys = cmds.keyframe( obj, query=True, attribute=fcurve, keyframeCount=True )
    for index in range(numKeys):
        timeValue = cmds.keyframe(obj, at=fcurve, query=True, index=(index, index))
        if timeValue:
            timeValue = timeValue[0]
            value = cmds.keyframe(obj, at=fcurve, query=True, eval=True, time=(timeValue, timeValue))
            if value:
                keys.append(AnimKey(timeValue, value[0]))
    SwitchLayer(BASE_LAYER)
    return keys


# The main adjustment blend function that does everything else.
# This is what you'd run if you were just adjustment blending a single object.
#
# For Maya, added specifying two layers to work on to the original function.
#
def AdjustmentBlendObject(obj, baseLayer=BASE_LAYER, poseLayer='AnimLayer1'):
    if cmds.objExists(poseLayer) and cmds.nodeType(poseLayer) == 'animLayer':
        poseLayerFCurves = GetObjectFCurvesForLayer_Maya(obj, poseLayer)
        baseLayerFCurves = GetObjectFCurvesForLayer_Maya(obj, baseLayer)
        for i in range(len(poseLayerFCurves)):
            poseFCurve = poseLayerFCurves[i]
            SwitchLayer(poseLayer)
            numKeys = cmds.keyframe(obj, query=True, attribute=poseFCurve, keyframeCount=True )
            if numKeys > 1:
                keys = GetKeys(obj, poseFCurve, animLayer=poseLayer)
                base_keys = GetKeys(obj, baseLayerFCurves[i])
                keyPairsList = GetKeyPairsFromFCurve(keys)
                for keyPair in keyPairsList:
                    startTime = keyPair[0]
                    stopTime = keyPair[1]
                    startValue = keyPair[2]
                    stopValue = keyPair[3]
                    spanValues = EvaluateFCurveForKeyPairTimespan(obj, baseLayerFCurves[i], startTime, stopTime)
                    percentageValues, totalBaseLayerChange = GetPercentageOfChangeValues(spanValues)
                    totalPoseLayerChange = abs(stopValue - startValue)
                    previousValue = startValue
                    for index, value in enumerate(percentageValues):
                        valueDelta = (totalPoseLayerChange / 100.0) * value[1]
                        if stopValue > startValue:
                            currentValue = previousValue + valueDelta
                        else:
                            currentValue = previousValue - valueDelta
                        # Adding a key to the curve in the animation layer.
                        targetValue = currentValue + base_keys[index].Value 
                        cmds.setKeyframe(obj, at=poseLayerFCurves[i], al=poseLayer, value=targetValue, time=(value[0], value[0]))
                        previousValue = currentValue

