import os
import subprocess

def genpat(tmp_path):
	vidfn = tmp_path + '/test.mp4'

	if os.path.exists(vidfn):
		os.remove(vidfn)

	subprocess.check_call(['ffmpeg', '-v', 'warning',
						   '-f', 'lavfi',
						   '-i', 'smptebars',
						   '-t', '5',
						   vidfn])

	return vidfn