import os
import json
import subprocess

def ffprobe(fin, fout):

    ffp_in = subprocess.check_output(['ffprobe', '-v', 'warning',
                                      '-print_format', 'json',
                                      '-show_streams',
                                      '-show_format',
                                      fin])
    ffp_out = subprocess.check_output(['ffprobe', '-v', 'warning',
                                       '-print_format', 'json',
                                       '-show_streams',
                                       '-show_format',
                                       fout])
    ffp_in = json.loads(ffp_in)
    ffp_out = json.loads(ffp_out)

    duration_in = int(ffp_in['format']['duration'].split('.')[0])
    duration_out = int(ffp_out['format']['duration'].split('.')[0])

    if duration_in == duration_out:
        return True
    else:
        return False

def encode_c480(fin, fout):
	if os.path.exists(fout):
		os.remove(fout)

	output = ""

	cmd = ['ffmpeg',
		   '-i', fin,
		   '-r', '30',
		   '-s', 'hd480',
		   '-b:v', '1024k',
		   '-loglevel', 'quiet',
		   fout]

	try:
		subprocess.check_call(cmd)
	except OSError:
		output += "cmd ffmpeg not found. please install ffmpeg first."
		return False, output
	except subprocess.CalledProcessError as e:
		output += "error converting. msg: {}".format(e)
		return False, output

	succeed = ffprobe(fin, fout)
	if succeed:
		output += "finished(480p)"
		return True, output
	else:
		output += "failed(480p)"
		return False, output

def encode_c720(fin, fout):
	if os.path.exists(fout):
		os.remove(fout)

	output = ""

	cmd = ['ffmpeg',
		   '-i', fin,
		   '-r', '30',
		   '-s', 'hd720',
		   '-b:v', '2048k',
		   '-loglevel', 'quiet',
		   fout]

	try:
		subprocess.check_call(cmd)
	except OSError:
		output += "cmd ffmpeg not found. please install ffmpeg first."
		return False, output
	except subprocess.CalledProcessError as e:
		output += "error converting. msg: {}".format(e)
		return False, output

	succeed = ffprobe(fin, fout)
	if succeed:
		output += "finished(720p)"
		return True, output
	else:
		output += "failed(480p)"
		return False, output