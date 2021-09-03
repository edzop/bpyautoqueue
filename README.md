# bpyautoqueue

## Introduction 
bpyautoqueue is a set of tools for automation of blender baking, rendering and scene setup.

There are 4 parts to the bpyautoqueue set of tools:
* Render Queue
* Bake Queue
* Camera Helper UI
* Queue Helper UI

bpyautoqueue uses sqlite3 for storage. 


## Camera Helper UI
The Camera Helper UI is provided to provide a consistant repeatable way to streamline scene setup / camera placement / and automatic camera panning keyframes for animation sequences. 

![](images/camera_helper.png)


## Queue Helper UI
The Queue Helper UI is a provided to manipulate the render queue from the command blender user interface as an alternative to the `blq` and `blb` command line.

![](images/queue_helper.png)

## Render Queue
The render queue is managed with the `blb` command. 

The command `blq --help` will display a summary of options availible for the render queue:
```
====================================
--halfsize --fullsize --quartersize --2ksize - resize all renders to preset size
--clear  - clear DB
-s --searchpath  - add files to DB
-i - frame index
-m mode (anim/pananim/pankey)
-e engine: 'CYCLES' or 'LUXCORE'
--requeueall - requeue all jobs
--times - summary of render times
--requeuefailed - requeue failed jobs
--requeuefile FILENAME - requeue specific file (searches like wildcard)
--removefile FILENAME - remove specific file (searches like wildcard)
--markallfinished - mark all files as finished
-p --print  - print all files
--render render files in queue
--printqueued - print queued files
--printfailed - print failed files
-b --brief  - brief summary of DB

```


The command `blq --brief` will display a brief summary of the current render queue:

```
Opening database: /home/blender/bpyautoqueue/render_db.sqlite3
CYCLES: Queued 16545
CYCLES: Finished 7305
```

The command `blq -p` will print the contents of the current reneder queue:
```
68394 1920x1080 f:244 pan:0 movie:1 Queued		CYCLES	/home/user/new_blend/2021_06_spiral_01_water.blend samples: 0 time: 0.0
68395 1920x1080 f:245 pan:0 movie:1 Queued		CYCLES	/home/user/new_blend/2021_06_spiral_01_water.blend samples: 0 time: 0.0
Finished Count: 7313
Queued Count: 16537
Failed Count: 0
Total count: 23850
```

The command `blq --requeueall` will requeue all jobs for rendering. 

The command `blq --clear` will clear all jobs from the render queue

The command `blq --times` will display a summary of the total time for all frames rendered for each blender file in the render queue:

```
Opening database: /blender/bpyautoqueue/render_db.sqlite3
================== Times =================
Samples: 512 Resolution: (1920x1080) Time: 06:03:38 File: /home/blender/anim/water/2012_figure_splash.blend
Samples: 512 Resolution: (1920x1080) Time: 03:39:16 File: /home/blender/anim/water/2020_02_16_water.blend
Samples: 512 Resolution: (1920x1080) Time: 03:09:41 File: /home/blender/anim/water/2021_02_honey_grid_orbs.blend
Samples: 512 Resolution: (1920x1080) Time: 06:04:13 File: /home/blender/anim/water/2021_02_honey_twist_concave.blend
```
There are several options to assign output resolution to files in the render queue:
* --2ksize 2560x1440
* --fullsize 1920x1080
* --halfsize 960x540
* --quartersize 480x270

The command `blq --render` will render all files in the render queue and store results in the database. 




## Bake Queue
The bake queue is managed with the `blb` command. 

The typical work sequeunce is:

* Add files to bake queue with `blb --search` option
* Assign draft settings to each file with `blb --setupdraft`
* Bake fluid in blender files with `blb --bake`
* After results are satisfactory upscale to final settings with `blb --setupfinal`
* Bake fluids again with `blb --bake`

The draft and final settings have different resolution, timesteps, and subframe assignments.

The command `blb --help` will display a list of options:
```
====================================
-p --print		| print all files
-b --brief		| brief summary of DB
--bake		| bake remaining files in queue
--setupdraft		| setup draft settings
--setupfinal		| setup final settings
--clean		| clean particles
--clearresults		| delete all bake results
--results -r		Print bake results
-s --searchpath		| add files to DB
--clearjobs			| clear DB
--markallfinished	| mark all files as finished
--requeueall		| requeue all jobs
--requeuefailed		| requeue failed jobs
```

The command `blb -r` will display bake results:

```
================== Results =================
2021-08-27 14:55 baketime: 03:35:08, frames: 250, resolution: 120, domain: (0.7,0.7,0.4), cache: 63G, filename: 2012_figure_splash.blend 
2021-08-27 17:42 baketime: 02:46:56, frames: 400, resolution: 120, domain: (6.0,2.1,0.1), cache: 112G, filename: 2021_02_honey_twist_concave.blend 
2021-08-27 19:45 baketime: 02:03:34, frames: 400, resolution: 120, domain: (7.0,4.0,4.0), cache: 298M, filename: 2021_02_honey_twist_concave_roller.blend 
2021-08-27 19:46 baketime: 08:23:32, frames: 400, resolution: 120, domain: (8.0,6.0,6.0), cache: 5.6G, filename: 2021_02_honey_grid_orbs.blend 
2021-08-27 19:46 baketime: 08:25:40, frames: 300, resolution: 120, domain: (6.0,6.0,6.0), cache: 35G, filename: 2020_02_16_water.blend 
```

The command `blb --bake` will bake all fluid files in the queue. Sometimes a fluid bake operation will not use all threads because of collision physics so multiple instances of the bake command can be run in different consoles.

The command `blb --search test/` will search the `test` directory for any matching blend files and add them to the bake queue.

The command `blb -p` will print the current bake queue:
```
Opening database: /blender/bpyautoqueue/bake_db.sqlite3
================== BakeDB =================
#1 status: Queued file: test/test2.blend
#2 status: Queued file: test/test1.blend
Finished Count: 0
Queued Count: 2
Processing Count: 0
Total count: 2
```

The command `blb --setupdraft` will iterate through all files currently in the queue and assign draft fluid settings. The fluid settings are defined in the file `bake_fluids.py` and currently set to subdivision 32 for draft settings. This is useful to configure a series of blend files for preview fluid behavior before baking at higher resolution. 

The command `blb --setupfinal` will iterate through all files currently in the queue and assign draft fluid settings. The fluid settings are defined in the file `bake_fluids.py` and currently set to subdivision 90 for final settings. 

The command `blb --clear` will clear all records from the bake queue. 

## Installation
An automated install package is not availible at this time. If you copy this repository into your:
`blender_installation_directory/addons/scripts/bpyautoqueue` directory you should see bpyautoqueue in the list of blender addons next time you start blender. 

Running the command `setup_environment.sh` will add symbolic links for the commands `blq` and `blb` into `/usr/bin` so you can manipulate the render queue and the bake queue.