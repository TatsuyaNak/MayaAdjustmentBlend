# MayaAdjustmentBlend
A Python script to implement Adjustment Blend method with animation layers in Autodesk Maya.
Copyright (c) 2025 Tatsuya Nakamura

Adjustment Blending is a method for adjusting additive layer interpolation between keyframes,
 so that movement on the layer is shifted to areas where there is already movement on the base layer.

This script was originally written by Dan Lowe as part of the MobuCore package for Motion Builder.
I wrote this to implement it with Autodesk Maya

This helps to maintain the existing energy of the base layer motion, and helps to maintain contact points. For more information,
 see this talk from GDC 2016: https://youtu.be/eeWBlMJHR14?t=518

In this video, Dan Lowe explains why this method can be applied to fix a sliding foot for keyframes created with raw motion-capture (mocap) with Motion Builder. Here are some parts of a transcript from the above video:

8:56) The way we do (clean up keyframes in raw mocap data) is that, first, we degrade a layer and then we'd apply a consistent pose to the start of the clip and to the end of the clip.

 But you will notice however that we now have sliding feet and this is because as you see here in the curves window.

 A post change is being applied across the entire length of this animation. So to fix this, the animator would have to manually adjust the curves so that our post change only applies when the foots moving and this type of manual adjustment is really painstaking work because it has to be done for each effective that's sliding.

9:45) Now let's look at the adjustment blending tool and as before we create a layer and we apply a start pose and our end pose. As before, we've got a sliding feet and then we run the tool and that's it's done already.

11:45) What are we actually doing here?

 We want to hide any adjustments that we make during the parts where our animation is already moving and we want to make no adjustments where our animation is still.

 1. For each curve on the Base Layer of our animation we start by looking at the amount of change that's happening from one frame to the next.

 2. Then we store up those values and we total them up. We then convert those per frame values into percentages of the total.

 3. And once we have that, if we map these percentages to a curve you get something that looks like this. This is our Motion Delta.

 4. As we wanted, it's showing us where we've got movement and how much movement and the flat parts are areas where this curve is static. Then, on our layer where we applied our new poses, we just apply those sample per frame percentage values and that's it.

12:43)
 One of the really nice things about this method is that since it's just math operations on curves you can do this in any of the DCC's. It also means that we can do this at runtime and I'm going to talk about that a bit later.

