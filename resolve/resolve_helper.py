
import DaVinciResolveScript  as dvr


class resolve_helper:

    resolve=None
    fusion=None
    activeproject=None

    def __init__(self):

        self.resolve = dvr.scriptapp("Resolve")

        if not self.resolve:
            print("Please launch DaVinci Resolve first.")
            sys.exit()

        
        self.fusion = dvr.scriptapp('Fusion')

        self.projectmanager = self.resolve.GetProjectManager()

        if self.projectmanager is None:
            print("Project Manager not found...")
            sys.exit()

        self.activeproject = self.projectmanager.GetCurrentProject()

        if self.activeproject is None:
            print("No Current project")
        else:
            print("Using Project: %s"%self.activeproject.GetName())

        #self.timeline = self.projectmanager.GetCurrentTimeline()


    def getTimeline(self):
        timeline=self.activeproject.GetCurrentTimeline()

        if not timeline:
	        mediapool = self.activeproject.GetMediaPool()
	        timeline = mediapool.CreateEmptyTimeline("Timeline1")
        
        return timeline

    def print_folder_media(self,folder):

        print("Folder: %s"%folder.GetName())

        clips = folder.GetClipList()

        for clip in clips:
            file_name=clip.GetClipProperty('File Name')
            clip_type=clip.GetClipProperty('Type')
            resolution=clip.GetClipProperty('Resolution')
            print("%10s:\t%10s\t%s"%(clip_type,resolution,file_name))

        for subfolder in folder.GetSubFolderList():

            self.print_folder_media(subfolder)

    def list_media_in_pool(self,project):

        mediaPool = self.activeproject.GetMediaPool()
        rootFolder = mediaPool.GetRootFolder()
        
        self.print_folder_media(rootFolder)


