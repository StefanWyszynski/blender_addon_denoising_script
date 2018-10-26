bl_info = {
    "name": "Denoiser animation Avisynth script generator",
    "description": "Generate denoising script for Avisynth",
    "author": "Stefan Wyszyński",
    "version": (0, 3),
    "blender": (2, 78, 0),
    "location": "Properties > Render > Denoising scrip generator",
    "warning": "Requires Avisynth to denoise the images!",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Render"}

import bpy
import os
from os import system, sep, path, makedirs, remove, chmod, path as ospath, listdir
import stat
from shutil import copyfile, rmtree
from random import random


class MergeProgAnim(bpy.types.Operator):
    """Generate Avisynth script and images"""
    bl_idname = "generate.script"
    bl_label = "Generate Avisynth script"
    animation = bpy.props.BoolProperty()

    def execute(self, context):
        animation = self.animation
        scn = context.scene
        ext = scn.render.file_extension

        range_start = scn.frame_start
        range_end = scn.frame_end + 1

        # count animation frames that has been written do drive
        frames_count = 0
        for frameN in range(range_start, range_end):
            if (ospath.exists(bpy.context.scene.render.frame_path(frame=frameN))):
                frames_count = frames_count + 1

        pathonly = scn.render.filepath
        # movie path:
        # for AVI RAW this is the path of any frame from start to end because file name will be for example "movie001-200.avi
        # for PNG or another image format we will generate movie (from set of images) and assign its file name to this variable
        inputMoviePath = bpy.context.scene.render.frame_path(frame=range_start)

        # generate movie from images if its not AVI_RAW
        if (bpy.context.scene.render.image_settings.file_format != 'AVI_RAW'):
            if (frames_count > 0):
                # save frame duration
                frameDuration = 1.0 / scn.render.fps
                # we will generate inputvideo.txt in animation folder which will contain the following lines for all frames:
                # file 'current_animation_image_path'
                # duration FRAME_DURATION
                inputTextPath = pathonly + "inputvideo.txt"
                f = open(inputTextPath, 'w+')
                for frameN in range(range_start, range_end):
                    currentImage = bpy.context.scene.render.frame_path(frame=frameN)
                    if (ospath.exists(currentImage)):
                        f.write("file '" + currentImage + "'\n")
                        f.write("duration " + str(frameDuration) + "\n")
                f.close()

                # it is time to create .bat file with FFmpeg script. This script will user above inputvideo.txt to
                # generate output movie001-200.avi
                movieBatPath = pathonly + "convertToMovie.bat"
                outputMoviePath = pathonly + str(range_start) + "-" + str(range_end) + ".avi"
                f = open(movieBatPath, 'w+')

                if scn.UseH264ForPNG:
                    if scn.USEFastEncodingH264ForPNG:
                        f.write("ffmpeg -y -safe 0 -f concat -i " + inputTextPath + " -vf fps=" + str(
                            scn.render.fps) + " -pix_fmt yuv420p -c:v libx264 -preset ultrafast -crf 0 " + outputMoviePath + "\n")
                    else:
                        f.write("ffmpeg -y -safe 0 -f concat -i " + inputTextPath + " -vf fps=" + str(
                            scn.render.fps) + " -pix_fmt yuv420p -c:v libx264 -preset veryslow -crf 0 " + outputMoviePath + "\n")
                else:
                    f.write("ffmpeg -y -safe 0 -f concat -i " + inputTextPath + " -vf fps=" + str(
                        scn.render.fps) + " -pix_fmt yuv420p -vcodec rawvideo " + outputMoviePath + "\n")  # -pix_fmt yuv420p -vcodec rawvideo
                f.close()
                chmod(movieBatPath, stat.S_IRWXU)

                # now we will run created .bat file to generate movie based on animation frames saved in images
                if (ospath.exists(movieBatPath)):
                    m = os.system(movieBatPath)
                    if m == 0:
                        scn.SomeError = False
                    else:
                        scn.SomeError = True

                    # remove(movieBatPath)
                    if (ospath.exists(outputMoviePath)):
                        inputMoviePath = outputMoviePath

        # create merger script
        f = open(pathonly + "denoise.avs", 'w+')

        f.write("# this script is a modified part of:\n")
        f.write("# 8mm film restoration script by videoFred.\n")
        f.write("# www.super-8.be\n")
        f.write("# info@super-8.be\n")
        f.write("# version 01.A with frame interpolation\n")
        f.write("# release date: june 20, 2012\n")
        f.write("#============================================================================================\n")
        f.write("# august 2010: added removerdirtMC() as suggested by John Meyer\n")
        f.write("# october 2010: auto sharpening parameters\n")

        f.write("film= \"" + inputMoviePath + "\"\n")
        f.write("result=\"result1\" \n")

        f.write("numerator = " + str(scn.render.fps) + " # numerator for the interpolator (final frame rate) \n")
        f.write("denumerator = 1 # denumerator  example: 60000/1001= 59.94fps\n")

        # f.write("final_framerate = " + str(scn.render.fps) + " # final frame rate \n")
        # f.write("frame_blend= 0.0 #0.4 set this lover for less blending \n")
        f.write("maxstabH=0\n")
        f.write("maxstabV=0 #maximum values for the stabiliser (in pixels) 20 is a good start value\n")

        f.write("trust_value= 1.0     # scene change detection, higher= more sensitive\n")
        f.write("cutoff_value= 0.0   # no need to change this, but you can play with it and see what you get\n")

        f.write("dirt_strenght = " + str(scn.DirtStrenght) + " # set this lower for clean films.\n")

        # f.write("frame_blend= 0.0 #0.4 set this lover for less blending \n")
        f.write("denoising_strenght= " + str(
            scn.DenoisingFilterStrenght) + " #300 denoising level of second denoiser: MVDegrainMulti()\n")
        f.write("denoising_frames=" + str(
            scn.DenoisingFramesComareCount) + " #number of frames for averaging (forwards and backwards) 3 is a good start value\n")
        f.write("block_size=16  #block size of MVDegrainMulti()\n")
        f.write("block_size_v= 16\n")
        f.write("block_over= 8  #block overlapping of MVDegrainMulti()\n")
        f.write("USM_sharp_ness= " + str(
            scn.USMSharpness) + " USM_radi_us= 3  # 40 this is the start value for the unsharpmask sharpening\n")
        f.write("#do not set radius less then 3\n")
        f.write("#the script will automatically add two other steps with lower radius\n")
        f.write(
            "last_sharp=" + str(scn.FinalSharpen) + " #final sharpening step after degraining and before blending\n")
        f.write("last_blur= " + str(scn.FinalBlur) + " #this smooths out the heavy sharpening effects\n")
        f.write("SetMemoryMax(" + str(scn.MaxMemoryForDenoising) + ")  #set this to 1/3 of the available memory\n")

        f.write("Loadplugin(\"Deflicker.dll\")\n")
        f.write("Loadplugin(\"Depan.dll\")\n")
        f.write("LoadPlugin(\"DepanEstimate.dll\")\n")
        f.write("Loadplugin(\"removegrain.dll\")\n")
        f.write("Loadplugin(\"removedirt.dll\")\n")
        f.write("LoadPlugin(\"MVTools.dll\")\n")
        f.write("LoadPlugin(\"MVTools2.dll\")\n")
        f.write("Loadplugin(\"warpsharp.dll\")\n")
        f.write("LoadPlugin(\"Motion_06Dec05B.dll\")\n")
        f.write("Import(\"03_RemoveDirtMC.avs\")\n")
        f.write("Import(\"SmartSmootherHQ.avs\")\n")

        # DirectShowSource(film)
        # source= AviSource(film).assumefps(play_speed).converttoYV12()
        f.write("cleaned= AviSource(film).converttoYV12()\n")

        f.write("stab_reference= cleaned\n")
        f.write("mdata=DePanEstimate(stab_reference,trust=trust_value,dxmax=maxstabH,dymax=maxstabV)\n")
        f.write(
            "stab = DePanStabilize(cleaned, data=mdata, cutoff=cutoff_value, dxmax=maxstabH, dymax=maxstabV, method=0, mirror=15)")
        if scn.UseDeflicker:
            f.write(".deflicker()\n")
        f.write("\n")

        f.write("USM_sharp_ness1 = USM_sharp_ness\n")
        f.write("USM_sharp_ness2 = USM_sharp_ness+(USM_sharp_ness/2)\n")
        f.write("USM_sharp_ness3 = USM_sharp_ness*2\n")

        f.write("USM_radi_us1 = USM_radi_us\n")
        f.write("USM_radi_us2 = USM_radi_us-1\n")
        f.write("USM_radi_us3 = USM_radi_us2-1\n")

        f.write("noise_baseclip = stab\n")

        f.write(
            "cleaned = RemoveDirtMC(noise_baseclip, dirt_strenght).unsharpmask(USM_sharp_ness1, USM_radi_us1, 0).unsharpmask(USM_sharp_ness2, USM_radi_us2, 0)\n")

        f.write(
            "vectors= cleaned.MVAnalyseMulti(refframes=denoising_frames, pel=2, blksize=block_size, blksizev= block_size_v, overlap=block_over, idx=1)\n")
        f.write(
            "denoised= cleaned.MVDegrainMulti(vectors, thSAD=denoising_strenght, SadMode=1, idx=2).unsharpmask(USM_sharp_ness3,USM_radi_us3,0)\n")

        f.write("super= denoised.MSuper()\n")

        f.write(
            "backward_vec= MAnalyse(super, blksize=block_size, blksizev= block_size_v, overlap=block_over, isb=true)\n")
        f.write(
            "forward_vec= MAnalyse(super, blksize=block_size, blksizev= block_size_v, overlap=block_over, isb= false)\n")

        f.write(
            "interpolated = denoised.MFlowFps(super, backward_vec, forward_vec, num=numerator, den=denumerator,ml = 100).sharpen(last_sharp, mmx=false).sharpen(last_sharp, mmx=false).blur(last_blur, mmx=false)\n")
        f.write("result1= interpolated\n")
        # f.write("final_framerate = numerator / denumerator\n")
        # f.write("source1=source1.changeFPS(final_framerate)\n")
        # f.write("resultS1 = stackhorizontal(subtitle(source1, \"original\", size=28, align=2), subtitle(result1, \"result1: manual colors and levels correction\", size=28, align=2))\n")

        # f.write("result1= denoised.converttoYV12().BlendFPS(final_framerate, frame_blend).blur(last_blur)\n")

        if scn.UseSmarthSmootherHQ:
            f.write("result1=result1.ConvertToRGB().VD_SmartSmoothHiQ(" + str(scn.SmarthShootherHQDiameter) + "," + str(
                scn.SmarthShootherHQTreshold) + "," + str(
                scn.SmarthShootherHQAmount) + ",\"average\").ConvertToYUY2()\n")

        if scn.ResizeOnFinish:
            f.write("result1=Lanczos4Resize(result1," + str(scn.FinalResolutionWidth) + "," + str(
                scn.FinalResolutionHeight) + ")\n")

        f.write("Eval(result)\n")

        f.close()

        batpath = pathonly + "denoise.bat"
        avspath = pathonly + "denoise.avs"

        if scn.ExecuteProgram == "AvsPmod":
            f = open(batpath, 'w+')
            f.write("avsPmod.exe \"" + avspath + "\"\n")
            f.close()
            chmod(batpath, stat.S_IRWXU)

        if scn.ExecuteProgram == "VirtualDub":
            f = open(batpath, 'w+')
            f.write("virtualdub.exe \"" + avspath + "\"\n")
            f.close()
            chmod(batpath, stat.S_IRWXU)
        if scn.ExecuteProgram == "Avs2avi":
            f = open(batpath, 'w+')
            f.write("avs2avi.exe \"" + avspath + "\" \"" + avspath + ".avi\" -w -q -c null\n")
            f.close()
            chmod(batpath, stat.S_IRWXU)
        if scn.ExecuteProgram == "ffmpeg":
            f = open(batpath, 'w+')
            f.write("ffmpeg -i \"" + avspath + "\" -an -vcodec rawvideo -y \"" + avspath + ".avi\"\n")
            f.close()
            chmod(batpath, stat.S_IRWXU)

        # run merger script
        if scn.ExecuteProgram != "Generate only":
            m = os.system(batpath)
            if m == 0:
                scn.SomeError = False
            else:
                scn.SomeError = True

        if (ospath.exists(batpath)):
            remove(batpath)

        # full_file_path = pathonly + "preview.png"
        # image = bpy.data.images.load(full_file_path)
        # bpy.ops.render.view_show('INVOKE_SCREEN')
        return {'FINISHED'}


class RENDER_PT_avisynth_script(bpy.types.Panel):
    bl_label = "Avisynth script generator"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'CYCLES'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column(align=False)
        row = col.row(align=True)
        row.operator("wm.url_open", text="",
                     icon="QUESTION").url = "https://blenderartists.org/forum/showthread.php?413157-Denoiser-Addon-for-animatio-in-Blender-script-generator-for-avisynth-or-virtualdub"

        col.prop(scene, "DirtStrenght")
        col.prop(scene, "DenoisingFilterStrenght")
        col.prop(scene, "DenoisingFramesComareCount")
        col.prop(scene, "USMSharpness")
        col.prop(scene, "FinalSharpen")
        col.prop(scene, "FinalBlur")
        col.prop(scene, "MaxMemory")
        col.prop(scene, "UseDeflicker")
        col.prop(scene, "UseSmarthSmootherHQ")
        col.prop(scene, "SmarthShootherHQDiameter")
        col.prop(scene, "SmarthShootherHQTreshold")
        col.prop(scene, "SmarthShootherHQAmount")
        col.prop(scene, "ResizeOnFinish")
        col.prop(scene, "FinalResolutionWidth")
        col.prop(scene, "FinalResolutionHeight")
        col.prop(scene, "UseH264ForPNG")
        col.prop(scene, "USEFastEncodingH264ForPNG")

        col.prop(scene, "ExecuteProgram")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("generate.script", icon="IMAGE_ZDEPTH", text="Generate script").animation = True

        if scene.SomeError:
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Warning!", icon="ERROR")
            col.label(text="Avisynth might not be installed correctly!")
            col.separator()
            col.label(text="Avisynth is an external program used to denoise")
            row = col.row()
            row.label(text="the images")
            row.operator("wm.url_open", text="Why you need this",
                         icon="URL").url = "https://blenderartists.org/forum/showthread.php?413157-Denoiser-Addon-for-animatio-in-Blender-script-generator-for-avisynth-or-virtualdub"
            col.separator()
            # https://sourceforge.net/projects/avisynth2/?source=navbar
            # http://avisynth.nl/index.php/Main_Page
            col.operator("wm.url_open", text="Download Avisynth",
                         icon="URL").url = "https://sourceforge.net/projects/avisynth2/?source=navbar"
            col.operator("wm.url_open", text="Download Virtualdub",
                         icon="URL").url = "https://sourceforge.net/projects/virtualdub/"

            col.operator("wm.url_open", text="Download avsPmod",
                         icon="URL").url = "https://github.com/AvsPmod/AvsPmod/releases"

            col.operator("wm.url_open", text="Download ffmpeg",
                         icon="URL").url = "https://ffmpeg.zeranoe.com/builds/"

            col.operator("wm.url_open", text="Download klite codecs pack",
                         icon="URL").url = "https://www.codecguide.com/download_kl.htm"


def register():
    bpy.types.Scene.SomeError = bpy.props.BoolProperty(
        name="SomeError",
        default=False,
        description="SomeError")

    bpy.types.Scene.DirtStrenght = bpy.props.IntProperty(
        name="Dirt strenght",
        default=30,
        min=1,
        max=200,
        description="How much dirt will be cleaned (this helps to get rid of fireflies if I'm not worng)")

    bpy.types.Scene.DenoisingFilterStrenght = bpy.props.IntProperty(
        name="Denoising strenght",
        default=300,
        description="Strenght of denoising multiframe algorithm")

    bpy.types.Scene.DenoisingFramesComareCount = bpy.props.IntProperty(
        name="Denoising frames to comare",
        default=4,
        min=1,
        max=30,
        description="How many frames will be compared when denoising. The best is range 4 to 7. Larger values gives more blurry result")

    bpy.types.Scene.USMSharpness = bpy.props.IntProperty(
        name="USM Sharpness",
        min=0,
        default=0,
        description="USM sharpness value. Default 0. 40 is quite large value")

    bpy.types.Scene.FinalSharpen = bpy.props.FloatProperty(
        name="FinalSharpen",
        min=0.0,
        default=0.0,
        description="Sharpen after all filters. Value between 0 to 1 is a good to go")

    bpy.types.Scene.FinalBlur = bpy.props.FloatProperty(
        name="Final blur (post processing)",
        min=0.0,
        default=0.0,
        description="Blur after all filters. Value between 0 to 1 is a good to go")

    bpy.types.Scene.MaxMemoryForDenoising = bpy.props.IntProperty(
        name="Max memory for denoisers",
        default=300,
        min=16,
        description="Memory in megabytes used by filters. 1/4 of total memory could be a good choice. Dont go to high because there will be 'out of memmory' error")

    bpy.types.Scene.UseDeflicker = bpy.props.BoolProperty(
        name="Use deflicker",
        default=False,
        description="Do you want to use deflicker?. Better noise reduction in some areas. Sometimes a must have option.")

    bpy.types.Scene.UseSmarthSmootherHQ = bpy.props.BoolProperty(
        name="Use SmarthSmootherHQ denoiser",
        default=False,
        description="Do you want to use smart shoother HQ?. Better noise reduction in some areas. Sometimes a must have option.")

    bpy.types.Scene.SmarthShootherHQDiameter = bpy.props.IntProperty(
        name="SmarthShootherHQ Diameter",
        default=13,
        min=3,
        max=13,
        description="SmarthShootherHQ diameter param. default 13. range 3 to 13.")

    bpy.types.Scene.SmarthShootherHQTreshold = bpy.props.IntProperty(
        name="SmarthShootherHQ Treshold",
        default=7,
        min=1,
        max=200,
        description="SmarthShootherHQ threshold param. default 7. range 1 to 200.")

    bpy.types.Scene.SmarthShootherHQAmount = bpy.props.IntProperty(
        name="SmarthShootherHQ Amount",
        default=254,
        min=1,
        max=254,
        description="SmarthShootherHQ amount param. default 254. range 1 to 254.")

    bpy.types.Scene.ResizeOnFinish = bpy.props.BoolProperty(
        name="Resize video to specified resolution?",
        default=False,
        description="Do you want to resize video on the end to specified resolution?.")

    bpy.types.Scene.FinalResolutionWidth = bpy.props.IntProperty(
        name="Resised frame width",
        default=1280,
        min=2,
        max=15000,
        description="Final frame width if you use Resize video button")

    bpy.types.Scene.FinalResolutionHeight = bpy.props.IntProperty(
        name="Resised frame height",
        default=720,
        min=2,
        max=15000,
        description="Final frame height if you use Resize video button")

    bpy.types.Scene.UseH264ForPNG = bpy.props.BoolProperty(
        name="Use H.264 when convert PNGs to avi",
        default=False,
        description="Do you want to convert your animation frames from PNG's or other types to H.264 output avi instead of AVIRAW ?.")

    bpy.types.Scene.USEFastEncodingH264ForPNG = bpy.props.BoolProperty(
        name="Use fast H.264 encoding but bigger file size?",
        default=True,
        description="Do you want to use fast H.264 encoding but bigger file size? this option is related to -Use H.264 when convert PNGs to avi- option")

    bpy.types.Scene.ExecuteProgram = bpy.props.EnumProperty(
        items=(('Generate only', 'Generate only', 'Only generate script'),
               ('AvsPmod', 'AvsPmod', 'AvsPmod is an avs scipt (avisynth) editor with video preview'),
               ('VirtualDub', 'VirtualDub', 'VirtualDub for generation final video from avs script'),
               ('Avs2avi', 'avs2avi', 'Convert avs script directly to avi'),
               ('ffmpeg', 'ffmpeg', 'Use ffmpeg to convert avs script to avi')),
        name="Run script with",
        default="Generate only",
        description="Which program do you want to use to run script.")

    bpy.utils.register_module(__name__)


def unregister():
    del bpy.types.Scene.SomeError
    del bpy.types.Scene.DirtStrenght
    del bpy.types.Scene.DenoisingFilterStrenght
    del bpy.types.Scene.DenoisingFramesComareCount
    del bpy.types.Scene.USMSharpness
    del bpy.types.Scene.FinalSharpen
    del bpy.types.Scene.FinalBlur
    del bpy.types.Scene.MaxMemoryForDenoising
    del bpy.types.Scene.UseDeflicker
    del bpy.types.Scene.UseSmarthSmootherHQ
    del bpy.types.Scene.SmarthShootherHQDiameter
    del bpy.types.Scene.SmarthShootherHQTreshold
    del bpy.types.Scene.SmarthShootherHQAmount
    del bpy.types.Scene.ResizeOnFinish
    del bpy.types.Scene.FinalResolutionWidth
    del bpy.types.Scene.FinalResolutionHeight
    del bpy.types.Scene.UseH264ForPNG
    del bpy.types.Scene.USEFastEncodingH264ForPNG

    del bpy.types.Scene.ExecuteProgram

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
