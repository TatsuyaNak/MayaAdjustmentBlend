# MayaAdjustmentBlend
A Python script to implement Adjustment Blend method with a animation layer in Autodesk Maya.
Copyright (c) 2025 Tatsuya Nakamura

Adjustment Blending is a method for adjusting additive layer interpolation between keyframes,
 so that movement on the layer is shifted to areas where there is already movement on the base layer.

This helps to maintain the existing energy of the base layer motion, and
 helps to maintain contact points. For more information,
 see this talk from GDC 2016: https://youtu.be/eeWBlMJHR14?t=518

This script was originally written by Dan Lowe as part of the MobuCore package for Motion Builder.
