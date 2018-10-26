### How do I get set up? ###

* Restrictions

Current version restrictions:

1. animation frame has to have width and height divided by 2 - for example 2, 4, 6, 8 and so on (another example of valid resolution will be 1280x720, but neither 1279x720 nor 1280x719)

2. the plugin may not work correctly on Linux or other systems than windows (I have only tried it on windows)

3. The rendering output has to be one of the following:
* "AVI_RAW" (this is preferred option),
* "FFmpeg video" - AVI container with codec H.264 and lossless quality (I haven't tried to use other quality options),
*  PNG (require an FFMPEG installed, but all frames will be connected to AVI file and then it will be processed as input for denoising,

* Configuration
- install blender addon

- install Avisynth

https://sourceforge.net/projects/avisynth2/?source=navbar

add paths to system environment path:

for example

C:\AviSynth

and

C:\AviSynth\plugins

- install Avisynth plugins and copy to Avisynth\plugins dir    

https://dl.dropboxusercontent.com/u/26042452/avi/plugins.zip    

- install VirtualDub (used by script to convert video if you want to)

https://sourceforge.net/projects/virtualdub/    

add path to system environment path:

for example
C:\VirtualDub-1.10.4

- install Microsoft Visual C++ 2010 SP1 Redistributable Package (x86). Needed for some plugins    

https://www.microsoft.com/en-us/download/details.aspx?id=8328

ADDITIONAL SOFTWARE HELPFULL BUT NOT REALLY NEEDED (addon will work without it, but it won't be fully functional)

- install avsPmod (used by script to display video preview end edit script)    

https://github.com/AvsPmod/AvsPmod/releases    

for example
C:\AvsPmod_v2.5.1\AvsPmod\
C:\AvsPmod_v2.5.1\AvsPmod\tools

- install FFmpeg (used by the script to automatically convert input video to output - if you want to)    

https://ffmpeg.zeranoe.com/builds/

for example
C:\ffmpeg-3.2.2-win32\bin

- install k-lite codecs pack (helpfull codecs needed for many things )    

https://www.codecguide.com/download_kl.htm    

If you won't download avsPmod you can't generate movies by it, same as FFmpeg. 
But you can use VirtualDub which was recommended for downloading. 
K-lite codecs pack will be useful if I extend plugin functionality to use another kind of input than AVI_RAW

PLUGINS USED BY SCRIPT (you don't have to download it. This is only for information purposes)

MvTools plugins for AviSynth

http://avisynth.nl/index.php/MVTools

SmartSmootherHQ plugin for AviSynth    

http://rationalqm.us/hiq/smoothhiq.html

The script is inspired by film restoration script by videoFreed so it uses this:

https://forum.doom9.org/showthread.php?t=144271

if you still can't run denoising script then you could additionally download

Hybrid:

http://www.selur.de/downloads

and you don't have to install this but just open this exe as a zip archive and copy AviSynth plugins from it to Avisynth\plugins folder

* How to use

How to use it in the blender:

First of all, you have to generate AVI_RAW animation (no PNG etc for now) - this is current restriction

then you can change some denoising setting and click generate a script

The script will be generated with a name as the avi animation file and extension .avs

there is a combo box "Run script with" with option how the script will be run. 

So you can generate the script and:
- open it with VirtualDub (to make/preview a final movie),
- open it with avsPmod and edit/preview changes,
- generate final raw avi movie from input by using FFmpeg,
- generate final raw avi movie from input by using avs2avi

Finally. There are two methods (known by me) for a good denoising,

first one: render 8 samples (or more if you want to) with compositor filtering node setup
(I have given a blender setup scene in dropbox folder - download if you want), and then use denoising script

this method is a base but there will be more blurry result than if you use the second method.

the second one method of denoising: download Lucas denoising build. 
Render 8 sample (or more) animation with his denoising method and then denoise with script (addon)

To get the best denoising result in animation you could use modified blender version with LWR denoiser
from lukasstockner97 as a base for denoising script

https://blenderartists.org/forum/showthread.php?395313-Experimental-2-77-Cycles-Denoising-build