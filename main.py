import os
import json
import time
import npyscreen
import subprocess
from multiprocessing import Process, Queue, Manager

PROCESS_NUM = 10

def testFunc(task_q, messages, id):
	while True:
		messages[id] = 'waiting task'
		task = task_q.get()
		messages[id] = task
		time.sleep(30)

def encode(task_q, messages, id):
	while True:
		messages[id] = 'waiting task'
		filename = task_q.get()
		parsed = filename.split('.')
		fout_480p = "".join(parsed[:-1]) + "_480p." + parsed[-1]
		fout_720p = "".join(parsed[:-1]) + "_720p." + parsed[-1]
		messages[id] = 'recv file to encode {}'.format(filename)
		encode_c480(filename, fout_480p, messages, id)
		time.sleep(1)
		encode_c720(filename, fout_720p, messages, id)

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


def encode_c480(fin, fout, messages, id):
	messages[id] = "converting {} (output 480p)...".format(fin)
	if os.path.exists(fout):
		os.remove(fout)

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
		messages[id] = "cmd ffmpeg not found. please install ffmpeg first."
		return False
	except subprocess.CalledProcessError as e:
		messages[id] = "error converting. msg: {}".format(e)
		return False

	succeed = ffprobe(fin, fout)
	if succeed:
		messages[id] = "finished(480p)"
		return True
	else:
		messages[id] = "failed(480p)"
		return False

def encode_c720(fin, fout, messages, id):
	messages[id] = "converting {} (output 720p)...".format(fin)
	if os.path.exists(fout):
		os.remove(fout)
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
		messages[id] = "cmd ffmpeg not found. please install ffmpeg first."
		return False
	except subprocess.CalledProcessError as e:
		messages[id] = "error converting. msg: {}".format(e)
		return False

	succeed = ffprobe(fin, fout)
	if succeed:
		messages[id] = "finished(720p)"
		return True
	else:
		messages[id] = "failed(480p)"
		return False

class VideoEncoderApp(npyscreen.NPSAppManaged):
	def onStart(self):
		self.keypress_timeout_default = 1
		self.manager = Manager()
		self.messages = self.manager.dict()
		self.task_q = Queue()
		self.msg_q = Queue()
		self.pool = []
		self.addForm("MAIN", MainForm, name="Video Encoder")
		

		for i in range(PROCESS_NUM):
			p = Process(target=encode, args=(self.task_q, self.messages, i))
			p.start()
			self.pool.append(p)

	def onCleanExit(self):
		npyscreen.notify_wait("Goodbye!")

		# terminate all the processes
		for process in self.pool:
			process.terminate()
			time.sleep(0.1)

class MainForm(npyscreen.ActionForm):
	def create(self):
		self.keypress_timeout_default = 1
		self.process_fields = []
		self.fn = self.add(npyscreen.TitleFilenameCombo, name="filename: ")
		self.status = self.add(npyscreen.MultiLineEdit, value="Welcome! Please choose mp4 or mov file to encode\n", max_height=10, rely=9)
		self.stdout = None
		for i in range(PROCESS_NUM):
			process_name = "process {}:".format(i)
			self.process_fields.append(self.add(npyscreen.TitleText, name=process_name, value="initializing", editable=False))

	def while_waiting(self):
		for i in range(PROCESS_NUM):
			if i in self.parentApp.messages:
				self.process_fields[i].value = self.parentApp.messages[i]
				self.process_fields[i].display()
			if self.stdout is not None:
				self.status.value += self.stdout
				self.stdout = None
				self.status.display()

	def on_cancel(self):
		self.parentApp.setNextForm(None)

	def on_ok(self):
		filename = self.fn.value
		parsed = filename.split('.')
		if len(parsed) > 1:
			suffix = parsed[-1]
			if suffix == 'mp4'or suffix == 'mov':
				self.parentApp.task_q.put(filename)
				self.stdout = "add file({}) to task queue(current size:{})\n".format(filename, self.parentApp.task_q.qsize())
			else:
				self.stdout = "invalid filename({}). mp4 or mov file required.\n".format(filename)
		else:
			self.stdout = "invalid filename({}). mp4 or mov file required.\n".format(filename)


if __name__ == "__main__":
	app = VideoEncoderApp()
	app.run()