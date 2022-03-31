import os       
import subprocess

def encode_mpg(source_path,blend_file_path,renderer_directory):
    # ffmpeg -f image2 -r 1/5 -i image%05d.png -vcodec mpeg4 -y movie.mp4
    #input_files="'%s/%*.png'" %(path,source_path) 
    output_movie_file="./%s-%s.mp4" %(blend_file_path,renderer_directory)
    print("encoding %s to %s" %(source_path,output_movie_file))
    ffmpeg_command = [ 'ffmpeg' ]
    ffmpeg_command.append('-y')
    
    ffmpeg_command.append('-pattern_type')
    ffmpeg_command.append('glob')
    
    ffmpeg_command.append('-i')
    ffmpeg_command.append("%s/*.png" %(source_path))

    ffmpeg_command.append("-codec")
    ffmpeg_command.append("libx264")

    ffmpeg_command.append("-crf")
    ffmpeg_command.append("19")

    ffmpeg_command.append("-pix_fmt")
    ffmpeg_command.append("yuv420p")
    
    ffmpeg_command.append(output_movie_file)

    subprocess.call(ffmpeg_command)

def getSubDirectories(path):
    sublist = os.listdir(path)
    return sublist

def iterate_renderers(blend_file_path):
    sublist = getSubDirectories(blend_file_path)
    for renderer_directory in sublist:
        print(renderer_directory)
        if os.path.isdir("%s/%s" %(blend_file_path,renderer_directory)):
            source_path="./%s/%s" %(blend_file_path,renderer_directory)
            print("Processing directory: %s" %(source_path))
            encode_mpg(source_path,blend_file_path,renderer_directory)



def encode_subdirectories(path):
    blend_file_list = getSubDirectories(path)

    for blend_file in blend_file_list:
        if os.path.isdir(blend_file):
            print("Processing: %s" %blend_file)
            iterate_renderers(blend_file)
